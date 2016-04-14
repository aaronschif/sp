import sys
from .gui import MainWindow, QApplication
from PyQt5.Qt import QSettings


class Controller(object):
    def __init__(self):
        self.app = None
        self.window = None
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "spp", "qui")

    def start(self):
        app = QApplication(sys.argv)
        self.window = MainWindow(self)
        self.window.show()
        app.exec_()

    def stop(self):
        pass

    def title(self):
        return "SPP"

    def handle_close(self):
        swlf.window.close()
