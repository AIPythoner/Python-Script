import sys
import time
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QAction, QMessageBox, QTextBrowser
from PyQt5.Qt import QLineEdit, QLabel
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, QtCore

from SearchHelper import search
from threading import Thread


class App(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.title = '扫货助手V2.0'
        self.left = 300
        self.top = 300
        self.width = 840
        self.height = 850

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 球员
        self.label_player = QLabel('球员', self)
        self.label_player.move(20, 20)
        self.textbox_player = QLineEdit(self)
        self.textbox_player.move(55, 20)
        self.textbox_player.resize(150, 25)

        # 最低价
        self.label_min_price = QLabel('最低价', self)
        self.label_min_price.move(250, 20)
        self.textbox_min_price = QLineEdit(self)
        self.textbox_min_price.move(300, 20)
        self.textbox_min_price.resize(100, 25)

        # 最高价
        self.label_max_price = QLabel('最高价', self)
        self.label_max_price.move(450, 20)
        self.textbox_max_price = QLineEdit(self)
        self.textbox_max_price.move(500, 20)
        self.textbox_max_price.resize(100, 25)

        # 最高价
        self.label_flow_price = QLabel('浮动价格', self)
        self.label_flow_price.move(650, 20)
        self.textbox_flow_price = QLineEdit(self)
        self.textbox_flow_price.move(715, 20)
        self.textbox_flow_price.resize(100, 25)

        self.btn_login = QPushButton('登录', self)
        self.btn_login.move(50, 75)
        self.btn_login.resize(75, 30)
        self.btn_login.clicked.connect(self.login_driver)

        self.btn_start = QPushButton('开始扫货', self)
        self.btn_start.move(150, 75)
        self.btn_start.resize(75, 30)
        self.btn_start.clicked.connect(self.on_click)

        self.btn_stop = QPushButton('停止扫货', self)
        self.btn_stop.move(250, 75)
        self.btn_stop.resize(75, 30)
        self.btn_stop.clicked.connect(self.on_click)

        self.btn_stop = QPushButton('保存设置', self)
        self.btn_stop.move(350, 75)
        self.btn_stop.resize(75, 30)
        self.btn_stop.clicked.connect(self.on_click)

        # 日志框
        self.label_player = QLabel('购\n买\n记\n录', self)
        self.label_player.move(23, 120)
        self.textbox_log = QTextBrowser(self)
        self.textbox_log.move(50, 120)
        self.textbox_log.resize(600, 700)

    def on_click(self):
        # print(self.textbox_player.text())
        self.btn_login.setEnabled(False)

        def func():
            time.sleep(2)
            self.textbox_log.insertPlainText(f'{now_time()}球员：Michael Jeffrey Jordan购买成功!价格:35000\n')
            # self.textbox_log.setText('456\n') # 线程里不能这样

            self.btn_login.setEnabled(True)

        thread = Thread(target=func)
        thread.start()
        # self.textbox_log.insertPlainText('123\n')
        # self.textbox_log.setText('456\n')

    def init_settings(self):
        """加载化输入框的缓存"""
        pass

    def start_buy(self):
        """开始扫货"""
        pass

    def stop_buy(self):
        """停止扫货"""
        pass

    def login_driver(self):
        """浏览器登录，用户手动登录即可"""

        def func():
            search()
        thread = Thread(target=func)
        thread.start()
        pass

    def save_settings(self):
        """保存设置"""
        pass


def now_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' | '


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
