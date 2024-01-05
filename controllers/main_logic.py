import configparser
import logging
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QDialog
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from ui.MainWindow import Ui_MainWindow
from services.rush import login, rush
from ui.LoginDialog import Ui_LoginDialog
from ui.CourseDialog import Ui_CourseDialog


# 主窗口逻辑
class MainWindowLogic(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindowLogic, self).__init__(parent)
        self.setupUi(self)

        # 初始化变量
        self.uid = None
        self.pwd = None
        self.type = 1
        self.mode = 1
        self.blacklist = []
        self.whitelist = []
        self.login_thread = None
        self.rush_thread = None

        # UI部件
        # Button_login
        self.Button_login.clicked.connect(self.Button_login_clicked)
        # Button_rush
        self.Button_rush.clicked.connect(self.Button_rush_clicked)
        # logTextfield
        self.log_thread = LogThread(self)
        self.log_thread.update_log_signal.connect(self.updateLogTestfield)
        # Button_setting
        self.Button_setting.clicked.connect(self.Button_setting_clicked)
        # Button_edit
        self.Button_edit.clicked.connect(self.Button_edit_clicked)
        #

    def Button_login_clicked(self):
        # 检查线程是否已经存在
        if self.login_thread is not None and self.login_thread.isRunning():
            return
        else:
            # 检查 RushThread 是否正在运行
            if self.rush_thread is not None and self.rush_thread.is_alive():
                self.rush_thread.stop()
                self.rush_thread.wait()

            # 获取参数
            self.getLoginInfo()

            # 启动线程
            self.login_thread = LoginThread(self.uid, self.pwd)
            self.login_thread.start()

    def Button_rush_clicked(self):
        # 启动线程
        if self.rush_thread is not None and self.rush_thread.isRunning():
            return
        else:
            # 检查 LoginThread 是否正在运行
            if self.login_thread is not None and self.login_thread.isRunning():
                self.login_thread.stop()
                self.login_thread.join()

            # 获取参数
            self.getLoginInfo()
            self.getType()
            self.getMode()
            self.getList()

            # 启动线程
            self.printInfo()
            self.rush_thread = RushThread(self.uid, self.pwd, self.type, self.mode, self.blacklist, self.whitelist)
            self.rush_thread.start()

    def getLoginInfo(self):
        config = configparser.ConfigParser()
        try:
            config.read('resources/config.ini')
            self.uid = config.get('login', 'uid')
            self.pwd = config.get('login', 'pwd')
        except configparser.Error:
            logging.info("登录信息不存在")

    def getMode(self):
        if self.radioButton_3.isChecked():
            self.mode = 1
            # 抢课模式：自由
        elif self.radioButton_4.isChecked():
            self.mode = 2
            # 抢课模式：白名单
        elif self.radioButton_5.isChecked():
            self.mode = 3
            # 抢课模式：黑名单
        else:
            self.mode = 1

    def getType(self):
        if self.radioButton_1.isChecked():
            self.type = 0
            # 课程类型：专选课
        elif self.radioButton_2.isChecked():
            self.type = 1
            # 课程类型：公选课
        else:
            self.type = 0

    def getList(self):
        config = configparser.ConfigParser()
        config_path = 'resources/config.ini'
        config.read(config_path)

        if config.has_section('blackList'):
            self.blacklist = [config.get('blackList', key) for key in config['blackList']]

        if config.has_section('whiteList'):
            self.whitelist = [config.get('whiteList', key) for key in config['whiteList']]

    def printInfo(self):
        # type
        if self.type == 0:
            logging.info("课程类型：专选课")
        elif self.type == 1:
            logging.info("课程类型：公选课")
        # mode
        if self.mode == 1:
            logging.info("抢课模式：自由")
        elif self.mode == 2:
            logging.info("抢课模式：白名单")
        elif self.mode == 3:
            logging.info("抢课模式：黑名单")
        # list
        if self.mode == 2:
            logging.info(f"白名单：{self.whitelist}")
        elif self.mode == 3:
            logging.info(f"黑名单：{self.blacklist}")

    def updateLogTestfield(self, content):
        self.logTextfield.setPlainText(content)
        cursor = self.logTextfield.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.logTextfield.setTextCursor(cursor)

    def Button_setting_clicked(self):
        self.login_dialog = LoginDialog(self)
        self.login_dialog.exec_()

    def Button_edit_clicked(self):
        self.getMode()
        if self.mode != 1:
            self.edit_dialog = CourseDialog(self.mode, self)
            self.edit_dialog.exec_()


# login线程
class LoginThread(QThread):
    def __init__(self, uid, pwd):
        super(LoginThread, self).__init__()
        self.uid = uid
        self.pwd = pwd
        self.driver = None

    def run(self):
        self.stop()
        try:
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            self.driver.get("http://jwxk.hrbeu.edu.cn/xsxk/profile/index.html")
            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, "loginDiv")))
            login(self.driver, self.uid, self.pwd)
        except Exception as e:
            print(f"发生错误: {e}")

    def stop(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
        self.quit()
        self.wait()


# rush线程
class RushThread(QThread):
    def __init__(self, uid, pwd, type, mode, blacklist, whitelist):
        super(RushThread, self).__init__()
        self.uid = uid
        self.pwd = pwd
        self.type = type
        self.mode = mode
        self.blacklist = blacklist
        self.whitelist = whitelist
        self.driver = None

    def run(self):
        try:
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            self.driver.get("http://jwxk.hrbeu.edu.cn/xsxk/profile/index.html")
            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, "loginDiv")))
            login(self.driver, self.uid, self.pwd)
            rush(self.driver, self.type, self.mode, self.blacklist, self.whitelist)
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            self.stop()

    def stop(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
        self.quit()
        self.wait()


# log线程
class LogThread(QThread):
    update_log_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(LogThread, self).__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(1000)

    @pyqtSlot()
    def update_log(self):
        try:
            with open('resources/app.log', 'r') as f:
                content = f.read()
            # 发送信号，将日志内容传递给主线程更新 UI
            self.update_log_signal.emit(content)
        except Exception as e:
            print(f"Failed to update log: {e}")


class LoginDialog(QDialog, Ui_LoginDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setupUi(self)
        # Button_save
        self.Button_save.clicked.connect(self.Button_save_clicked)

    def setLoginInfo(self):
        # 获取用户输入的账号和密码
        uid = self.lineEdit_uid.text()
        pwd = self.lineEdit_pwd.text()
        # 创建一个配置解析器对象
        config = configparser.ConfigParser()
        # 添加一个配置节
        config.add_section('login')
        # 在该节中设置账号和密码
        config.set('login', 'uid', uid)
        config.set('login', 'pwd', pwd)
        # 指定 INI 文件的完整路径
        ini_file_path = 'resources/config.ini'
        # 将配置写入到 INI 文件中
        with open(ini_file_path, 'w') as configfile:
            config.write(configfile)

    def Button_save_clicked(self):
        self.setLoginInfo()
        self.close()


class CourseDialog(QDialog, Ui_CourseDialog):
    def __init__(self, mode, parent=None):
        super(CourseDialog, self).__init__(parent)
        self.setupUi(self)
        self.mode = mode
        # Button_save2
        self.Button_save2.clicked.connect(self.Button_save2_clicked)

    def setList(self):
        # 获取 CourseTextEdit 的文本内容
        text = self.CourseTextEdit.toPlainText()
        # 按行分割
        lines = text.split('\n')

        ini_file_path = 'resources/config.ini'
        config = configparser.ConfigParser()
        # 读取现有配置
        config.read(ini_file_path)


        if self.mode == 2:
            section = 'whiteList'
        elif self.mode == 3:
            section = 'blackList'
        else:
            return

        # 如果节不存在，添加它
        if not config.has_section(section):
            config.add_section(section)
        else:
            # 清除旧配置
            config.remove_section(section)
            config.add_section(section)

        # 更新配置
        for i, line in enumerate(lines):
            if line.strip():
                config.set(section, f'line{i}', line)
        # 将更新后的配置写回文件
        with open(ini_file_path, 'w') as configfile:
            config.write(configfile)

    def Button_save2_clicked(self):
        self.setList()
        self.close()
