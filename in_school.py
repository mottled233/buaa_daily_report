import logging
from time import sleep
import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

user = ""  # 你的统一认证账号
passwd = ""  # 你的统一认证密码json
position = ("39.97805900941237", "116.34515751812742")  # 定位，经纬度
SCKEY = ""  # 微信推送api，到http://sc.ftqq.com/ 免费申请，不需要请留空
set_time = [(18, 12)]  # (小时，分钟)， 如果多个时间可以写成[(h, m),(h, m)]的形式
max_attempt = 5  # 失败重复五次


def daka():
    login_flag, browser = login()
    if not login_flag:
        return

    browser.execute_script("window.navigator.geolocation.getCurrentPosition=function(success){" +
                           "var position = {\"coords\" : {\"latitude\": \"" + position[0] + "\",\"longitude\": \""
                           + position[1] + "\"}};" +
                           "success(position);}")

    location_button = browser.find_element_by_css_selector('div[name=area]>input')
    location_button.click()
    logger.info("成功输入经纬度")

    tiwen = browser.find_element_by_xpath("//div[@name='tw']/div/div[2]/span[1]")
    ActionChains(browser).move_to_element(tiwen).click(tiwen).perform()
    logger.info("成功输入体温")

    # 点击提交
    submit_button = browser.find_element_by_css_selector(
        'body > div.item-buydate.form-detail2.ncov-page > div > div > section > div.list-box > div > a')
    ActionChains(browser).move_to_element(submit_button).click(submit_button).perform()

    browser.implicitly_wait(3)
    while True:
        try:
            confirm_button = browser.find_element_by_css_selector('#wapcf > div > div.wapcf-btn-box > div.wapcf-btn.wapcf-btn-ok')
            result = '提交成功'
            break
        except:
            try:
                confirm_button = browser.find_element_by_css_selector('#wapat > div > div.wapat-btn-box > div')
                reason = browser.find_element_by_css_selector('#wapat > div > div.wapat-title').text
                result = f'打卡失败，原因：{reason}'
                break
            except:
                time.sleep(1)

    ActionChains(browser).move_to_element(confirm_button).click(confirm_button).perform()

    logger.info(result)

    datee = datetime.date.today()

    send_message(f"{datee} {result}")
    sleep(50)
    browser.quit()
    logger.info("流程结束")


def login():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(chrome_options=chrome_options)

    try:
        url = "https://app.buaa.edu.cn/uc/wap/login?redirect=https%3A%2F%2Fapp.buaa.edu.cn%2Fsite%2Fncov%2Fxisudailyup"
        browser.get(url)

        # 账号密码
        user_name_input = browser.find_element_by_css_selector('#app > div.content > div:nth-child(1) > input[type=text]')
        user_name_input.send_keys(user)
        user_pwd_input = browser.find_element_by_css_selector(
            '#app > div.content > div:nth-child(2) > input[type=password]')
        user_pwd_input.send_keys(passwd)

    except:
        logger.info("打开打卡网页失败，请确认网络")
        send_message("打开打卡网页失败，请确认网络")
        return False, None

    logger.info("成功打开打卡网页")

    # 点击登录按钮
    login_button = browser.find_element_by_css_selector('#app > div.btn')
    ActionChains(browser).move_to_element(login_button).click(login_button).perform()
    browser.implicitly_wait(2)

    # 跳转并点击获取位置按钮
    # 这样写是为了等待跳转页面加载出来
    fail_cnt = 0
    while True:
        location_button = browser.find_elements_by_css_selector('div[name=area]>input')
        if len(location_button) > 0:
            logger.info("登录成功")
            return True, browser
        else:
            # 出现密码错误提示框
            if len(browser.find_elements_by_css_selector('div.wapat-btn-box')) > 0:
                send_message("打卡失败，用户名密码错误，程序已退出，请检查")
                logger.info("打卡失败，用户名密码错误，请检查")
                exit(0)

            # 若只是反应慢，重试
            if fail_cnt >= max_attempt:
                send_message("登录超时超过最大尝试次数，请检查网络或打卡系统已崩溃")
                logger.info("登录超时超过最大尝试次数")
                return False, None
            time.sleep(10)
            browser.get("https://app.buaa.edu.cn/site/ncov/xisudailyup")
            logger.info("登录超时，正在重试")
            fail_cnt += 1


def main():  # 0:05进行打卡
    logger.info("正在进行验证...")
    flag, browser = login()  # 测试能否进入网页以及用户名密码是否正确
    browser.quit()
    if not flag:
        exit(0)
    while True:
        while True:
            # time_up = True  # debug
            time_up = False
            now = datetime.datetime.now()
            for hour, minute in set_time:
                if now.hour == hour and now.minute == minute:
                    time_up = True
            if time_up:
                break
            logger.debug(f"时间未到，当前时间 {now}")
            sleep(20)
        logger.info("时间已到，正在打卡")
        daka()


def send_message(msg):
    if SCKEY == "":
        return
    payload = {'text': msg}
    requests.get(f"https://sc.ftqq.com/{SCKEY}.send", params=payload)


if __name__ == "__main__":
    log_file = "log.log"
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    logger = logging.getLogger("main")
    fh = logging.FileHandler(log_file, mode='w')
    fh.setFormatter(formatter)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    main()
