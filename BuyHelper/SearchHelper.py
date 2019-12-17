import getpass
from selenium import webdriver
import datetime
import time
from traceback import print_exc

from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


option = ChromeOptions()
option.add_argument("--user-data-dir=" + r"C:/Users/%s/AppData/Local/Google/Chrome/User Data/" % getpass.getuser())


def now_time():
    return datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')


def search():
    # tuihua705@yeah.net   密码 Woaini123   邮箱密码 degen472
    url = 'https://www.easports.com/fifa/ultimate-team/web-app/'
    driver = webdriver.Chrome(executable_path='bin/chromedriver.exe', chrome_options=option)
    driver.implicitly_wait(10)
    driver.get(url)
    print(now_time(), '请开始手动登录')

    while True:
        try:
            input(now_time() + ' 搜索条件输入完毕请敲回车，注意搜索按钮不用点，程序会自动点击搜索')
            driver.find_element_by_xpath('//button[text()="Search"]').click()
            time.sleep(.2)
            for i in range(30):
                if i == 1:
                    if driver.execute_script('return document.getElementsByClassName("no-results-icon").length') > 0:
                        print(now_time(), '搜索结果为空，请手动返回只搜索界面重新输入查询条件')
                        break
                try:
                    driver.find_element_by_xpath('//button[text()="Make Bid"]')
                    break
                except:
                    time.sleep(.2)
                    continue
            if driver.execute_script('return document.getElementsByClassName("no-results-icon").length') > 0:
                continue
            # 接下来检索搜索到结果
            # length = driver.execute_script('return document.getElementsByClassName("listFUTItem has-auction-data selected").length')

            can_buy = driver.find_element_by_xpath('//button[text()="Make Bid"]').get_attribute('class')
            if 'disabled' not in can_buy:
                res_html = driver.execute_script('return document.getElementsByClassName("listFUTItem has-auction-data selected")[0].getElementsByClassName("currency-coins value")[2].innerText')
                xpath = '//button[text()="Buy Now for %s"]' % res_html
                print(now_time(), '开始点击购买')
                for j in range(10):
                    try:
                        driver.find_element_by_xpath(xpath).click()
                        break
                    except Exception as e:
                        if j == 9:
                            print('购买失败')
                            print_exc()
                            raise e
                driver.find_element_by_xpath('//span[text()="Ok"]').click()

                time.sleep(2)
                success = driver.execute_script(
                    'return document.getElementsByClassName("ut-item-details--metadata")[0].innerText')
                if 'CONGRATULATIONS' in success:
                    print(now_time() + '购买成功！开始下一轮购买，请手动返回到搜索界面，注意搜索按钮不用点，程序会自动点击搜索')
                else:
                    print(now_time() + ' **本次购买失败！开始下一轮购买，请手动返回到搜索界面，注意搜索按钮不用点，程序会自动点击搜索')
            else:
                print(now_time(), '无法购买请检查是否超过购买限制')
        except Exception:
            print_exc()
            print(now_time() + '购买出现错误，请手动返回到搜索页面开始下一轮购买')


if __name__ == '__main__':
    search()
    # print(now_time())
    # document.getElementsByClassName("dialog-msg")[0].innerText
