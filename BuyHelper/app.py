import sys
import time
import datetime
import getpass

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QAction, QMessageBox, QTextBrowser, QComboBox
from PyQt5.Qt import QLineEdit, QLabel
from PyQt5 import QtWidgets

from traceback import print_exc
from threading import Thread


from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class UI(QtWidgets.QWidget):
    """软件的界面布局"""

    def __init__(self):
        super().__init__()
        self.title = '扫货助手V2.0'
        self.left = 300
        self.top = 300
        self.width = 700
        self.height = 850

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 价格
        self.label_price = QLabel('价格', self)
        self.label_price.move(20, 20)
        self.textbox_price = QLineEdit(self)
        self.textbox_price.move(50, 20)
        self.textbox_price.resize(100, 25)

        # 最低价
        self.label_min_price = QLabel('最低价', self)
        self.label_min_price.move(175, 20)
        self.textbox_min_price = QLineEdit(self)
        self.textbox_min_price.move(225, 20)
        self.textbox_min_price.resize(100, 25)

        # 最高价
        self.label_max_price = QLabel('最高价', self)
        self.label_max_price.move(350, 20)
        self.textbox_max_price = QLineEdit(self)
        self.textbox_max_price.move(400, 20)
        self.textbox_max_price.resize(100, 25)

        # 浮动
        self.label_flow_price = QLabel('浮动价格', self)
        self.label_flow_price.move(20, 60)
        self.textbox_flow_price = QLineEdit(self)
        self.textbox_flow_price.move(85, 60)
        self.textbox_flow_price.resize(65, 25)

        # 浮动类型
        self.label_flow_type = QLabel('类型', self)
        self.label_flow_type.move(175, 60)
        self.select = QComboBox(self)
        self.select.move(225, 60)
        self.select.addItems(['增加', '降低'])
        self.select.resize(60, 20)

        self.btn_login = QPushButton('登录', self)
        self.btn_login.move(50, 100)
        self.btn_login.resize(75, 30)
        self.btn_login.clicked.connect(self.login_driver)

        self.btn_start = QPushButton('开始扫货', self)
        self.btn_start.move(150, 100)
        self.btn_start.resize(75, 30)
        self.btn_start.clicked.connect(self.start_buy)

        self.btn_stop = QPushButton('停止扫货', self)
        self.btn_stop.move(250, 100)
        self.btn_stop.resize(75, 30)
        self.btn_stop.clicked.connect(self.stop_buy)

        self.btn_stop = QPushButton('保存设置', self)
        self.btn_stop.move(350, 100)
        self.btn_stop.resize(75, 30)
        self.btn_stop.clicked.connect(self.on_click)

        # 日志框
        self.label_log = QLabel('购\n买\n记\n录', self)
        self.label_log.move(23, 150)
        self.textbox_log = QTextBrowser(self)
        self.textbox_log.move(50, 150)
        self.textbox_log.resize(600, 670)


class App(UI):

    def __init__(self):
        super().__init__()
        self.price = None
        self.min_price = None
        self.max_price = None
        self.flow_price = None
        self.flow_type = None
        self.driver = None

    def on_click(self):
        self.btn_login.setEnabled(False)
        self.init_param()

        def func():
            time.sleep(2)
            self.textbox_log.insertPlainText(f'{now_time()}球员：Michael Jeffrey Jordan购买成功!价格:35000\n')
            # self.textbox_log.setText('456\n') # 线程里不能这样
            self.btn_login.setEnabled(True)

        thread = Thread(target=func)
        thread.start()

    def start_buy(self):
        """开始扫货"""
        self.init_param()
        if not self.driver:
            reply = QMessageBox.question(self, '提示', '请先登录', QMessageBox.Yes, QMessageBox.No)
            return

        def func():
            try:
                self.driver.find_element_by_xpath('//button[text()="Search"]').click()
                time.sleep(.2)
                for i in range(30):
                    if i == 1:
                        if self.driver.execute_script('return document.getElementsByClassName("no-results-icon").length') > 0:
                            print(now_time(), '搜索结果为空，请手动返回只搜索界面重新输入查询条件')
                            break
                    try:
                        self.driver.find_element_by_xpath('//button[text()="Make Bid"]')
                        break
                    except:
                        time.sleep(.2)
                        continue
                if self.driver.execute_script('return document.getElementsByClassName("no-results-icon").length') > 0:
                    return

                # 接下来检索搜索到结果
                can_buy = self.driver.find_element_by_xpath('//button[text()="Make Bid"]').get_attribute('class')
                if 'disabled' not in can_buy:
                    js = 'return document.getElementsByClassName("listFUTItem has-auction-data selected")[0].' \
                         'getElementsByClassName("currency-coins value")[2].innerText'
                    res_html = self.driver.execute_script(js)
                    xpath = '//button[text()="Buy Now for %s"]' % res_html
                    self.log('开始点击购买')
                    for j in range(10):
                        try:
                            self.driver.find_element_by_xpath(xpath).click()
                            break
                        except Exception as e:
                            if j == 9:
                                self.log('购买失败')
                                print_exc()
                                raise e
                    self.driver.find_element_by_xpath('//span[text()="Ok"]').click()

                    time.sleep(2)
                    success = self.driver.execute_script(
                        'return document.getElementsByClassName("ut-item-details--metadata")[0].innerText')
                    if 'CONGRATULATIONS' in success:
                        self.log('购买成功！开始下一轮购买，请手动返回到搜索界面，注意搜索按钮不用点，程序会自动点击搜索')
                    else:
                        self.log('本次购买失败！开始下一轮购买，请手动返回到搜索界面，注意搜索按钮不用点，程序会自动点击搜索')
                else:
                    self.log('无法购买请检查是否超过购买限制')
            except Exception as ex:
                print_exc()
                self.log('购买出现错误，请手动返回到搜索页面开始下一轮购买 %s' % ex)

        thread = Thread(target=func)
        thread.start()
        # self.textbox_log.insertPlainText(f'{now_time()}球员：Michael Jeffrey Jordan购买成功!价格:35000\n')
        pass

    def stop_buy(self):
        """停止扫货"""
        pass

    def login_driver(self):
        """浏览器登录，用户手动登录即可"""
        self.btn_login.setEnabled(False)

        def func():
            option = ChromeOptions()
            option.add_argument(
                "--user-data-dir=" + r"C:/Users/%s/AppData/Local/Google/Chrome/User Data/" % getpass.getuser())
            url = 'https://www.easports.com/fifa/ultimate-team/web-app/'
            self.driver = webdriver.Chrome(executable_path='bin/chromedriver.exe', chrome_options=option)
            self.driver.implicitly_wait(10)
            self.driver.get(url)
            self.btn_login.setEnabled(True)
            self.log('请手动开始登录')

        thread = Thread(target=func)
        thread.start()

    def init_param(self):
        self.price = self.textbox_price.text()
        self.min_price = self.textbox_min_price.text()
        self.max_price = self.textbox_max_price.text()
        self.flow_price = self.textbox_flow_price.text()
        self.flow_type = self.select.currentText()

    def log(self, text):
        self.textbox_log.insertPlainText(f'{now_time()}日志：{text} \n')

    def init_settings(self):
        """加载化输入框的缓存"""
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
