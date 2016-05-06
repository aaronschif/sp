import sys
from pkgutil import get_data
from PyQt5.Qt import (QMainWindow, QApplication, QTextEdit, QToolBar, QAction, QIcon, QPixmap,
    QSettings, QStatusBar, QTextCharFormat, QTextBlockFormat, pyqtSignal, QObject, QFileDialog)
import speech_recognition
from contextlib import ExitStack, suppress


class Speech(object):
    def __init__(self, callback):
        self.mic = speech_recognition.Microphone()
        self.rec = speech_recognition.Recognizer()
        self.callback = callback

    def start(self):
        with self.mic:
            self.rec.adjust_for_ambient_noise(self.mic)
        self.rec.listen_in_background(self.mic, self._callback)

    def _callback(self, rec, audio):
        with suppress(speech_recognition.UnknownValueError):
            self.callback(rec.recognize_sphinx(audio))
            # self.callback(rec.recognize_google(audio))


class QuiController(object):
    def __init__(self):
        pass

    def window_init(self):
        self.document_editor = QuiTextEditor(self)
        self.document = self.document_editor.document()

        self.settings = QSettings("MyCompany", "MyApp")

        self.main_window = QuiMain(self)
        self._end_called = False

    def start(self):
        app = QApplication(sys.argv)
        app.setApplicationName('QuickText')

        self.window_init()

        if self.settings.value("myWidget/geometry") and self.settings.value("myWidget/windowState"):
            self.main_window.restoreGeometry(self.settings.value("myWidget/geometry"))
            self.main_window.restoreState(self.settings.value("myWidget/windowState"))
        self.main_window.show()

        try:
            ret = app.exec_()
        finally:
            self.end(ret)

    def end(self, ret=0):
        if self._end_called:
            return
        self._end_called = True

        self.settings.setValue("myWidget/geometry", self.main_window.saveGeometry())
        self.settings.setValue("myWidget/windowState", self.main_window.saveState())

        sys.exit(ret)


class QuiStatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        self.setSizeGripEnabled(True)


class QuiAction(QAction):
    def __init__(self, window, data):
        super().__init__(window)
        icon, name, tooltip, shortcut, action = data

        if icon:
            self.setIcon(icon)
        self.setText(name)
        if tooltip:
            self.setToolTip(tooltip)
        if shortcut:
            self.setShortcut(shortcut)
        self.triggered.connect(action)


class QuiToolbar(QToolBar):
    def __init__(self, window, name, controls):
        super().__init__(window)

        self.setObjectName(name)

        for control in controls:
            self.addAction(QuiAction(window, control))


class QuiTextEditor(QTextEdit):
    new_speech_signal = pyqtSignal(str)

    def __init__(self, controller):
        super().__init__()
        formc = QTextCharFormat()
        formc.setFontItalic(True)
        formc.setFontWeight(3)
        form = QTextBlockFormat()
        form.setLineHeight(200, 1)

        cur = self.textCursor()
        cur.insertText('Foo')
        cur.movePosition(1, 1, 8)

        # print(dir(new_speech_signal))
        # new_speech_signal = QObject()
        Speech(self.new_speech_signal.emit).start()
        self.new_speech_signal.connect(cur.insertText)

    def foo(self):
        cur = self.textCursor()
        cur.insertText('Foo')
        chars = cur.positionInBlock()
        for i in range(chars):
            cur.deletePreviousChar()
        print(cur.block().text())
        cur.movePosition(1, 1, 8)


class QuiMain(QMainWindow):

    def __init__(self, controller):
        super().__init__()

        self.setWindowTitle("QuickText")
        self.setGeometry(100,100,1030,800)
        pixmap = QPixmap()
        pixmap.loadFromData(get_data(__name__, 'icon.png'))
        self.setWindowIcon(QIcon(pixmap))
        self.setStatusBar(QuiStatusBar())

        self.setCentralWidget(controller.document_editor)
        self.addToolBar(QuiToolbar(self, 'FileToolbar', [
            (None, "Open", "Open a file", None, lambda: QFileDialog.getOpenFileName()),
            (None, "Save", "Save the current file", None, lambda: QFileDialog.getSaveFileName()),
            (None, "Exit", "Exit", None, controller.end),
        ]))

        self.addToolBar(QuiToolbar(self, 'FormatToolbar', [
            (None, "Heading 1", "Heading level one", None, lambda: controller.document_editor.foo()),
            (None, "Heading 2", "Heading level two", None, lambda: print('foo')),
            (None, "Heading 3", "Heading level three", None, lambda: print('foo')),
            (None, "Heading 4", "Heading level four", None, lambda: print('foo')),
            (None, "Heading 5", "Heading level five", None, lambda: print('foo')),
            (None, "Heading 6", "Heading level six", None, lambda: print('foo')),
            (None, "Body", "Simple body text", None, lambda: print('foo')),
        ]))


if __name__ == "__main__":
    QuiController().start()
