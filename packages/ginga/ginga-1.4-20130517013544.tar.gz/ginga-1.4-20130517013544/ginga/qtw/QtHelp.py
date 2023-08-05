#
# QtHelp.py -- customized Qt widgets and convenience functions
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import time
import os

# PySide or PyQt4: choose one or the other, but not both
toolkit = 'choose'
#toolkit = 'pyside'
#toolkit = 'pyqt4'

has_pyqt4 = False
has_pyside = False

if toolkit in ('pyqt4', 'choose'):
    try:
        import sip
        for cl in ('QString', ):
            sip.setapi(cl, 2)

        from PyQt4 import QtCore, QtGui
        has_pyqt4 = True
        try:
            from PyQt4 import QtWebKit
        except ImportError:
            pass

        # for Matplotlib
        os.environ['QT_API'] = 'pyqt'
    except ImportError:
        pass

if toolkit in ('pyside', 'choose') and (not has_pyqt4):
    try:
        from PySide import QtCore, QtGui
        has_pyside = True
        try:
            from PySide import QtWebKit
        except ImportError:
            pass

        # for Matplotlib
        os.environ['QT_API'] = 'pyside'
    except ImportError:
        pass
    
if (not has_pyside) and (not has_pyqt4):
    raise ImportError("Please install pyqt4 or pyside")

from ginga.misc import Bunch, Callback

tabwidget_style = """
QTabWidget::pane { margin: 0px,0px,0px,0px; padding: 0px; }
QMdiSubWindow { margin: 0px; padding: 2px; }
"""

class TopLevel(QtGui.QWidget):

    def closeEvent(self, event):
        if hasattr(self, 'app') and self.app:
            self.app.quit()

    def setApp(self, app):
        self.app = app
    
class TabWidget(QtGui.QTabWidget):
    pass

class StackedWidget(QtGui.QStackedWidget):

    def addTab(self, widget, label):
        self.addWidget(widget)

    def removeTab(self, index):
        self.removeWidget(self.widget(index))

class Workspace(QtGui.QMdiArea):

    def __init__(self):
        super(Workspace, self).__init__()
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setViewMode(QtGui.QMdiArea.TabbedView)
        
    def addTab(self, widget, label):
        ## subw = QtGui.QMdiSubWindow()
        ## subw.setWidget(widget)
        ## subw.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        ## self.addSubWindow(subw)
        w = self.addSubWindow(widget)
        #w.setContentsMargins(0, 0, 0, 0)
        w.setWindowTitle(label)
        w.show()

    def indexOf(self, widget):
        try:
            wl = list(self.subWindowList())
            #l = [ sw.widget() for sw in wl ]
            return wl.index(widget)
        except (IndexError, ValueError), e:
            return -1

    def widget(self, index):
        l = list(self.subWindowList())
        sw = l[index]
        #return sw.widget()
        return sw.widget()

    def tabBar(self):
        return None
    
    def setCurrentIndex(self, index):
        l = list(self.subWindowList())
        w = l[index]
        self.setActiveSubWindow(w)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

class ComboBox(QtGui.QComboBox):

    def insert_alpha(self, text):
        index = 0
        while True:
            itemText = self.itemText(index)
            if len(itemText) == 0:
                break
            if itemText > text:
                self.insertItem(index, text)
                return
            index += 1
        self.addItem(text)
        
    def delete_alpha(self, text):
        index = self.findText(text)
        self.removeItem(index)

    def show_text(self, text):
        index = self.findText(text)
        self.setCurrentIndex(index)

    def append_text(self, text):
        self.addItem(text)

class VBox(QtGui.QWidget):
    def __init__(self, *args, **kwdargs):
        super(VBox, self).__init__(*args, **kwdargs)

        layout = QtGui.QVBoxLayout()
        # because of ridiculous defaults
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
    
    def addWidget(self, w, **kwdargs):
        self.layout().addWidget(w, **kwdargs)

    def setSpacing(self, val):
        self.layout().setSpacing(val)
        
class HBox(QtGui.QWidget):
    def __init__(self, *args, **kwdargs):
        super(HBox, self).__init__(*args, **kwdargs)

        layout = QtGui.QHBoxLayout()
        # because of ridiculous defaults
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def addWidget(self, w, **kwdargs):
        self.layout().addWidget(w, **kwdargs)
    
    def setSpacing(self, val):
        self.layout().setSpacing(val)
        
class Frame(QtGui.QFrame):
    def __init__(self, title=None):
        super(Frame, self).__init__()

        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
        vbox = QtGui.QVBoxLayout()
        # because of ridiculous defaults
        vbox.setContentsMargins(2, 2, 2, 2)
        self.setLayout(vbox)
        if title:
            lbl = QtGui.QLabel(title)
            lbl.setAlignment(QtCore.Qt.AlignHCenter)
            vbox.addWidget(lbl, stretch=0)
            self.label = lbl
        else:
            self.label = None

    def getLabel(self):
        return self.label
    
    def addWidget(self, w, **kwdargs):
        self.layout().addWidget(w, **kwdargs)
    
class Dialog(QtGui.QDialog):
    def __init__(self, title=None, flags=None, buttons=None,
                 callback=None):
        QtGui.QDialog.__init__(self)
        self.setModal(False)

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.content = QtGui.QWidget()
        vbox.addWidget(self.content, stretch=1)
        
        hbox_w = QtGui.QWidget()
        hbox = QtGui.QHBoxLayout()
        hbox_w.setLayout(hbox)

        def mklocal(val):
            def cb():
                callback(self, val)
            return cb
            
        for name, val in buttons:
            btn = QtGui.QPushButton(name)
            if callback:
                btn.clicked.connect(mklocal(val))
            hbox.addWidget(btn, stretch=0)

        vbox.addWidget(hbox_w, stretch=0)
        #self.w.connect("close", self.close)

    def get_content_area(self):
        return self.content


class Desktop(Callback.Callbacks):

    def __init__(self):
        super(Desktop, self).__init__()
        
        # for tabs
        self.tab = Bunch.caselessDict()
        self.tabcount = 0
        self.notebooks = Bunch.caselessDict()
        
        for name in ('page-switch', 'page-select'):
            self.enable_callback(name)
        self.popmenu = None
        
    # --- Tab Handling ---
    
    def make_ws(self, name=None, group=1, show_tabs=True, show_border=False,
                detachable=True, tabpos=None, scrollable=True, closeable=False,
                wstype='nb'):
        if tabpos == None:
            tabpos = QtGui.QTabWidget.North

        if wstype == 'mdi':
            nb = Workspace()

        elif show_tabs:
            nb = TabWidget()
            nb.setTabPosition(tabpos)
            nb.setUsesScrollButtons(scrollable)
            nb.setTabsClosable(closeable)
            nb.setMovable(True)   # reorderable
            nb.setAcceptDrops(True)
            nb.currentChanged.connect(lambda idx: self.switch_page(idx, nb))

            tb = nb.tabBar()
            ## tb.setAcceptDrops(True)
            tb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            tb.connect(tb, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'),
                       lambda point: self.on_context_menu(nb, point))


        else:
            nb = StackedWidget()
            nb.currentChanged.connect(lambda idx: self.switch_page(idx, nb))

        nb.setStyleSheet (tabwidget_style)
        if not name:
            name = str(time.time())
        self.notebooks[name] = Bunch.Bunch(nb=nb, name=name, nbtype=wstype)
        return self.notebooks[name]

    def get_nb(self, name):
        return self.notebooks[name].nb
        
    def on_context_menu(self, nb, point):
        # create context menu
        popmenu = QtGui.QMenu(nb)
        submenu = QtGui.QMenu(popmenu)
        submenu.setTitle("Take Tab")
        popmenu.addMenu(submenu)

        tabnames = list(self.tab.keys())
        tabnames.sort()
        for tabname in tabnames:
            item = QtGui.QAction(tabname, nb)
            item.triggered.connect(self._mk_take_tab_cb(tabname, nb))
            submenu.addAction(item)

        popmenu.exec_(nb.mapToGlobal(point))
        self.popmenu = popmenu

    def add_tab(self, tab_w, widget, group, labelname, tabname=None,
                data=None):
        """NOTE: use add_page() instead."""
        self.tabcount += 1
        if not tabname:
            tabname = labelname
            if self.tab.has_key(tabname):
                tabname = 'tab%d' % self.tabcount
            
        tab_w.addTab(widget, labelname)
        self.tab[tabname] = Bunch.Bunch(widget=widget, name=labelname,
                                        tabname=tabname, data=data,
                                        group=group)
        return tabname

    def add_page(self, nbname, widget, group, labelname, tabname=None):
        tab_w = self.get_nb(nbname)
        return self.add_tab(tab_w, widget, group, labelname, tabname=tabname)

    def _find_nb(self, tabname):
        widget = self.tab[tabname].widget
        for bnch in self.notebooks.values():
            nb = bnch.nb
            page_num = nb.indexOf(widget)
            if page_num < 0:
                continue
            return (nb, page_num)
        return (None, None)

    def _find_tab(self, widget):
        for key, bnch in self.tab.items():
            if widget == bnch.widget:
                return bnch
        return None

    def select_cb(self, widget, event, name, data):
        self.make_callback('page-select', name, data)
        
    def raise_tab(self, tabname):
        nb, index = self._find_nb(tabname)
        widget = self.tab[tabname].widget
        if (nb != None) and (index >= 0):
            nb.setCurrentIndex(index)

    def highlight_tab(self, tabname, onoff):
        nb, index = self._find_nb(tabname)
        if nb:
            tb = nb.tabBar()
            if tb == None:
                return
            widget = tb.tabButton(index, QtGui.QTabBar.RightSide)
            if widget == None:
                return
            name = self.tab[tabname].name
            if onoff:
                widget.setStyleSheet('QPushButton {color: palegreen}')
            else:
                widget.setStyleSheet('QPushButton {color: grey}')

    def remove_tab(self, tabname):
        nb, index = self._find_nb(tabname)
        widget = self.tab[tabname].widget
        if (nb != None) and (index >= 0):
            nb.removeTab(index)

    def create_toplevel_ws(self, width, height, x=None, y=None):
        # create main frame
        root = TopLevel()
        ## root.setTitle(title)
        # TODO: this needs to be more sophisticated

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        root.setLayout(layout)

        menubar = QtGui.QMenuBar()
        layout.addWidget(menubar, stretch=0)

        # create a Window pulldown menu, and add it to the menu bar
        winmenu = menubar.addMenu("Window")

        ## item = QtGui.QAction("Take Tab", menubar)
        ## item.triggered.connect(self.gui_load_file)
        ## winmenu.addAction(item)

        sep = QtGui.QAction(menubar)
        sep.setSeparator(True)
        winmenu.addAction(sep)
        
        quititem = QtGui.QAction("Quit", menubar)
        winmenu.addAction(quititem)

        bnch = self.make_ws(group=1)
        bnch.root = root
        layout.addWidget(bnch.nb, stretch=1)
        root.closeEvent = lambda event: self.close_page(bnch, event)
        quititem.triggered.connect(lambda: self._close_page(bnch))

        root.show()
        root.resize(width, height)
        if x != None:
            root.moveTo(x, y)
        return True

    def detach_page(self, source, widget, x, y, group):
        # Detach page to new top-level workspace
        ## page = self.widgetToPage(widget)
        ## if not page:
        ##     return None
        width, height = widget.size()
        
        ## self.logger.info("detaching page %s" % (page.name))
        bnch = self.create_toplevel_ws(width, height, x=x, y=y)

        return bnch.nb

    def _mk_take_tab_cb(self, tabname, to_nb):
        def _foo():
            nb, index = self._find_nb(tabname)
            widget = self.tab[tabname].widget
            if (nb != None) and (index >= 0):
                nb.removeTab(index)
                to_nb.addTab(widget, tabname)
            
        return _foo
        
    def _close_page(self, bnch):
        num_children = bnch.nb.count()
        if num_children == 0:
            del self.notebooks[bnch.name]
            root = bnch.root
            bnch.root = None
            root.destroy()
        return True
    
    def close_page(self, bnch, event):
        num_children = bnch.nb.count()
        if num_children == 0:
            del self.notebooks[bnch.name]
            #bnch.root.destroy()
            event.accept()
        else:
            event.ignore()
        return True
    
    def switch_page(self, page_num, nbw):
        pagew = nbw.currentWidget()
        bnch = self._find_tab(pagew)
        if bnch != None:
            self.make_callback('page-switch', bnch.name, bnch.data)
        return False

    def make_desktop(self, layout, widgetDict=None):
        if widgetDict == None:
            widgetDict = {}

        def process_common_params(widget, inparams):
            params = Bunch.Bunch(name=None, height=-1, width=-1)
            params.update(inparams)
            
            if params.name:
                widgetDict[params.name] = widget

            if ((params.width >= 0) or (params.height >= 0)) and \
                   isinstance(widget, QtGui.QWidget):
                if params.width < 0:
                    width = widget.width()
                else:
                    width = params.width
                if params.height < 0:
                    height = widget.height()
                else:
                    height = params.height
                widget.resize(width, height)
            
        def make_widget(kind, paramdict, args, pack):
            #print "ARGS ARE ", args
            kind = kind.lower()
            
            # Process workspace parameters
            params = Bunch.Bunch(name=None, title=None, height=-1,
                                 width=-1, group=1, show_tabs=True,
                                 show_border=False, scrollable=True,
                                 detachable=True, wstype='nb',
                                 tabpos=QtGui.QTabWidget.North)
            params.update(paramdict)
            #print "PARAMS ARE", params

            if kind == 'widget':
                widget = args[0]

            elif kind == 'ws':
                group = int(params.group)
                widget = self.make_ws(name=params.name, group=group,
                                      show_tabs=params.show_tabs,
                                      show_border=params.show_border,
                                      detachable=params.detachable,
                                      tabpos=params.tabpos,
                                      wstype=params.wstype,
                                      scrollable=params.scrollable).nb
                #debug(widget)

            # If a title was passed as a parameter, then make a frame to
            # wrap the widget using the title.
            if params.title:
                fr = Frame(params.title)
                fr.layout().addWidget(widget, stretch=1)
                pack(fr)
            else:
                pack(widget)

            process_common_params(widget, params)
            
            if (kind in ('ws', 'mdi')) and (len(args) > 0):
                # <-- Notebook ws specified a sub-layout.  We expect a list
                # of tabname, layout pairs--iterate over these and add them
                # to the workspace as tabs.
                print "ws args=", args
                for tabname, layout in args[0]:
                    def pack(w):
                        # ?why should group be the same as parent group?
                        self.add_tab(widget, w, group,
                                     tabname, tabname.lower())

                    make(layout, pack)
                
            return widget

        # Horizontal adjustable panel
        def horz(params, cols, pack):
            if len(cols) >= 2:
                hpaned = QtGui.QSplitter()
                hpaned.setOrientation(QtCore.Qt.Horizontal)

                for col in cols:
                    make(col, lambda w: hpaned.addWidget(w))
                widget = hpaned

            elif len(cols) == 1:
                widget = QtGui.QWidget()
                layout = QtGui.QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                make(cols[0], lambda w: layout.addWidget(w, stretch=1))
                widget.setLayout(layout)
                #widget.show()

            process_common_params(widget, params)
            pack(widget)
            

        # Vertical adjustable panel
        def vert(params, rows, pack):
            if len(rows) >= 2:
                vpaned = QtGui.QSplitter()
                vpaned.setOrientation(QtCore.Qt.Vertical)

                for row in rows:
                    make(row, lambda w: vpaned.addWidget(w))
                widget = vpaned

            elif len(rows) == 1:
                widget = QtGui.QWidget()
                layout = QtGui.QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                make(rows[0], lambda w: layout.addWidget(w, stretch=1))
                widget.setLayout(layout)
                #widget.show()

            process_common_params(widget, params)
            pack(widget)

        # Horizontal fixed array
        def hbox(params, cols, pack):
            widget = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)

            for dct in cols:
                if isinstance(dct, dict):
                    stretch = dct.get('stretch', 0)
                    col = dct.get('col', None)
                else:
                    # assume a list defining the col
                    stretch = align = 0
                    col = dct
                if col != None:
                    make(col, lambda w: layout.addWidget(w,
                                                         stretch=stretch))
            process_common_params(widget, params)
            
            #widget.show()
            pack(widget)

        # Vertical fixed array
        def vbox(params, rows, pack):
            widget = QtGui.QWidget()
            layout = QtGui.QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)

            for dct in rows:
                if isinstance(dct, dict):
                    stretch = dct.get('stretch', 0)
                    row = dct.get('row', None)
                else:
                    # assume a list defining the row
                    stretch = align = 0
                    row = dct
                if row != None:
                    make(row, lambda w: layout.addWidget(w,
                                                         stretch=stretch))
            process_common_params(widget, params)

            #widget.show()
            pack(widget)

        def make(constituents, pack):
            kind = constituents[0]
            params = constituents[1]
            if len(constituents) > 2:
                rest = constituents[2:]
            else:
                rest = []
                
            if kind == 'vpanel':
                vert(params, rest, pack)
            elif kind == 'hpanel':
                horz(params, rest, pack)
            elif kind == 'vbox':
                vbox(params, rest, pack)
            elif kind == 'hbox':
                hbox(params, rest, pack)
            elif kind in ('ws', 'mdi', 'widget'):
                make_widget(kind, params, rest, pack)

        widget33 = QtGui.QWidget()
        layout33 = QtGui.QVBoxLayout()
        layout33.setContentsMargins(0, 0, 0, 0)
        widget33.setLayout(layout33)
        make(layout, lambda w: layout33.addWidget(w, stretch=1))
        #widget33.show()
        return widget33

def _name_mangle(name, pfx=''):
    newname = []
    for c in name.lower():
        if not (c.isalpha() or c.isdigit() or (c == '_')):
            newname.append('_')
        else:
            newname.append(c)
    return pfx + ''.join(newname)

def _make_widget(tup, ns):
    swap = False
    title = tup[0]
    if not title.startswith('@'):
        name  = _name_mangle(title)
        w1 = QtGui.QLabel(title + ':')
        w1.setAlignment(QtCore.Qt.AlignRight)
    else:
        # invisible title
        swap = True
        name  = _name_mangle(title[1:])
        w1 = QtGui.QLabel('')

    wtype = tup[1]
    if wtype == 'label':
        w2 = QtGui.QLabel('')
        w2.setAlignment(QtCore.Qt.AlignLeft)
    elif wtype == 'xlabel':
        w2 = QtGui.QLabel('')
        w2.setAlignment(QtCore.Qt.AlignLeft)
        name = 'xlbl_' + name
    elif wtype == 'entry':
        w2 = QtGui.QLineEdit()
        w2.setMaxLength(12)
    elif wtype == 'combobox':
        w2 = ComboBox()
    elif wtype == 'spinbutton':
        w2 = QtGui.QSpinBox()
    elif wtype == 'spinfloat':
        w2 = QtGui.QDoubleSpinBox()
    elif wtype == 'vbox':
        w2 = VBox()
    elif wtype == 'hbox':
        w2 = HBox()
    elif wtype == 'hscale':
        w2 = QtGui.QSlider(QtCore.Qt.Horizontal)
    elif wtype == 'vscale':
        w2 = QtGui.QSlider(QtCore.Qt.Vertical)
    elif wtype == 'checkbutton':
        w1 = QtGui.QLabel('')
        w2 = QtGui.QCheckBox(title)
        swap = True
    elif wtype == 'radiobutton':
        w1 = QtGui.QLabel('')
        w2 = QtGui.QRadioButton(title)
        swap = True
    elif wtype == 'togglebutton':
        w1 = QtGui.QLabel('')
        w2 = QtGui.QPushButton(title)
        w2.setCheckable(True)
        swap = True
    elif wtype == 'button':
        w1 = QtGui.QLabel('')
        w2 = QtGui.QPushButton(title)
        swap = True
    elif wtype == 'spacer':
        w1 = QtGui.QLabel('')
        w2 = QtGui.QLabel('')
    else:
        raise Exception("Bad wtype=%s" % wtype)

    lblname = 'lbl_%s' % (name)
    if swap:
        w1, w2 = w2, w1
        ns[name] = w1
        ns[lblname] = w2
    else:
        ns[name] = w2
        ns[lblname] = w1
    return (w1, w2)

def build_info(captions):
    numrows = len(captions)
    numcols = reduce(lambda acc, tup: max(acc, len(tup)), captions, 0)

    widget = QtGui.QWidget()
    table = QtGui.QGridLayout()
    widget.setLayout(table)
    table.setVerticalSpacing(2)
    table.setHorizontalSpacing(4)
    table.setContentsMargins(2, 2, 2, 2)

    wb = Bunch.Bunch()
    row = 0
    for tup in captions:
        col = 0
        while col < numcols:
            if col < len(tup):
                tup1 = tup[col:col+2]
                w1, w2 = _make_widget(tup1, wb)
                table.addWidget(w1, row, col)
                table.addWidget(w2, row, col+1)
            col += 2
        row += 1

    return widget, wb

def debug(widget):
    foo = dir(widget)
    print "---- %s ----" % str(widget)
    for x in foo:
        if x.startswith('set'):
            print x

def children(layout):   
    i = 0
    res = []
    child = layout.itemAt(i)
    while child != None:
        res.append(child)
        i += 1
        child = layout.itemAt(i)
    return res

def removeWidget(layout, widget):
    print "removing %s from list" % widget
    kids = children(layout)
    kids2 = map(lambda item: item.widget(), kids)
    print "children are", kids2
    if widget in kids2:
        idx = kids2.index(widget)
        w = kids[idx]
        #layout.removeWidget(widget)
        print "removing item"
        layout.removeItem(w)
        widget.setParent(None)
        #print "deleting widget"
        #widget.delete()
    else:
        print "widget is not present"
        

#END
