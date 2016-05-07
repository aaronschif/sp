import sys
from pkgutil import get_data
from PyQt5.Qt import (QMainWindow, QApplication, QTextEdit, QToolBar, QAction, QIcon, QPixmap,
    QSettings, QStatusBar, QTextCharFormat, QTextBlockFormat, pyqtSignal, QObject, QFileDialog,
    QDockWidget, QSpinBox, Qt, QWidget)
from PyQt5.Qt import *
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


class QuiDock(QDockWidget):
    def __init__(self, controller):
        super().__init__()
        self.setObjectName('SettingsDock')

        box = QVBoxLayout()
        box.setAlignment(Qt.AlignTop)
        group = QGroupBox("Speech to text engine")
        stte = QVBoxLayout()
        group.setLayout(stte)
        google = QCheckBox('Google')
        google.setDisabled(True)
        stte.addWidget(google)
        stte.addWidget(QCheckBox('Sphinx'))

        box.addWidget(group)
        widget = QWidget()
        widget.setLayout(box)
        self.setWidget(widget)


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


class QuiFormat(QTextCharFormat):
    def __init__(self, size, weight=QFont.Normal):
        super().__init__()
        self.setFontWeight(weight)
        self.setFontPointSize(size)

class QuiTextEditor(QTextEdit):
    new_speech_signal = pyqtSignal(str)

    format_h1 = QuiFormat(30)
    format_h2 = QuiFormat(25)
    format_h3 = QuiFormat(20)
    format_h4 = QuiFormat(15)
    format_h5 = QuiFormat(10)
    format_h6 = QuiFormat(5)

    format_p = QuiFormat(10)

    def __init__(self, controller):
        super().__init__()
        formc = QTextCharFormat()
        formc.setFontItalic(True)
        formc.setFontWeight(3)
        form = QTextBlockFormat()
        form.setLineHeight(200, 1)

        cur = self.textCursor()
        cur.insertText('A', self.format_h1)
        cur.insertText('B', self.format_h2)
        cur.insertText('C', self.format_h3)
        cur.insertText('D', self.format_h4)
        cur.insertText('E', self.format_h5)
        cur.insertText('F', self.format_h6)

        # print(dir(new_speech_signal))
        # new_speech_signal = QObject()
        # Speech(self.new_speech_signal.emit).start()
        self.new_speech_signal.connect(cur.insertText)

    def setCurrentFont(self, font):
        pass

    def foo(self):

        cur = self.textCursor()
        last_text = cur.block().text()
        last_pos = cur.position()
        cur.movePosition(cur.EndOfBlock)
        chars = cur.positionInBlock()
        for i in range(chars):
            cur.deletePreviousChar()
        cur.insertText(last_text, self.format_h1)
        cur.setPosition(last_pos)
        self.setTextCursor(cur)


class QuiMain(QMainWindow):

    def __init__(self, controller):
        super().__init__()

        self.setWindowTitle("QuickText")
        self.setGeometry(100,100,1030,800)
        pixmap = QPixmap()
        pixmap.loadFromData(get_data(__name__, 'icon.png'))
        self.setWindowIcon(QIcon(pixmap))
        self.setStatusBar(QuiStatusBar())
        self.addDockWidget(Qt.RightDockWidgetArea, QuiDock(controller))

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
