import logging
import base64
from time import sleep
import ddddocr
from selenium.webdriver.common.by import By


def login(driver, uid, pwd):
    max_attempts = 5
    attempts = 0

    while attempts < max_attempts:
        try:
            logging.info("尝试登录")
            # 账号
            usr_div = driver.find_element(By.ID, "loginNameDiv")
            usr_text = usr_div.find_element(By.CLASS_NAME, "el-input__inner")
            usr_text.send_keys(uid)
            # 密码
            pwd_div = driver.find_element(By.ID, "loginPwdDiv")
            pwd_text = pwd_div.find_element(By.CLASS_NAME, "el-input__inner")
            pwd_text.send_keys(pwd)
            # 验证码
            img = driver.find_element(By.ID, "vcodeImg")
            img_src = img.get_attribute("src")
            img_base64 = img_src.split(',')[1]
            img_data = base64.b64decode(img_base64)

            ocr = ddddocr.DdddOcr()
            res = ocr.classification(img_data)
            verify_text = driver.find_element(By.ID, "verifyCode")
            verify_text.send_keys(res)
            # 登录
            login_button_div = driver.find_element(By.ID, "loginDiv")
            login_button = login_button_div.find_element(By.CLASS_NAME, "el-button")
            login_button.click()
            sleep(0.5)
            # 选择轮次
            driver.find_element(By.CSS_SELECTOR, "button[class='el-button el-button--primary']").click()
            sleep(0.5)
            # 进入选课
            driver.find_element(By.CSS_SELECTOR,
                                "button[class='el-button courseBtn el-button--primary is-round']").click()
            sleep(0.5)
            # 跳过教程
            driver.find_element(By.CSS_SELECTOR,
                                "img[src='http://jwxk.hrbeu.edu.cn/xsxk/profile/image/guide.png']").click()
            sleep(0.5)
            logging.info("登录成功")
            break  # 登录成功
        except Exception :
            logging.info("登录失败，正在重试")
            attempts += 1
            if attempts >= max_attempts:
                logging.info("达到最大尝试次数，脚本自动结束")
                break
            sleep(1)
            driver.refresh()


def rush(driver, type, mode, blacklist, whitelist):


    # 选课模式
    def should_select_course(course_name):
        if mode == 1:
            return True
        elif mode == 2 and course_name in whitelist:
            return True
        elif mode == 3 and course_name not in blacklist:
            return True
        return False


    # 公选课
    if (type):
        counter = 0
        # 公选课按钮
        gongxuanke_button = driver.find_element(By.XPATH, "(//li[@role='menuitem'])[2]")
        gongxuanke_button.click()
        # 选课
        while 1:
            # 当前页面课程列表
            courses = driver.find_elements(By.CLASS_NAME, "el-table__row")
            for cour in courses:
                course_name = cour.find_element(By.CSS_SELECTOR, "td.el-table_1_column_3 .cell span").text
                try:
                    # 课程已满
                    cour.find_element(By.CSS_SELECTOR, "span[class='el-tag el-tag--danger el-tag--mini el-tag--dark']")
                except:
                    if should_select_course(course_name):
                        # 未满课程
                        try:
                            # 检查是否在黑名单
                            if course_name in blacklist:
                                continue
                            # 选课按钮
                            select_button = cour.find_element(By.CSS_SELECTOR,
                                                              "button[class='el-button el-button--primary el-button--mini is-round']")
                            select_button.click()
                            sleep(0.1)
                            # 确认按钮
                            driver.find_element(By.CSS_SELECTOR,
                                                "button[class='el-button el-button--default el-button--small el-button--primary ']").click()
                            sleep(0.05)

                            if (select_button.text == "退选"):
                                logging.info("抢到" + course_name)
                        except:
                            logging.info("已选过 " + course_name)
                            counter += 1
                            if counter == 5:
                                logging.info("公选课已选满或目标课程已抢到，脚本自动结束")
                                return
            # 下一页
            if driver.find_element(By.CLASS_NAME, "btn-next").get_attribute("disabled"):
                driver.find_element(By.CSS_SELECTOR, "ul[class='el-pager'] :nth-child(1)").click()
            else:
                driver.find_element(By.CLASS_NAME, "btn-next").click()

            sleep(0.2)

    # 专业课
    else:
        # 选课
        while 1:
            # 当前页面课程列表
            courses = driver.find_elements(By.CLASS_NAME, "el-table__row")
            for cour in courses:
                course_name = cour.find_element(By.CSS_SELECTOR, "td.el-table_1_column_3 .cell span").text
                try:
                    # 课程已满
                    cour.find_element(By.CSS_SELECTOR, "span[class='el-tag el-tag--danger el-tag--mini el-tag--dark']")
                except:
                    if should_select_course(course_name):
                        # 未满课程
                        try:
                            # 打开折叠项
                            expand_button = cour.find_element(By.CSS_SELECTOR, "td.el-table_1_column_3 .cell span")
                            expand_button.click()
                            # 选课按钮
                            select_button = driver.find_element(By.CSS_SELECTOR,
                                                                ".el-button.el-button--primary.el-button--mini.is-round")
                            if (select_button.text == "选择"):
                                select_button.click()
                            sleep(0.1)
                            # 确认按钮
                            driver.find_element(By.CSS_SELECTOR,
                                                "button[class='el-button el-button--default el-button--small el-button--primary ']").click()
                            sleep(0.05)

                            if (select_button.text == "退选"):
                                logging.info("抢到" + course_name)

                        except:
                            logging.info("已选过 " + course_name)
                        finally:
                            # 关闭折叠项
                            if course_name not in blacklist:
                                expand_button.click()
            # 下一页
            if driver.find_element(By.CLASS_NAME, "btn-next").get_attribute("disabled"):
                driver.find_element(By.CSS_SELECTOR, "ul[class='el-pager'] :nth-child(1)").click()
            else:
                driver.find_element(By.CLASS_NAME, "btn-next").click()

            sleep(0.2)