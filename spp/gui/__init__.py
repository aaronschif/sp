from PyQt5.Qt import (QWidget, QApplication, QTreeView, QTreeWidgetItem, QHBoxLayout,
    QVBoxLayout, QStandardItemModel, QStandardItem, QSplitter, QTextEdit, QMainWindow, QAction,
    QIcon, QFileDialog, QTextListFormat, QTextDocument, QPrinter, QPrintDialog, QDialog)



def _doc_iter(doc):
    assert isinstance(doc, QTextDocument)
    x = doc.begin()
    while x != doc.end():
        yield x
        x = x.next()


class SideWindow(QTreeView):
    def __init__(self):
        super().__init__()

        model = QStandardItemModel()

        for x in range(10):
            item = QStandardItem('Foo' + str(x))
            item.setChild(0, QStandardItem('Zoo'))
            model.insertRow(0, item)

        # model.setItem(2, 2, QStandardItem('Bar'))
        self.setModel(model)
        self.setHeaderHidden(True)
        # self.setExpanded(True)


class EditWindow(QTextEdit):
    def __init__(self):
        super().__init__()


def init_file_toolbar(window):
    # QIcon.fromTheme('exit'),
    exitAction = QAction('Exit', window)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.triggered.connect(window.controller.handle_close)

    printAction = QAction('Print', window)
    printAction.setShortcut('Ctrl+P')
    printAction.triggered.connect(window.sig_print)

    exportAction = QAction('Export', window)
    exportAction.triggered.connect(window.sig_export)

    importAction = QAction('Import', window)
    importAction.triggered.connect(window.sig_import)

    undoAction = QAction('Undo', window)

    window.toolbar = window.addToolBar('Exit')
    window.toolbar.addAction(exitAction)
    window.toolbar.addAction(printAction)
    window.toolbar.addAction(exportAction)
    window.toolbar.addAction(importAction)
    window.toolbar.addAction(undoAction)


def init_edit_toolbar(window):
    h1Action = QAction('Title 1', window)
    h1Action.triggered.connect(window.sig_h1)

    window.edit_toolbar = window.addToolBar('Edit')
    window.edit_toolbar.addAction(h1Action)


def init_menu(window):
    exitAction = QAction('&Exit', window)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(window.close)

    menu = window.menuBar()
    menuitem = menu.addMenu('&File')
    menuitem.addAction(exitAction)


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle(controller.title())

        self.win_editor = EditWindow()

        splitter = QSplitter()
        splitter.addWidget(SideWindow())
        splitter.addWidget(self.win_editor)
        self.setGeometry(100, 100, 500, 355)

        self.setCentralWidget(splitter)
        self.statusBar().setSizeGripEnabled(True)

        init_file_toolbar(self)
        init_edit_toolbar(self)
        init_menu(self)

    def keyPressEvent(self, event):
        print('foo')

    def sig_h1(self):
        cursor = self.win_editor.textCursor()
        cursor.insertText('foo', headingFormat)

    def sig_print(self):
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec() != QDialog.Accepted:
            return

        doc = self.win_editor.document()
        doc.print_(printer)

    def sig_export(self):
        path = QFileDialog.getSaveFileName(caption="Save", filter="Markdown (*.md);;Text (*.txt);;HTML (*.html *.htm);;All (*)")
        print(path)

    def sig_import(self):
        path = QFileDialog.getOpenFileName()
        self.controller.handle_load(path)
        self.win_editor.setDocument(self.win_editor.document())
