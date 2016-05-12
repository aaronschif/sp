import sys

class Settings(object):
    pass


def link_pyqt():
    sys.path.append('/usr/lib/python3/dist-packages/')
    from PyQt5.QtCore import QSettings
    from PyQt5.QtWidgets import QWidget
    # from PyQt5.QtGui import QWidget
    import sip
    sys.path.pop()
