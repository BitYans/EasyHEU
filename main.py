import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QCoreApplication
from controllers.main_logic import MainWindowLogic
import sys


def main():
    # log
    logging.basicConfig(filename='./resources/app.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S')
    logging.info("欢迎！第一次使用前请先进行设置")
    # GUI
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = MainWindowLogic()
    window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
    window.setWindowIcon(QIcon('resources/icon.ico'))
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
