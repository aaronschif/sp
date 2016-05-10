import sys
from pkgutil import get_data
from PyQt5.Qt import (QMainWindow, QApplication, QTextEdit, QToolBar, QAction, QIcon, QPixmap,
    QSettings, QStatusBar, QTextCharFormat, QTextBlockFormat, pyqtSignal, QObject, QFileDialog,
    QDockWidget, QSpinBox, Qt, QWidget)
from PyQt5.Qt import *
import speech_recognition
from contextlib import ExitStack, suppress
from markdown import Markdown
from markdown import util
from markdown.serializers import to_html_string
ElementTree = util.etree.ElementTree


class Speech(object):
    def __init__(self):
        self.mic = speech_recognition.Microphone()
        self.rec = speech_recognition.Recognizer()
        self.callback = None
        self._stopper = None

    def connect(self, controller):
        self.callback = controller

    def start(self):
        with self.mic:
            self.rec.adjust_for_ambient_noise(self.mic)
        self._stopper = self.rec.listen_in_background(self.mic, self._callback)

    def end(self):
        self._stopper()

    def toggle(self, name):
        pass

    def selectMic(self, name):
        self.end()
        with suppress(OSError):
            mic = speech_recognition.Microphone(name)
            with mic:
                pass
            self.mic = mic
        self.start()

    def _callback(self, rec, audio):
        with suppress(speech_recognition.UnknownValueError):
            try:
                # self.callback(rec.recognize_sphinx(audio))
                self.callback(rec.recognize_google(audio))
            except speech_recognition.RequestError:
                pass


class QuiDock(QDockWidget):
    def __init__(self, controller):
        super().__init__()

        self.setObjectName('SettingsDock')

        box = QVBoxLayout()
        box.setAlignment(Qt.AlignTop)

        # group = QGroupBox("Speech to text engine")
        # stte = QVBoxLayout()
        # group.setLayout(stte)
        # google = QCheckBox('Google')
        # # google.setDisabled(True)
        # stte.addWidget(google)
        # stte.addWidget(QCheckBox('Sphinx'))
        # box.addWidget(group)

        group = QGroupBox("Microphone")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)
        mic_box = QComboBox()
        group_layout.addWidget(mic_box)
        for mic in speech_recognition.Microphone.list_microphone_names():
            mic_box.addItem(mic)
        mic_box.currentIndexChanged.connect(lambda num: controller.speech.selectMic(num))

        box.addWidget(group)
        widget = QWidget()
        widget.setLayout(box)
        self.setWidget(widget)


class QuiController(object):
    def __init__(self):
        pass

    def window_init(self):
        self.speech = Speech()
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

    def save(self):
        path, t = QFileDialog.getSaveFileName()
        cur = self.document.begin()
        last = self.document.end()
        with open(path, 'w') as f:
            while cur != last:
                f.write(cur.text()+'\n\n')
                cur = cur.next()

    def load(self):
        path, t = QFileDialog.getOpenFileName()
        markdown = Markdown()
        markdown.serializer = self._loader
        markdown.convertFile(path)

    def _loader(self, element):
        root = ElementTree(element).getroot()
        self.document.clear()
        cur = self.document_editor.textCursor()
        for child in root.getchildren():
            form = getattr(self.document_editor, 'format_{}'.format(child.tag), None)

            cur.insertText(child.text+'\n', form)

        return to_html_string(element)


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

    format_h1 = QuiFormat(40, QFont.Bold)
    format_h2 = QuiFormat(35, QFont.Bold)
    format_h3 = QuiFormat(30, QFont.Bold)
    format_h4 = QuiFormat(30)
    format_h5 = QuiFormat(25)
    format_h6 = QuiFormat(20)

    format_p = QuiFormat(11)

    def __init__(self, controller):
        super().__init__()
        formc = QTextCharFormat()
        formc.setFontItalic(True)
        formc.setFontWeight(3)
        form = QTextBlockFormat()
        form.setLineHeight(200, 1)


        cur = self.textCursor()
        cur.insertText('', self.format_p)
        new_speech_signal = QObject()
        controller.speech.connect(self.new_speech_signal.emit)
        controller.speech.start()
        self.new_speech_signal.connect(cur.insertText)

    def setCurrentFont(self, font):
        cur = self.textCursor()
        cur.beginEditBlock()
        last_text = cur.block().text()
        last_pos = cur.position()
        cur.movePosition(cur.EndOfBlock)
        chars = cur.positionInBlock()
        for i in range(chars):
            cur.deletePreviousChar()
        cur.insertText(last_text, font)
        cur.setPosition(last_pos)
        self.setTextCursor(cur)
        cur.endEditBlock()


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
            (None, "Open", "Open a file", None, controller.load),
            (None, "Save", "Save the current file", None, controller.save),
            (None, "Exit", "Exit", None, controller.end),
        ]))

        self.addToolBar(QuiToolbar(self, 'FormatToolbar', [
            (None, "Heading 1", "Heading level one", "Ctrl+1", lambda: controller.document_editor.setCurrentFont(controller.document_editor.format_h1)),
            (None, "Heading 2", "Heading level two", "Ctrl+2", lambda: controller.document_editor.setCurrentFont(controller.document_editor.format_h2)),
            (None, "Heading 3", "Heading level three", "Ctrl+3", lambda: controller.document_editor.setCurrentFont(controller.document_editor.format_h3)),
            (None, "Heading 4", "Heading level four", "Ctrl+4", lambda: controller.document_editor.setCurrentFont(controller.document_editor.format_h4)),
            (None, "Heading 5", "Heading level five", "Ctrl+5", lambda: controller.document_editor.setCurrentFont(controller.document_editor.format_h5)),
            (None, "Heading 6", "Heading level six", "Ctrl+6", lambda: controller.document_editor.setCurrentFont(controller.document_editor.format_h6)),
            (None, "Body", "Simple body text", "Ctrl+`", lambda: controller.document_editor.setCurrentFont(controller.document_editor.format_p)),
        ]))


if __name__ == "__main__":
    QuiController().start()
