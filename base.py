#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = ["Tuan Nguyen"]
__copyright__ = "Copyright 2018, Tuan Nguyen"
__credits__ = ["Tuan Nguyen"]
__license__ = "GPL"
__version__ = "1.0"
__status__ = "Production"
__author__ = "TuanNguyen"
__email__ = "etuannv@gmail.com"
__website__ = "https://webscrapingbox.com"



import os
import zipfile
import sys
import time
import csv
import os.path
import re
import random
import string
import logging
import requests as rq
from urllib.parse import urlparse
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import lxml.html
from xlrd import open_workbook
import configparser
import pickle

#=========================================== CONFIG GLOBAL =============================================================
#
## CONFIG LOG
#
globalLogLevel = logging.INFO
#globalLogLevel = logging.DEBUG
globalLogFormat = '%(asctime)s %(levelname)-4s %(filename)s:%(lineno)d %(message)s'
globalLogFile = 'app.log'
globalDateFmt = '%Y%m%d %H:%M:%S'

# Config loggin global
# set up logging to file - see previous section for more details
logging.basicConfig(level=globalLogLevel,
                    format=globalLogFormat,
                    datefmt=globalDateFmt,
                    filename=globalLogFile)

# Config log to console
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(globalLogLevel)
# set a format which is simpler for console use
formatter = logging.Formatter(globalLogFormat, datefmt=globalDateFmt)
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

#===========================================================================================================================
#COMMA
# CHECK IF FILE EXIST
# import os.path
# os.path.isfile(filePath) 

''' How to use
    config = MyConfigParser("configFilePath").as_dict()
    username = config.get("config_info","username")
    write to config: config.set(section, key, value)
    '''
class MyConfigParser:
    def __init__(self, path):
        self._file_path = path
        self._config = configparser.ConfigParser()
        self._config.sections()
        self._config.read(path)
        
    def get(self, section, key):
        return self._config[section][key]

    def set(self, section, key, value):
        with open (self._file_path, 'w') as f:
            self._config[section, key, value]
            self._config.write(f)



def extractEmails(url):
    response = rq.get(url)
    # print(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}",s))
    emails = re.findall(r'\b[\w.-]+?@\w+?\.\w+?\b', response.text)
    if emails:
        for email in emails:
            if email not in emails:
                emails.append(email)
    return emails

def getDomainFromUrl(url, domainNameOnly = False):
    try:
        parsed_uri = urlparse(url.lower())
        if domainNameOnly:
            domain = '{uri.netloc}'.format(uri=parsed_uri)
            domain = domain.replace('www.', '')
        else:
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain.replace(' ', '').replace('\n', '')
    except:
        logging.error("Fail to parse url %s: ", url)

def getCurrentDateString(format= '%Y-%m-%d %H:%M:%S'):
    ''' Get current date time string with format'''
    return time.strftime(format)

def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print ('Please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def readTextFileToList(filePath):
    ''' Read text file line by line to list '''
    if not os.path.isfile(filePath):
        logging.debug('File %s not found', filePath)
        return []
    
    with open(filePath, encoding="utf8") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content] 
    return content
            

def writeListToTextFile(list, filePath, mode='a'):
    ''' Write list to csv line by line '''
    with open(filePath, mode, encoding="utf8") as myfile:
        for item in list:
            myfile.write(str(item) +  '\n')

def writeListToCsvFile(data, filename, mode='a', header = 'None'):
    ''' Write list to csv file '''
    with open(filename, mode,newline="", encoding="utf8") as f:
        writer = csv.writer(f, delimiter=',')
        if header:
            writer.writerow(header)
        writer.writerows(data)

def readXlsFileToDict(filePath):
    CurrentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    if not os.path.isfile(filePath):
        filePath = os.path.join(CurrentPath, filePath)
    if not os.path.isfile(filePath):
        logging.info("readXlsFileToDict - File not found")
    book = open_workbook(filePath)
    sheet = book.sheet_by_index(0)
    # read header values into the list    
    keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
    dict_list = []
    for row_index in range(1, sheet.nrows):
        d = {keys[col_index]: sheet.cell(row_index, col_index).value 
            for col_index in range(sheet.ncols)}
        dict_list.append(d)

    return dict_list

def readCsvToList(filePath):
    ''' Read csv file to list'''
    if not os.path.isfile(filePath):
        logging.debug('File %s not found', filePath)
        return []
    with open(filePath, 'rb', encoding="utf8") as f:
        reader = csv.reader(f)
        return list(reader)

def readCsvToListDict(filePath):
    ''' Read csv file to list of dictionary'''
    if not os.path.isfile(filePath):
        logging.debug('File %s not found', filePath)
        return []

    result = []
    with open(filePath, newline='', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result.append(row)
    return result

# def writeDictToCSV(dict_data, csvFilePath, mode='w'):
#     ''' Write list of dictionary to csv file'''
#     try:
#         isExistFile = os.path.isfile(csvFilePath)
#         keys = dict_data[0].keys()
#         with open(csvFilePath, mode,newline="", encoding="utf8") as f:
#             dict_writer = csv.DictWriter(f, keys)
#             if ('a' in mode) and isExistFile:
#                 pass
#             else:
#                 dict_writer.writeheader()

#             dict_writer.writerows(dict_data)
#         return True
#     except IOError as e:
#         logging.error("I/O error) %s", e)
#         return False
#     return True  


def writeDictToCSV(dict_data, csvFilePath, mode='w', headers=None):
    ''' Write list of dictionary to csv file'''
    try:
        isExistFile = os.path.isfile(csvFilePath)
        if not headers:
            headers = []
            for key in dict_data[0]:
                headers.append(key)

        with open(csvFilePath, mode,newline="", encoding="utf8") as f:
            writer = csv.writer(f)
            if ('a' in mode) and isExistFile:
                pass
            else:
                writer.writerow(headers)

            for row in dict_data:
                targetrow = []
                for key in headers:
                    targetrow.append(row[key])
                writer.writerow(targetrow)

        return True
    except IOError as e:
        logging.error("I/O error) %s", e)
        return False
    return True 



def getListFileInPath(dataPath, endwith = None):
    ''' Get list file in folder recusive '''
    result = []
    try:
        for root,files in os.walk(dataPath):
            for file in files:
                if endwith:
                    if file.endswith(endwith):
                        filename = os.path.join(root, file)
                        result.append(filename)
                else:
                    filename = os.path.join(root, file)
                    result.append(filename)
        return result
    except Exception as e:
        logging.error("Some thing wrong %s", e)
        return result
def removeHtmlTag(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def createFolderIfNotExists(folder_path):
    ''' Create a new folder if not exists'''
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def removeMoneySymbol(value):
    trim = re.compile(r'[^\d.,]+')
    value = trim.sub('', value)
    value = value.replace(",","")
    return value

def getRandomString(n=20):
    ''' Return random string'''
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(n))

def getRandomID(size=6, chars=string.ascii_uppercase + string.digits):
    ''' Return random string with number'''
    return ''.join(random.choice(chars) for _ in range(size))

def getUrlExtension(url):
    ''' Get extension of url'''
    ext = url.rsplit('.', 1)[1]
    return ext
def isAvailableUrl(url):
    '''
        Checking is url working or not
    '''
    result = False
    try:
        web = urlopen(url, timeout = 3.0)
        if web:
            code = web.getcode()
            result = code == 200
        else:
            result = False
    except:
        result = False
    return result


class WebBrowser():
    """Class web browser"""
    def __init__(self, currentPath=None, driver = None, 
        timeout = 10, isDisableImage = False, 
        isDisableJavascript = False, downloadPath = None, 
        isMaximum = False, isHeadless = False, 
        proxyArgsList = None, proxyIpList=None, changeProxyTotal=None
        ):
        self._currentPath = currentPath
        self._driver = driver
        self._timeout = timeout
        self._isDisableImage = isDisableImage
        self._isDisableJavascript = isDisableJavascript
        self._downloadPath = downloadPath
        self._isHeadLess = isHeadless
        self._isMaximum = isMaximum
        self._proxyArgsList = proxyArgsList
        self._proxyIpList = proxyIpList
        self._changeProxyTotal = changeProxyTotal
        self._changeProxyCounter = 0

        self.startBrowser()

    def saveCookie(self, filePath):
        pickle.dump( self._driver.get_cookies() , open(filePath,"wb"))
    
    def loadCookie(self, filePath):
        if os.path.isfile(filePath):
            cookies = pickle.load(open(filePath, "rb"))
            for cookie in cookies:
                self._driver.add_cookie(cookie)

    def getCurrentUrl(self):
        return self._driver.current_url

    def getPageSource(self):
        return self._driver.page_source
    
    def findVisibleByXpath(self, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, locator))
            )
            return element
        except TimeoutException:
            logging.info(' Find by xpath not found : %s', locator)
            logging.debug('%s', TimeoutException)
            return None
        

    def findByXpath(self, locator, timeout = None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, locator))
            )
            return element
        except TimeoutException:
            logging.info(' Find by xpath not found : %s', locator)
            logging.debug('%s', TimeoutException)
            return None

    def findByXpathFromElement(self, sel, locator , timeout = None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(sel, timeout).until(
                EC.presence_of_element_located((By.XPATH, locator))
            )
            return element
        except TimeoutException:
            logging.info(' Find by xpath not found : %s', locator)
            logging.debug('%s', TimeoutException)
            return None

    def findAllByXpath(self, locator, timeout = None):
        ''' Get all items by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, locator)))
            return element
        except TimeoutException:
            logging.info(' Find by xpath not found : %s', locator)
            logging.debug('%s', TimeoutException)
            return []

    def findByClass(self, classname, timeout = None):
        ''' Get one item by class'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, classname)))
            return element
        except TimeoutException:
            logging.info(' Find by class not found : %s', classname)
            logging.debug('%s', TimeoutException)
            return None
            
    def findAllByClass(self, classname, timeout = None):
        ''' Get all item by class'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, classname)))
            return element
        except TimeoutException:
            logging.info(' Find by class not found : %s', classname)
            logging.debug('%s', TimeoutException)
            return []

    def isExistByXPath(self, locator, timeout = None):
        ''' Check if xpath is exists'''
        if not timeout:
            timeout = self._timeout
        try:
            WebDriverWait(self._driver, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException:
            return False
        return True

                    
    def restartDriver(self):
        ''' Restart the browser'''
        logging.info("Restart browser")
        if self._driver:
            self._driver.close()
        time.sleep(1)
        self.startBrowser()

    def exitDriver(self):
        ''' Exit the browser'''
        logging.info("Exit browser")
        if self._driver:
            self._driver.close()

    def getUrl(self, url):
        if self._changeProxyTotal:
            self._changeProxyCounter+=1
            if self._changeProxyCounter > self._changeProxyTotal:
                self.restartDriver()
                self._changeProxyCounter = 0
        ''' Get an url '''
        try:
            self._driver.get(url)
            return True
        except:
            logging.info("Fail to get %s", url)
            print("Unexpected error:", sys.exc_info()[0])

    def scrollInfinity(self, iretry = 15):
        # scroll infinity
        # define initial page height for 'while' loop
        last_height = self._driver.execute_script("return document.body.scrollHeight")
        logging.info("Scrolling down ... ")
        retry = iretry
        page = 0
        while True:
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = self._driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                retry -= 1
                if retry < 0:
                    break
            else:
                last_height = new_height
                page += 1
                logging.info("Scroll down page: %d", page)
                retry = iretry

    def clickElement(self, element, moveTimeout=1):
        try:
            ''' Click an element'''
            actions = ActionChains(self._driver)
            actions.move_to_element(element)
            time.sleep(moveTimeout)
            actions.click(element)
            actions.perform()
            return True
        except:
            logging.info("Can't click element")
            return False

    def sendKeys(self, key):
        ''' Send key to brower'''
        actions = ActionChains(self._driver)
        actions.send_keys(key)
        actions.perform()

    def getPlugin(self, proxy_host, proxy_port, proxy_user, proxy_pass):
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
        """ % (proxy_host, proxy_port, proxy_user, proxy_pass)
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        
        return pluginfile

    def startBrowser(self):
        ''' Start the browser'''
        logging.info("Start browser")

        chromeOptions = webdriver.ChromeOptions()

        if self._proxyArgsList:
            chromeOptions.add_extension(self.getPlugin(**random.choice(self._proxyArgsList)))
        
        if self._proxyIpList:
            chromeOptions.add_argument('--proxy-server={}'.format(random.choice(self._proxyIpList)))

        if self._isHeadLess:
            logging.info('Start browser in headless mode')
            chromeOptions.add_argument("--headless")
            chromeOptions.add_argument("--disable-gpu") 
        
        chromeOptions.add_argument("--no-experiments")
        chromeOptions.add_argument("--disable-translate")
        chromeOptions.add_argument("--disable-plugins")
        # chromeOptions.add_argument("--disable-extensions");
        chromeOptions.add_argument("--no-default-browser-check")
        chromeOptions.add_argument("--clear-token-service")
        chromeOptions.add_argument("--disable-default-apps")
        USER_AGENT_LIST = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
            'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10'
        ]
        chromeOptions.add_argument('user-agent='+USER_AGENT_LIST[random.randint(0,2)]+'')
        #chromeOptions.add_argument("--enable-logging");
        chromeOptions.add_argument("test-type")
        chromeOptions.add_argument('--log-level=3')
        chromeOptions.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36")

        if(self._isMaximum):
            chromeOptions.add_argument("start-maximized")
        
        prefs = { "profile.default_content_setting_values.notifications": 2 }
        
        if self._isDisableImage:
            prefs["profile.managed_default_content_settings.images"] = 2

        if self._isDisableJavascript:
            prefs["profile.managed_default_content_settings.javascript"] = 2
        
        chromeOptions.add_experimental_option("prefs",prefs)

        if self._downloadPath:
            prefs = {'plugins': {'plugins_disabled': ['Chrome PDF Viewer']}, 'download': {'default_directory': self._downloadPath, "directory_upgrade": True}}

        if os.name == 'posix':
            if self._currentPath:
                chromedriver=os.path.join(self._currentPath,"chromedriver")
            else:
                chromedriver='chromedriver'
        else:
            if self._currentPath:
                chromedriver=os.path.join(self._currentPath,"chromedriver.exe")
            else:
                chromedriver='chromedriver.exe'

        self._driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

        #driver.set_window_position(-10000,0)


    def tryClick(self, element, num = 10):
        ''' Try to click an element'''
        is_clicked = False
        step = 0
        while not is_clicked and step < num:
            try:
                self.clickElement(element)
                is_clicked = True
            except: 
                time.sleep(1)
                logging.info("try click %s", element)
                is_clicked = False
            step+=1
        
        return is_clicked

    
    def tryClickByXpath(self, locator, num = 10):
        ''' Try to click an element'''
        is_clicked = False
        step = 0
        while not is_clicked and step < num:
            element = self.findByXpath(locator)
            if element:
                is_clicked = self.clickElement(element, moveTimeout=3)
                if is_clicked:
                    return True
            # Else try click again    
            time.sleep(1)
            logging.info("try click %s", element)
            is_clicked = False
            step+=1
        
        return is_clicked