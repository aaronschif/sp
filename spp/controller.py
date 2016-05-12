import sys
import signal

from blist import blist
from markdown.treeprocessors import Treeprocessor
import markdown

from .gui import MainWindow, QApplication


class MyTreeprocessor(Treeprocessor):
    def __init__(self, *args, **kwargs):
        self._exportable = None

    def run(self, root):
        root.text = 'modified content'


class Controller(object):
    def __init__(self):
        self.app = None
        self.window = None
        # self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "spp", "qui")
        signal.signal(signal.SIGINT, self.handle_close)

    def start(self):
        app = QApplication(sys.argv)
        self.window = MainWindow(self)
        self.window.show()
        app.exec_()

    def stop(self):
        pass

    def title(self):
        return "QuickText"

    def handle_close(self, *_):
        self.window.close()

    def handle_load(self, path):
        print('handle_load')


class Document(object):
    def __init__(self):
        self._document = None

    def document(self):
        if self._document is None:
            self._document = QTextDocument()
        return self._document

    def load(self, file):
        doc = MyTreeprocessor()
        md = markdown.Markdown(extensions=[doc])

    def save(self, file):
        pass

    def change(self, num, value):
        pass


if __name__ == '__main__':
    print(blist([('h1', 'adsfffd'), ('h2', 'asdfsdafwwfw')]))
