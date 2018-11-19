import time, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sys import platform as _platform
import getpass
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

MAX_SUBS = 1000000
MAX_CF_CONTEST_ID = 4444

SUBMISSION_URL = 'https://www.spoj.com/status/{UserID}/'

EXT = {'C++': 'cpp', 'C': 'c', 'Java': 'java', 'Python': 'py', 'Delphi': 'dpr', 'FPC': 'pas', 'C#': 'cs'}
EXT_keys = EXT.keys()

replacer = {'&quot;': '\"', '&gt;': '>', '&lt;': '<', '&amp;': '&', "&apos;": "'"}
keys = replacer.keys()

waitTime = 2


def GetPathOfChromeDriver():
    path = os.path.join(os.getcwd(), "chromedriver")
    if _platform == "linux" or _platform == "linux2":
        # linux
        path += "_linux"
    elif _platform == "darwin":
        # MAC OS X
        path += "_mac"
    elif _platform == "win32" or _platform == "win64":
        # Windows
        path += "_win"
    return path


driver = webdriver.Chrome(GetPathOfChromeDriver())
# driver.implicitly_wait(time_to_wait=30)


def get_ext(comp_lang):
    if comp_lang == "cpp":
        return comp_lang
    return "txt"
    for key in EXT_keys:
        if key in comp_lang:
            return EXT[key]
    return ""


def parse(source_code):
    for key in keys:
        source_code = source_code.replace(key, replacer[key])

    if source_code.startswith(" ") or source_code.startswith("  "):
        if not source_code.startswith("   ") and len(source_code) > 2:
            source_code = source_code.strip()
    return source_code


def SpojLogIn(user, passwd):
    login_site = "https://www.spoj.com/login/"
    driver.get(login_site)
    username = driver.find_element_by_id("inputUsername")
    password = driver.find_element_by_id("inputPassword")

    username.send_keys(user)
    password.send_keys(passwd)

    driver.find_element_by_class_name("btn-primary").click()
    # time.sleep(waitTime)

    elem = driver.find_elements_by_xpath('//*[@id="content"]/div/div/h3/span')
    if len(elem) > 0:
        print("Invalid Handle / Password")
        driver.quit()
        exit(0)
    # time.sleep(waitTime)


def FileNameParse(file):
    avoid = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    ret = ""
    for ch in file:
        if ch not in avoid:
            ret += ch
    return ret


def GetDownloadedFile(handle):
    path = os.path.join(handle, 'downloaded')
    if os.path.exists(path) == False:
        return []
    file = open(str(path), 'r')
    downloaded = file.readlines()
    downloaded = map(lambda s: s.strip(), downloaded)
    print("Existing: ", downloaded)
    return downloaded


def SetDownloadedFile(handle, st):
    path = os.path.join(handle, 'downloaded')
    file = open(str(path), 'a')
    file.write(st + "\n")
    file.close()


def main():
    handle = input("Enter your handle: ")
    print("Next step is password. ;) ")
    print("If you are afraid then check the code, You are smart enough to understand it")
    passwd = getpass.getpass("Enter your password: ")

    start_time = time.time()

    SpojLogIn(handle, passwd)

    if not os.path.exists(handle):
        os.makedirs(handle)

    driver.get(SUBMISSION_URL.format(UserID=handle))

    alreadyDownloaed = GetDownloadedFile(handle)
    downloaded = ""

    while True:
        submissions = driver.find_elements_by_class_name("kol1")

        for submission in submissions:
            WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.TAG_NAME, 'a')))
            tmp = submission.find_element_by_tag_name("a")
            if tmp.text in alreadyDownloaed:
                continue

            tmp.click()

            title = submission.find_element_by_class_name('sproblem').find_element_by_tag_name("a").text
            fileName = handle + "/" + FileNameParse(title) + "_" + tmp.text

            downloaded += tmp.text
            downloaded += "\n"

            time.sleep(waitTime)

            codes = driver.find_element_by_xpath('//*[@id="op_window2"]/div[2]/div/div[2]/pre/ol').text

            ext_name = driver.find_element_by_xpath('//*[@id="op_window2"]/div[2]/div/div[2]/pre')
            ext_name = ext_name.get_attribute('class')
            ext_name = get_ext(ext_name)
            fileName += "." + ext_name

            print(title)

            with open(fileName, "w") as fp:
                tmp = ""
                for codeLetter in codes:
                    if codeLetter == "\n":
                        codeLine = parse(tmp) + "\n"
                        fp.write(codeLine)
                        tmp = ""
                        continue
                    tmp += codeLetter

            WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                        '//*[@id="op_window2"]/div[2]/div/div[1]/button')))
            driver.find_element_by_xpath('//*[@id="op_window2"]/div[2]/div/div[1]/button').click()
            time.sleep(waitTime)

        next_page = driver.find_elements_by_xpath('//*[@id="content"]/div[7]/div/div/ul/li[8]/a')

        if len(next_page) == 0:
            break

        next_page[0].click()

    SetDownloadedFile(handle, downloaded)
    driver.quit()
    end_time = time.time()

    print("\n\nSuccessfully Completed 100%")
    print('Execution time %d seconds' % int(end_time - start_time))


if __name__ == "__main__":
    main()