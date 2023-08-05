#
# Catalogs.py -- Catalogs plugin for Ginga fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from ginga.gtkw import ColorBar
from ginga.gtkw import GtkHelp
from ginga.misc import Bunch, Future
from ginga.misc.plugins import CatalogsBase

import gobject
import gtk

class Catalogs(CatalogsBase.CatalogsBase):

    def __init__(self, fv, fitsimage):
        super(Catalogs, self).__init__(fv, fitsimage)

        self.tooltips = self.fv.w.tooltips

    def build_gui(self, container, future=None):
        vbox1 = gtk.VBox()

        self.msgFont = self.fv.getFont('sansFont', 12)
        tw = gtk.TextView()
        tw.set_wrap_mode(gtk.WRAP_WORD)
        tw.set_left_margin(4)
        tw.set_right_margin(4)
        tw.set_editable(False)
        tw.set_left_margin(4)
        tw.set_right_margin(4)
        tw.modify_font(self.msgFont)
        self.tw = tw

        fr = gtk.Frame(" Instructions ")
        fr.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        fr.set_label_align(0.1, 0.5)
        fr.add(tw)
        vbox1.pack_start(fr, padding=4, fill=True, expand=False)
        
        nb = gtk.Notebook()
        #nb.set_group_id(group)
        #nb.connect("create-window", self.detach_page, group)
        nb.set_tab_pos(gtk.POS_BOTTOM)
        nb.set_scrollable(True)
        nb.set_show_tabs(True)
        nb.set_show_border(False)
        vbox1.pack_start(nb, padding=4, fill=True, expand=True)

        vbox0 = gtk.VBox()
        hbox = gtk.HBox(spacing=4)

        vbox = gtk.VBox()
        fr = gtk.Frame(" Image Server ")
        fr.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        fr.set_label_align(0.5, 0.5)
        fr.add(vbox)

        captions = (('Server', 'xlabel'),
                    ('@Server', 'combobox'),
                    ('Use DSS channel', 'checkbutton'),
                    ('Get Image', 'button'))
        w, self.w = GtkHelp.build_info(captions)
        self.w.nb = nb
        self.w.get_image.connect('clicked', lambda w: self.getimage_cb())
        self.w.use_dss_channel.set_active(self.use_dss_channel)
        self.w.use_dss_channel.connect('toggled', self.use_dss_channel_cb)

        vbox.pack_start(w, padding=4, fill=True, expand=False)

        self.w.img_params = gtk.VBox()
        vbox.pack_start(self.w.img_params, padding=4, fill=True, expand=False)
        
        combobox = self.w.server
        index = 0
        self.image_server_options = self.fv.imgsrv.getServerNames(kind='image')
        for name in self.image_server_options:
            combobox.insert_text(index, name)
            index += 1
        index = 0
        combobox.set_active(index)
        combobox.sconnect('changed', self.setup_params_image)
        if len(self.image_server_options) > 0:
            self.setup_params_image(combobox, redo=False)

        hbox.pack_start(fr, fill=True, expand=True)

        vbox = gtk.VBox()
        fr = gtk.Frame(" Catalog Server ")
        fr.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        fr.set_label_align(0.5, 0.5)
        fr.add(vbox)

        captions = (('Server', 'xlabel'),
                    ('@Server', 'combobox'),
                    ('Limit stars to area', 'checkbutton'),
                    ('Search', 'button'))
        w, self.w2 = GtkHelp.build_info(captions)
        self.w2.search.connect('clicked', lambda w: self.getcatalog_cb())
        self.w2.limit_stars_to_area.set_active(self.limit_stars_to_area)
        self.w2.limit_stars_to_area.connect('toggled', self.limit_area_cb)

        vbox.pack_start(w, padding=4, fill=True, expand=False)

        self.w2.cat_params = gtk.VBox()
        vbox.pack_start(self.w2.cat_params, padding=4, fill=True, expand=False)
        
        combobox = self.w2.server
        index = 0
        self.catalog_server_options = self.fv.imgsrv.getServerNames(kind='catalog')
        for name in self.catalog_server_options:
            combobox.insert_text(index, name)
            index += 1
        index = 0
        combobox.set_active(index)
        combobox.sconnect('changed', self.setup_params_catalog)
        if len(self.catalog_server_options) > 0:
            self.setup_params_catalog(combobox, redo=False)

        hbox.pack_start(fr, fill=True, expand=True)
        vbox0.pack_start(hbox, fill=True, expand=True)

        btns = gtk.HButtonBox()
        btns.set_layout(gtk.BUTTONBOX_CENTER)
        btns.set_spacing(5)

        btn = gtk.Button("Set parameters from entire image")
        btn.connect('clicked', lambda w: self.setfromimage())
        btns.add(btn)
        vbox0.pack_start(btns, padding=4, fill=True, expand=False)

        lbl = gtk.Label("Params")
        self.w.params = vbox0
        nb.append_page(vbox0, lbl)

        vbox = gtk.VBox()
        self.table = CatalogListing(self.logger, vbox)

        hbox = gtk.HBox()
        scale = gtk.HScrollbar()
        adj = scale.get_adjustment()
        adj.configure(0, 0, 0, 1, 10, self.plot_limit)
        #scale.set_size_request(200, -1)
        self.tooltips.set_tip(scale, "Choose subset of stars plotted")
        #scale.set_update_policy(gtk.UPDATE_DELAYED)
        scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        self.w.plotgrp = scale
        scale.connect('value-changed', self.plot_pct_cb)
        hbox.pack_start(scale, padding=2, fill=True, expand=True)

        sb = GtkHelp.SpinButton()
        adj = sb.get_adjustment()
        adj.configure(self.plot_limit, 10, self.plot_max, 10, 100, 100)
        self.w.plotnum = sb
        self.tooltips.set_tip(sb, "Adjust size of subset of stars plotted")
        sb.connect('value-changed', self.plot_limit_cb)
        hbox.pack_start(sb, padding=2, fill=False, expand=False)
        vbox.pack_start(hbox, padding=0, fill=False, expand=False)

        #vbox1.pack_start(vbox, padding=4, fill=True, expand=True)
        lbl = gtk.Label("Listing")
        self.w.listing = vbox
        nb.append_page(vbox, lbl)

        btns = gtk.HButtonBox()
        btns.set_layout(gtk.BUTTONBOX_START)
        btns.set_spacing(3)
        btns.set_child_size(15, -1)
        self.w.buttons = btns

        btn = gtk.Button("Close")
        btn.connect('clicked', lambda w: self.close())
        btns.add(btn)

        if future:
            btn = gtk.Button('Ok')
            btn.connect('clicked', lambda w: self.ok())
            btns.add(btn)
            btn = gtk.Button('Cancel')
            btn.connect('clicked', lambda w: self.cancel())
            btns.add(btn)
        vbox1.pack_start(btns, padding=4, fill=True, expand=False)

        vbox1.show_all()
        container.pack_start(vbox1, padding=0, fill=True, expand=True)
        

    def limit_area_cb(self, w):
        self.limit_stars_to_area = w.get_active()
        return True

    def use_dss_channel_cb(self, w):
        self.use_dss_channel = w.get_active()
        return True

    def plot_pct_cb(self, rng):
        val = rng.get_value()
        self.plot_start = int(val)
        self.replot_stars()
        return True

    def _update_plotscroll(self):
        num_stars = len(self.starlist)
        if num_stars > 0:
            adj = self.w.plotgrp.get_adjustment()
            page_size = self.plot_limit
            self.plot_start = min(self.plot_start, num_stars-1)
            adj.configure(self.plot_start, 0, num_stars, 1,
                          page_size, page_size)

        self.replot_stars()

    def plot_limit_cb(self, rng):
        val = rng.get_value()
        self.plot_limit = int(val)
        self._update_plotscroll()
        return True

    def set_message(self, msg):
        buf = self.tw.get_buffer()
        buf.set_text(msg)
        self.tw.modify_font(self.msgFont)
        
    def _raise_tab(self, w):
        num = self.w.nb.page_num(w)
        self.w.nb.set_current_page(num)
        
    def _get_cbidx(self, w):
        return w.get_active()
        
    def _setup_params(self, obj, container):
        params = obj.getParams()
        captions = []
        for key, bnch in params.items():
            text = key
            if bnch.has_key('label'):
                text = bnch.label
            captions.append((text, 'entry'))

        # TODO: put RA/DEC first, and other stuff not in random orders
        w, b = GtkHelp.build_info(captions)

        # remove old widgets
        children = container.get_children()
        for child in children:
            container.remove(child)

        # add new widgets
        container.pack_start(w, fill=False, expand=False)
        container.show_all()
        return b

    def setup_params_image(self, combobox, redo=True):
        index = combobox.get_active()
        key = self.image_server_options[index]

        # Get the parameter list and adjust the widget
        obj = self.fv.imgsrv.getImageServer(key)
        b = self._setup_params(obj, self.w.img_params)
        self.image_server_params = b

        if redo:
            self.redo()

    def setup_params_catalog(self, combobox, redo=True):
        index = combobox.get_active()
        key = self.catalog_server_options[index]

        # Get the parameter list and adjust the widget
        obj = self.fv.imgsrv.getCatalogServer(key)
        b = self._setup_params(obj, self.w2.cat_params)
        self.catalog_server_params = b

        if redo:
            self.redo()
            
    def instructions(self):
        self.set_message("""TBD.""")

    def _update_widgets(self, d):
        for bnch in (self.image_server_params,
                     self.catalog_server_params):
            if bnch != None:
                for key in bnch.keys():
                    if d.has_key(key):
                        bnch[key].set_text(str(d[key]))

    def get_params(self, bnch):
        params = {}
        for key in bnch.keys():
            params[key] = bnch[key].get_text()
        return params
        
    def __str__(self):
        return 'catalogs'
    

class CatalogListing(CatalogsBase.CatalogListingBase):
    
    def _build_gui(self, container):
        self.mframe = container

        self.cell_sort_funcs = []
        for kwd, key in self.columns:
            self.cell_sort_funcs.append(self._mksrtfnN(key))

        vbox = gtk.VBox()

        sw = gtk.ScrolledWindow()
        sw.set_border_width(2)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # create the TreeView
        treeview = gtk.TreeView()
        self.treeview = treeview
        
        # create the TreeViewColumns to display the data
        tvcolumn = [None] * len(self.columns)
        for n in range(0, len(self.columns)):
            cell = gtk.CellRendererText()
            cell.set_padding(2, 0)
            header, kwd = self.columns[n]
            tvc = gtk.TreeViewColumn(header, cell)
            tvc.set_spacing(4)
            tvc.set_resizable(True)
            tvc.connect('clicked', self.sort_cb, n)
            tvc.set_clickable(True)
            tvcolumn[n] = tvc
            fn_data = self._mkcolfnN(kwd)
            tvcolumn[n].set_cell_data_func(cell, fn_data)
            treeview.append_column(tvcolumn[n])

        sw.add(treeview)
        self.treeview.connect('cursor-changed', self.select_star_cb)
        sw.show_all()
        vbox.pack_start(sw, fill=True, expand=True)

        self.cbar = ColorBar.ColorBar(self.logger)
        self.cbar.set_cmap(self.cmap)
        self.cbar.set_imap(self.imap)
        self.cbar.set_size_request(-1, 20)

        vbox.pack_start(self.cbar, padding=4, fill=True, expand=False)

        btns = gtk.HButtonBox()
        btns.set_layout(gtk.BUTTONBOX_CENTER)
        btns.set_spacing(5)

        for name in ('Plot', 'Clear', #'Close'
                     ):
            btn = gtk.Button(name)
            btns.add(btn)
            self.btn[name.lower()] = btn

        self.btn.plot.connect('clicked', lambda w: self.replot_stars())
        self.btn.clear.connect('clicked', lambda w: self.clear())
        #self.btn.close.connect('clicked', lambda w: self.close())

        vbox.pack_start(btns, padding=4, fill=True, expand=False)
        vbox.show_all()
        
        self.mframe.pack_start(vbox, expand=True, fill=True)
        self.mframe.show_all()

    def _mkcolfnN(self, kwd):
        def fn(column, cell, model, iter):
            bnch = model.get_value(iter, 0)
            cell.set_property('text', bnch[kwd])
        return fn

    def sort_cb(self, column, idx):
        treeview = column.get_tree_view()
        model = treeview.get_model()
        model.set_sort_column_id(idx, gtk.SORT_ASCENDING)
        fn = self.cell_sort_funcs[idx]
        model.set_sort_func(idx, fn)
        return True

    def _mksrtfnN(self, key):
        def fn(model, iter1, iter2):
            bnch1 = model.get_value(iter1, 0)
            bnch2 = model.get_value(iter2, 0)
            val1, val2 = bnch1[key], bnch2[key]
            if isinstance(val1, str):
                val1 = val1.lower()
                val2 = val2.lower()
            res = cmp(val1, val2)
            return res
        return fn

    def show_table(self, catalog, info, starlist):
        self.starlist = starlist
        self.catalog = catalog
        # info is ignored, for now
        #self.info = info
        self.selected = []

        # Update the starlist info
        listmodel = gtk.ListStore(object)
        for star in starlist:
            # TODO: find mag range
            listmodel.append([star])

        self.treeview.set_model(listmodel)

        self.cbar.set_range(self.mag_min, self.mag_max)


    def _select_tv(self, star, fromtable=False):
        treeselection = self.treeview.get_selection()
        star_idx = self.starlist.index(star)
        treeselection.select_path(star_idx)
        if not fromtable:
            # If the user did not select the star from the table, scroll
            # the table so they can see the selection
            self.treeview.scroll_to_cell(star_idx, use_align=True, row_align=0.5)

    def _unselect_tv(self, star):
        treeselection = self.treeview.get_selection()
        star_idx = self.starlist.index(star)
        treeselection.unselect_path(star_idx)

    def select_star_cb(self, treeview):
        """This method is called when the user selects a star from the table.
        """
        path, column = treeview.get_cursor()
        model = treeview.get_model()
        iter = model.get_iter(path)
        star = model.get_value(iter, 0)
        self.logger.debug("selected star: %s" % (str(star)))
        self.mark_selection(star, fromtable=True)
        return True
    

# END
