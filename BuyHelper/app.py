import ctypes
import inspect
import sys
import datetime
import getpass
import numpy as np
import cv2
import os
import aircv as ac
from PIL import ImageGrab
import pyautogui
import time

# 提前导入防止打包exe后运行报错
import PyQt5.sip
from PyQt5.QtWidgets import QPushButton, QMessageBox, QTextBrowser, QComboBox
from PyQt5.Qt import QLineEdit, QLabel
from PyQt5 import QtWidgets

from traceback import print_exc
from threading import Thread


from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class Back:
    def cv_imread(self, filePath):
        cv_img = cv2.imdecode(np.fromfile(filePath, dtype=np.uint8), -1)
        return cv_img

    # 获取匹配到的区域中心点坐标
    def get_pos(self, need, tar):
        # 含中文字符的路径会无法加载
        bg = self.cv_imread(need)  # 全屏截图
        obj = self.cv_imread(tar)  # 目标区域
        pos = ac.find_template(bg, obj)  # 对比图片识别出坐标
        if pos:
            x = int(pos['result'][0])
            y = int(pos['result'][1])
            center_pos = (x, y)
            return center_pos

    def back(self):
        for i in range(10):
            img = ImageGrab.grab()
            img.save('temp.png')
            pos = self.get_pos('temp.png', 'back.png')
            if pos:
                pyautogui.click(*pos)
                return True
            if i == 9:
                return False
            time.sleep(.5)


def back():
    back = Back()
    return back.back()


class UI(QtWidgets.QWidget):
    """软件的界面布局"""

    def __init__(self):
        super().__init__()
        self.title = '扫货助手V2.1'
        self.left = 300
        self.top = 300
        self.width = 700
        self.height = 850

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 最低价
        self.label_min_price = QLabel('最低价', self)
        self.label_min_price.move(20, 20)
        self.textbox_min_price = QLineEdit(self)
        self.textbox_min_price.move(50, 20)
        self.textbox_min_price.resize(100, 25)

        # 最高价
        self.label_max_price = QLabel('最高价', self)
        self.label_max_price.move(175, 20)
        self.textbox_max_price = QLineEdit(self)
        self.textbox_max_price.move(225, 20)
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

        # 查找次数

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
        self.btn_stop.clicked.connect(self.save_settings)

        # 日志框
        self.label_log = QLabel('购\n买\n记\n录', self)
        self.label_log.move(23, 150)
        self.textbox_log = QTextBrowser(self)
        self.textbox_log.move(50, 150)
        self.textbox_log.resize(600, 670)


class App(UI):

    def __init__(self):
        super().__init__()
        self.min_price = None
        self.max_price = None
        self.flow_price = None
        self.flow_type = None
        self.driver = None
        self.search_times = 2
        self.start_thread = None

    def on_click(self):
        self.btn_login.setEnabled(False)
        self.init_param()

        def func():
            time.sleep(4)
            print('on_click')
            # self.textbox_log.insertPlainText(f'{now_time()}球员：Michael Jeffrey Jordan购买成功!价格:35000\n')
            # self.textbox_log.setText('456\n') # 线程里不能这样
            self.btn_login.setEnabled(True)
        thread = Thread(target=func)
        thread.start()

    def start_buy(self):
        """开始扫货"""
        self.init_param()
        if not self.driver:
            QMessageBox.question(self, '提示', '请先登录', QMessageBox.Yes, QMessageBox.No)
            return

        def func():
            self.btn_start.setEnabled(False)
            for search_time in range(2):
                try:
                    WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Search"]')))
                    self.fill_price(search_time)
                    time.sleep(.1)
                    self.driver.find_element_by_xpath('//button[text()="Search"]').click()
                    time.sleep(.2)
                    no_result = False
                    result_length_js = "return document.getElementsByClassName('name').length"
                    no_result_length_js = "return document.getElementsByClassName('no-results-icon').length"
                    for i in range(30):
                        if self.driver.execute_script(result_length_js) > 0 and i == 1:
                            break
                        if self.driver.execute_script(no_result_length_js) > 0 and i == 3:
                            no_result = True
                            break
                        time.sleep(.1)
                    if no_result:
                        back()
                        time.sleep(.2)
                        continue

                    if self.driver.execute_script(result_length_js) == 0:
                        back()
                        time.sleep(.2)
                        continue
                    # 接下来检索搜索到结果
                    can_buy = self.driver.find_element_by_xpath('//button[text()="Make Bid"]').get_attribute('class')
                    if 'disabled' not in can_buy:
                        js = 'return document.getElementsByClassName("listFUTItem has-auction-data selected")[0].' \
                             'getElementsByClassName("currency-coins value")[2].innerText'
                        res_price = self.driver.execute_script(js)
                        xpath = '//button[text()="Buy Now for %s"]' % res_price
                        self.log('开始点击购买')
                        for j in range(20):
                            try:
                                self.driver.find_element_by_xpath(xpath).click()
                                break
                            except Exception as e:
                                if j == 19:
                                    self.log('开始点击购买失败 %s' % e)
                                    print_exc()
                                    raise e
                                time.sleep(.1)
                        for j in range(20):
                            try:
                                self.driver.find_element_by_xpath('//span[text()="Ok"]').click()
                                break
                            except Exception as e:
                                if j == 19:
                                    print_exc()
                                    self.log('点击确认购买ok出现错误 %s' % e)
                                    raise e
                        time.sleep(2)
                        success = self.driver.execute_script(
                            'return document.getElementsByClassName("ut-item-details--metadata")[0].innerText')
                        if 'CONGRATULATIONS' in success:
                            player_name = self.driver.find_elements_by_class_name('name')[0].text
                            self.log(f'球员：{player_name}购买成功!价格:{res_price} 此次购买结束')
                            self.start_thread = None
                            break
                        else:
                            self.log('本次购买失败！开始下一轮购买')
                            back()
                            time.sleep(.2)
                            continue
                    else:
                        self.log('无法购买请检查是否超过购买限制')
                except Exception as ex:
                    print_exc()
                    self.log('购买出现错误，请手动返回到搜索页面开始下一轮购买 %s' % ex)
                    back()
                    time.sleep(.2)
            self.btn_start.setEnabled(True)
        self.start_thread = Thread(target=func)
        self.start_thread.start()
        # self.textbox_log.insertPlainText(f'{now_time()}球员：Michael Jeffrey Jordan购买成功!价格:35000\n')

    def fill_price(self, search_time):
        max_price = self.max_price
        min_price = self.min_price
        if search_time > 0:
            if self.flow_price:
                if self.flow_type == '增加' and max_price:
                    max_price = f'{int(self.max_price) + int(self.flow_price)}'
                elif min_price:
                    min_price = f'{int(self.min_price) - int(self.flow_price)}'
        if min_price:
            ele_min = self.driver.find_elements_by_class_name('numericInput')[2]
            ele_min.clear()
            ele_min.send_keys(min_price)
        if max_price:
            ele_max = self.driver.find_elements_by_class_name('numericInput')[3]
            ele_max.clear()
            ele_max.send_keys(max_price)

    def stop_buy(self):
        """停止扫货"""
        if self.start_thread:
            self._async_raise(self.start_thread.ident, SystemExit)
            self.btn_start.setEnabled(True)
            self.start_thread = None
            QMessageBox.question(self, '提示', '搜索已停止', QMessageBox.Yes, QMessageBox.No)

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def login_driver(self):
        """浏览器登录，用户手动登录即可"""
        self.btn_login.setEnabled(False)

        def func():
            option = ChromeOptions()
            option.add_argument(
                "--user-data-dir=" + r"C:/Users/%s/AppData/Local/Google/Chrome/User Data/" % getpass.getuser())
            url = 'https://www.easports.com/fifa/ultimate-team/web-app/'
            base_path = os.path.dirname(__file__)
            executable_path = os.path.join(base_path, 'bin/chromedriver.exe')
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=option)
            self.driver.implicitly_wait(10)
            self.driver.get(url)
            self.btn_login.setEnabled(True)
            self.log('请手动开始登录，切记，登录成功请手动进入到搜索界面')

        thread = Thread(target=func)
        thread.start()

    def init_param(self):
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
        self.init_param()
        """保存设置"""
        QMessageBox.question(self, '提示', '保存成功', QMessageBox.Yes, QMessageBox.No)


def now_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '|'


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
