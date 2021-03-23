import os
import sys
import zipfile

import pandas as pd
import requests
from flask import Flask, render_template, Response
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from twocaptcha import TwoCaptcha

APP = Flask(__name__, static_folder="app/static/", template_folder="app/static/")


@APP.route("/", methods=["GET"])
def root():
    """index page"""
    return render_template("index.html")


# configure logger
logger.add("app/static/job.log", format="{time} - {message}")

PROXY_HOST = '82.78.55.70'  # rotating proxy
PROXY_PORT = 4129
PROXY_USER = 'exel'
PROXY_PASS = 'OvY5AUmj28'

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
        chrome_options.add_argument("--incognito")
        chrome_options.binary_location = '/app/.apt/usr/bin/google-chrome'

    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    global driver
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        chrome_options=chrome_options)
    return driver


def scrapper():
    yield "Starting the bot...\n"
    df = pd.read_csv('post_data.csv')

    Name = df['Name']
    Option = df['Options']
    Subject = df['Subject']
    Comment = df['Comment']
    Image_url = df['Image']

    Image_Path = "C:/Users/Dexter/PycharmProjects/4chan_Poster/post_image.jpg"

    df1 = pd.read_csv('reply_data.csv')

    Name1 = df1['Name']
    Option1 = df1['Options']
    Comment1 = df1['Comment']
    Image_url1 = df1['Image']

    Image_Path1 = "C:/Users/Dexter/PycharmProjects/4chan_Poster/reply_image.jpg"

    global post_url
    post_url = ''
    i = 0
    while i < len(Name):
        driver = get_chromedriver(use_proxy=True)
        write_image = open("post_image.jpg", 'wb+')
        image_content = requests.get(Image_url[i]).content
        write_image.write(image_content)
        write_image.close()
        yield "Creating a New Thread...\n"
        yield str(
            "Name : " + Name[i] + "\nOption : " + Option[i] + "\nSubject : " + Subject[i] + "\nComment : " + Comment[i]+"\n\n")
        driver.get("https://boards.4channel.org/biz/")
        driver.find_element_by_id("togglePostFormLink").click()
        driver.find_element_by_xpath("//*[@id='postForm']/tbody/tr[1]/td[2]/input").send_keys(Name[i])
        driver.find_element_by_xpath("//*[@id='postForm']/tbody/tr[2]/td[2]/input").send_keys(Option[i])
        driver.find_element_by_xpath("//*[@id='postForm']/tbody/tr[3]/td[2]/input[1]").send_keys(Subject[i])
        driver.find_element_by_xpath("//*[@id='postForm']/tbody/tr[4]/td[2]/textarea").send_keys(Comment[i])
        driver.find_element_by_xpath("//*[@id='postFile']").send_keys(Image_Path)

        yield "Solving Captcha...\n"
        solver = TwoCaptcha('cd8bddb5facaad70dff1e10a22b60b0b')

        try:
            result = solver.recaptcha(
                sitekey='6Ldp2bsSAAAAAAJ5uyx_lx34lJeEpTLVkP5k04qc',
                url=driver.current_url)

        except Exception as e:
            sys.exit(e)

        else:
            driver.execute_script(
                'var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
            driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]',
                                  str(result['code']))
            driver.find_element_by_id("g-recaptcha-response").submit()
        try:
            xpath = "/html/body/table/tbody/tr/td/span/a"
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            yield "Duplicate Post Exists Moving to Duplicate post\n"
            driver.find_element_by_xpath(xpath).click()

        except:
            yield "Thread Successfully Posted...\n"

        post_url = driver.current_url
        driver.get(
            'http://82.78.55.70:3158/8D5D2830EEFB4647A9E77E7FA9C450F0449A596749324A65A594887A12BCB9149919A4B0424B4D41B3BBD866966BF363/rotate')
        yield "Rotating IP..."
        if driver.current_url.__contains__("ban"):
            pass
        else:
            i += 1
            driver.close()
            j = 0
            while j < len(Name1):
                driver = get_chromedriver(use_proxy=True)
                write_image = open("reply_image.jpg", 'wb+')
                image_content = requests.get(Image_url1[j]).content
                write_image.write(image_content)
                write_image.close()
                yield "Creating New Reply for the previous thread...\n"
                yield str("Name : " + Name[i] + "\nOption : " + Option[i] + "\nComment : " + Comment[i]+"\n\n")
                driver.delete_all_cookies()
                driver.get(post_url)
                element_present = EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='delform']/div[1]/div[2]/div[1]/a"))
                WebDriverWait(driver, 10).until(element_present)

                # Posting a Reply to current opened thread!!
                driver.find_element_by_xpath("//*[@id='delform']/div[1]/div[2]/div[1]/a").click()
                driver.find_element_by_xpath("//*[@id='qrForm']/div[1]/input").send_keys(Name1[j])
                driver.find_element_by_xpath("//*[@id='qrEmail']").send_keys(Option1[j])
                driver.find_element_by_xpath("//*[@id='qrForm']/div[3]/textarea").send_keys(Comment1[j])
                driver.find_element_by_xpath("//*[@id='qrFile']").send_keys(Image_Path1)

                yield "Solving Captcha...\n"
                solver = TwoCaptcha('cd8bddb5facaad70dff1e10a22b60b0b')

                try:
                    result = solver.recaptcha(
                        sitekey='6Ldp2bsSAAAAAAJ5uyx_lx34lJeEpTLVkP5k04qc',
                        url=driver.current_url)

                except Exception as e:
                    sys.exit(e)

                else:
                    driver.execute_script(
                        'var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
                    driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]',
                                          str(result['code']))
                    driver.find_element_by_id("g-recaptcha-response").submit()

                try:
                    xpath = "/html/body/table/tbody/tr/td/span/a"
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
                    yield "Duplicate Post Exists Moving to Duplicate post\n"
                    driver.find_element_by_xpath(xpath).click()

                except:
                    pass

                yield "reply successfully posted...\n"
                driver.get(
                    'http://82.78.55.70:3158/8D5D2830EEFB4647A9E77E7FA9C450F0449A596749324A65A594887A12BCB9149919A4B0424B4D41B3BBD866966BF363/rotate')
                yield "Rotating IP..."
                if driver.current_url.__contains__("ban"):
                    pass
                else:
                    j += 1
                    driver.close()


@APP.route("/log_stream", methods=["GET"])
def stream():
    """returns logging information"""
    return Response(scrapper(), mimetype="text/plain", content_type="text/event-stream")


if __name__ == "__main__":
    APP.run(host="127.0.0.1", port=5000, debug=True, threaded=True)
