import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

import SCOPE

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('123.ico'))
    MainWindow = QMainWindow()
    ui = SCOPE.Ui_scope()
    ui.setupUi(MainWindow)
    MainWindow.setFixedSize(640, 480)
    MainWindow.show()
    sys.exit(app.exec_())

