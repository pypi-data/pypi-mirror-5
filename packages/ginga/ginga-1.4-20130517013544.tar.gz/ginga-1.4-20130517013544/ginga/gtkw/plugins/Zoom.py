#
# Zoom.py -- Zoom plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org) 
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import gtk
import gobject
from ginga.gtkw import GtkHelp

from ginga.misc import Bunch

from ginga.gtkw import FitsImageCanvasGtk
from ginga.gtkw import FitsImageCanvasTypesGtk as CanvasTypes
from ginga import GingaPlugin


class Zoom(GingaPlugin.GlobalPlugin):

    def __init__(self, fv):
        # superclass defines some variables for us, like logger
        super(Zoom, self).__init__(fv)

        self.zoomimage = None
        self.default_radius = 30
        self.default_zoom = 3
        self.zoom_radius = self.default_radius
        self.zoom_amount = self.default_zoom
        self.zoom_x = 0
        self.zoom_y = 0
        self.t_abszoom = True
        self.zoomtask = None
        self.fitsimage_focus = None
        self.lagtime = 2

        fv.add_callback('add-channel', self.add_channel)
        fv.add_callback('active-image', self.focus_cb)

    def build_gui(self, container):

        vpaned = gtk.VPaned()
    
        width, height = 200, 200

        # Uncomment to debug; passing parent logger generates too
        # much noise in the main logger
        #zi = FitsImageCanvasGtk.FitsImageCanvas(logger=self.logger)
        zi = FitsImageCanvasGtk.FitsImageCanvas(logger=None)
        zi.enable_autozoom('off')
        zi.enable_autocuts('off')
        #zi.set_scale_limits(0.001, 1000.0)
        zi.zoom_to(self.default_zoom, redraw=False)
        zi.add_callback('zoom-set', self.zoomset)
        zi.set_bg(0.4, 0.4, 0.4)
        zi.show_pan_mark(True, redraw=False)
        self.zoomimage = zi

        bd = zi.get_bindings()
        bd.enable_zoom(False)
        bd.enable_pan(False)
        bd.enable_cmap(False)

        iw = zi.get_widget()
        iw.set_size_request(width, height)
        vpaned.pack1(iw, resize=True, shrink=True)

        vbox = gtk.VBox()
        vbox.pack_start(gtk.Label("Zoom Radius:"), padding=2,
                        fill=True, expand=False)

        adj = gtk.Adjustment(lower=1, upper=100)
        adj.set_value(self.zoom_radius)
        scale = GtkHelp.HScale(adj)
        scale.set_size_request(200, -1)
        scale.set_digits(0)
        scale.set_draw_value(True)
        scale.set_value_pos(gtk.POS_BOTTOM)
        #scale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        self.w_radius = scale
        scale.connect('value-changed', self.set_radius_cb)
        vbox.pack_start(scale, padding=0, fill=True, expand=False)

        vbox.pack_start(gtk.Label("Zoom Amount:"), padding=2,
                        fill=True, expand=False)

        adj = gtk.Adjustment(lower=-20, upper=30)
        adj.set_value(self.zoom_amount)
        scale = GtkHelp.HScale(adj)
        scale.set_size_request(200, -1)
        scale.set_digits(0)
        scale.set_draw_value(True)
        scale.set_value_pos(gtk.POS_BOTTOM)
        #scale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        self.w_amount = scale
        scale.connect('value-changed', self.set_amount_cb)
        vbox.pack_start(scale, padding=0, fill=True, expand=False)

        captions = (('Zoom', 'label'),
                    ("Relative Zoom", 'checkbutton'),
                    ("Lag Time", 'spinbutton'),
                    ('Defaults', 'button'),
                    )

        w, b = GtkHelp.build_info(captions)
        b.zoom.set_text(self.fv.scale2text(zi.get_scale()))
        self.wzoom = b
        b.relative_zoom.set_active(not self.t_abszoom)
        b.relative_zoom.sconnect("toggled", self.set_absrel_cb)
        b.defaults.connect("clicked", lambda w: self.set_defaults())
        adj = b.lag_time.get_adjustment()
        adj.configure(0, 0, 20, 1, 1, 1)
        adj.set_value(self.lagtime)
        b.lag_time.set_digits(0)
        b.lag_time.set_wrap(True)
        b.lag_time.connect('value-changed', self.setlag_cb)
        vbox.pack_start(w, padding=4, fill=True, expand=False)

        sw = gtk.ScrolledWindow()
        sw.set_border_width(2)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(vbox)

        vpaned.pack2(sw, resize=True, shrink=True)
        vpaned.show_all()
        vpaned.set_position(height)
        
        container.pack_start(vpaned, padding=0, fill=True, expand=True)

    def prepare(self, fitsimage):
        fitsimage.add_callback('image-set', self.new_image_cb)
        #fitsimage.add_callback('focus', self.focus_cb)
        # TODO: should we add our own canvas instead?
        fitsimage.add_callback('motion', self.motion_cb)
        fitsimage.add_callback('cut-set', self.cutset_cb)
        fitsimage.add_callback('transform', self.transform_cb)
        fitsimage.add_callback('rotate', self.rotate_cb)
        fitsimage.add_callback('zoom-set', self.zoomset_cb)

    def add_channel(self, viewer, chinfo):
        self.prepare(chinfo.fitsimage)

    def start(self):
        names = self.fv.get_channelNames()
        for name in names:
            chinfo = self.fv.get_channelInfo(name)
            self.add_channel(self.fv, chinfo)
        
    # CALLBACKS

    def new_image_cb(self, fitsimage, image):
        if fitsimage != self.fv.getfocus_fitsimage():
            return True

        self.fitsimage_focus = fitsimage
        # Reflect transforms, colormap, etc.
        fitsimage.copy_attributes(self.zoomimage,
                                  ['transforms', 'cutlevels',
                                   'rgbmap'],
                                  redraw=False)
                                  
        ## data = image.get_data()
        ## self.set_data(data)

    def focus_cb(self, viewer, fitsimage):
        self.fitsimage_focus = fitsimage
        # Reflect transforms, colormap, etc.
        fitsimage.copy_attributes(self.zoomimage,
                                  ['transforms', 'cutlevels',
                                   'rgbmap', 'rotation'],
                                  redraw=False)

        # TODO: redo cutout?
        
    # Match cut-levels to the ones in the "main" image
    def cutset_cb(self, fitsimage, loval, hival):
        if fitsimage != self.fitsimage_focus:
            return True
        self.zoomimage.cut_levels(loval, hival)
        return True

    def transform_cb(self, fitsimage):
        if fitsimage != self.fitsimage_focus:
            return True
        flip_x, flip_y, swap_xy = fitsimage.get_transforms()
        self.zoomimage.transform(flip_x, flip_y, swap_xy)
        return True
        
    def rotate_cb(self, fitsimage, deg):
        if fitsimage != self.fitsimage_focus:
            return True
        self.zoomimage.rotate(deg)
        return True
        
    def _zoomset(self, fitsimage, zoomlevel):
        if fitsimage != self.fitsimage_focus:
            return True
        if self.t_abszoom:
            # Did user set to absolute zoom?
            myzoomlevel = self.zoom_amount
            
        else:
            # Amount of zoom is a relative amount
            myzoomlevel = self.zoomimage.get_zoom()
            myzoomlevel = zoomlevel + self.zoom_amount

        self.logger.debug("zoomlevel=%d myzoom=%d" % (
            zoomlevel, myzoomlevel))
        self.zoomimage.zoom_to(myzoomlevel, redraw=True)
        text = self.fv.scale2text(self.zoomimage.get_scale())
        return True
        
    def zoomset_cb(self, fitsimage, zoomlevel, scale_x, scale_y):
        """This method is called when a main FITS widget changes zoom level.
        """
        fac_x, fac_y = fitsimage.get_scale_base_xy()
        fac_x_me, fac_y_me = self.zoomimage.get_scale_base_xy()
        if (fac_x != fac_x_me) or (fac_y != fac_y_me):
            alg = fitsimage.get_zoom_algorithm()
            self.zoomimage.set_zoom_algorithm(alg)
            self.zoomimage.set_scale_base_xy(fac_x, fac_y)
        return self._zoomset(self.fitsimage_focus, zoomlevel)
        
    def set_amount_cb(self, rng):
        """This method is called when 'Zoom Amount' control is adjusted.
        """
        val = rng.get_value()
        self.zoom_amount = val
        zoomlevel = self.fitsimage_focus.get_zoom()
        self._zoomset(self.fitsimage_focus, zoomlevel)
        
    def set_absrel_cb(self, w):
        self.t_abszoom = not w.get_active()
        zoomlevel = self.fitsimage_focus.get_zoom()
        return self._zoomset(self.fitsimage_focus, zoomlevel)
        
    def set_defaults(self):
        self.t_abszoom = True
        self.wzoom.relative_zoom.set_active(not self.t_abszoom)
        self.w_radius.set_value(self.default_radius)
        self.w_amount.set_value(self.default_zoom)
        self.zoomimage.zoom_to(self.default_zoom, redraw=False)
        
    # LOGIC
    
    def zoomset(self, fitsimage, zoomlevel, scalefactor):
        text = self.fv.scale2text(self.zoomimage.get_scale())
        self.wzoom.zoom.set_text(text)
        
    def set_radius_cb(self, rng):
        val = rng.get_value()
        self.set_radius(val)
        
    def setlag_cb(self, w):
        val = w.get_value()
        self.logger.debug("Setting lag time to %d" % (val))
        self.lagtime = val
        
    def set_radius(self, val):
        self.logger.debug("Setting radius to %d" % val)

        self.zoom_radius = val
        fitsimage = self.fitsimage_focus
        if fitsimage == None:
            return True
        image = fitsimage.get_image()
        wd, ht = image.get_size()
        data_x, data_y = wd // 2, ht // 2
        self.showxy(fitsimage, data_x, data_y)
        
    def showxy(self, fitsimage, data_x, data_y):
        # Cut and show zoom image in zoom window
        self.zoom_x, self.zoom_y = data_x, data_y

        image = fitsimage.get_image()
        if image == None:
            # No image loaded into this channel
            return True

        # If this is a new source, then update our widget with the
        # attributes of the source
        if self.fitsimage_focus != fitsimage:
            self.focus_cb(self.fv, fitsimage)
            
        # Cut out and show the zoom detail
        if self.zoomtask:
            gobject.source_remove(self.zoomtask)
        self.zoomtask = gobject.timeout_add(self.lagtime, self.showzoom,
                                            image, data_x, data_y)
        # x1, y1, x2, y2 = self.cutdetail_radius(image, self.zoomimage,
        #                                        data_x, data_y,
        #                                        self.zoom_radius)
        return True

    def motion_cb(self, fitsimage, button, data_x, data_y):
        # TODO: pass _canvas_ and cut from that
        self.showxy(fitsimage, data_x, data_y)
        return False

    def showzoom(self, image, data_x, data_y):
        # cut out and set the zoom image
        x1, y1, x2, y2 = self.cutdetail_radius(image, self.zoomimage,
                                               data_x, data_y,
                                               self.zoom_radius, redraw=True)
        self.zoomtask = None

    def cutdetail_radius(self, image, dstimage, data_x, data_y,
                         radius, redraw=True):
        data, x1, y1, x2, y2 = image.cutout_radius(int(data_x), int(data_y),
                                                   radius)

        dstimage.set_data(data, redraw=redraw)

        return (x1, y1, x2, y2)


    def __str__(self):
        return 'zoom'
    
#END
