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
__website__ = "https://etuannv.com"


# Start import other
from base import *
import re
import requests
import csv
import shutil
from lxml import html
from lxml import etree
from urllib.parse import urljoin




def isBlocked(html_source):
    
    if "Access Denied" in html_source:
        return True
    else:
        return False
    

def getPropertyUrlFromPage(url):
    ''' Get all property url a page. Return list of dictionary'''
    is_next_page = False
    while not browser.getUrl(url):
        time.sleep(20)
        browser.getUrl(url)
        pass

    while isBlocked(browser.getPageSource()):
        logging.info('Proxy is blocked. Restarting the browser ...')
        browser.restartDriver()
        time.sleep(1)
        browser.getUrl(url)
    
    result = []  #{'category' :'-', 'url':'-',}

    #while not browser.isExistByXPath(".//*[@class='placard-details']//a", 2):
    #    logging.info("Waiting for page loading")
    #    pass
    
    root = lxml.html.fromstring(browser.getPageSource())

    
    # # cate
    # tag = root.xpath(".//li[@class='active']/a/text()")
    # if tag:
    #     cate = tag[0].strip()

    cate_text_list = root.xpath(".//h2/span/text()")
    ul_list = root.xpath(".//h2/span[1]/parent::h2/following::ul[1]")
    for i, cate in enumerate(cate_text_list):
        if 'See also' in cate or 'References' in cate:
            continue
        if len(ul_list) > i:
            li_list = ul_list[i].xpath(".//li")
            for li in li_list:
                url = li.xpath("./a[1]/@href")
                title = li.xpath("./a[1]/text()")
                description = " ".join(li.xpath('.//text()'))
                if description is not None:
                        description = description.strip()
                        description = description.split(" – ")[-1]
                        description = description.strip()

                if url and title:
                    
                    result.append({'category': cate, 'title': title[0], 'url': urljoin("https://en.wikipedia.org",url[0]), 'desc': description})        


        # if item is not None:
        #     result.append({'category': cate, 'url':  urljoin("http://www.game-debate.com",item.strip())})
    
    # Check next page
    # next_page = browser.findByXpath(".//a[@class='next_page']", 5)
    next_page = False
    if next_page:
        is_next_page = True
    

    return result, is_next_page

def getPropertyDetail(url, category, title, desc):

    
    result = {
                'url': "-",
                'category': "-",
                'title': "-",
                'desc': "-",
                'developer': "-",
                'developer_url': "-",
                'stable_release': "-",
                'supported_os': "-",
                'type': "-",
                'License': "-",
                
            }
    
    browser.getUrl(url)
    time.sleep(1)

    while isBlocked(browser.getPageSource()):
        logging.info('Proxy is blocked. Restarting the browser ...')
        browser.restartDriver()
        time.sleep(1)
        browser.getUrl(url)

    # retry = 3
    # while not browser.isExistByXPath(".//th[text()='Symbol']/following-sibling::td",10):
    #     time.sleep(1)
    #     retry -= 1
    #     logging.info("Refesh page")
    #     browser.getUrl(url)
    #     if retry < 0:
    #         return None

    

    result['url'] = browser.getCurrentUrl()
    result['category'] = category
    result['title'] = title
    result['desc'] = desc


    root = lxml.html.fromstring(browser.getPageSource())
    
    # developer
    tag = root.xpath(".//table[contains(@class,'infobox')][1]//th/a[@title='Software developer']/parent::th/following::td[1]//text()")
    if tag:
        result['developer'] = tag[0].strip()

    # developer_url
    tag = root.xpath(".//table[contains(@class,'infobox')][1]//th[text()='Website']/following::td[1]//a/@href")
    if tag:
        result['developer_url'] = tag[0].strip()

    # stable_release
    tag = root.xpath(".//table[contains(@class,'infobox')][1]//th/a[@title='Software release life cycle']/parent::th/following::td[1]//span[contains(@class,'published')]/text()")
    if tag:
        result['stable_release'] = tag[0].strip()
    else:
        tag = root.xpath(".//table[contains(@class,'infobox')][1]//th/a[@title='Software release life cycle']/parent::th/following::td[1]//text()")
        if tag:
            result['stable_release'] = tag[0].strip()

    # supported_os
    tag = root.xpath(".//table[contains(@class,'infobox')][1]//th/a[@title='Operating system']/parent::th/following::td[1]//text()")
    if tag:
        result['supported_os'] = ' '.join(filter(None, tag)).strip()
    else:
        tag = root.xpath(".//table[contains(@class,'infobox')][1]//th/a[@title='Computing platform']/parent::th/following::td[1]//text()")
        if tag:
            result['supported_os'] = ' '.join(filter(None, tag)).strip()


    # type
    tag = root.xpath(".//table[contains(@class,'infobox')][1]//th/a[@title='Software categories']/parent::th/following::td[1]//text()")
    if tag:
        result['type'] = ' '.join(filter(None, tag)).strip()
    
     # License
    tag = root.xpath(".//table[contains(@class,'infobox')][1]//th/a[@title='Software license']/parent::th/following::td[1]//text()")
    if tag:
        result['License'] = ' '.join(filter(None, tag)).strip()
    
    
    return result


def checkContinue():
    result = False
    if os.path.exists(TempPath):
        #ask for continue
        os.system('clear')
        print ("============== ATTENTION !!! The previous session has not finished ==============")
        print("\n")
        is_continue = confirm(prompt='DO YOU WANT CONTINUE THE PREVIOUS SESSION?', resp=True)
        if not is_continue:
            logging.info("You choice start new session")
            print("\n")
            print("\n")
            try:
                # Delete all file in temp folder
                shutil.rmtree(TempPath)
                # Delete previous result
                # if ResultPath:
                #     os.remove(ResultPath)
            except OSError:
                
                sys.exit("Error occur when delete temp folder")
            result = False
        else:
            logging.info("You choice continue previous session")
            print("\n")
            print("\n")
            result = True
    createFolderIfNotExists(TempPath)
    return result

def getCateUrls(url):
    browser.getUrl(url)
    tags = browser.findAllByXpath(".//*[@class='PopCategories']//a", 5)
    result = []
    if tags:
        for tag in tags:
            result.append(tag.get_attribute('href'))
        return result
    else:
        return None

def getFilterUrl(url):
    browser.getUrl(url)
    time.sleep(1)
    tag = browser.findByXpath(".//button[contains(@ng-click,'toggleAdvancedFilters')]")
    if tag is None:
        return None
    
    browser.clickElement(tag)
    time.sleep(1)
    tag = browser.findByXpath(".//form[@name='advancedFilter']//input[@name='PriceRangeMax']")
    if tag:
        tag.send_keys("750000")
        time.sleep(0.5)
    
    tag = browser.findByXpath(".//button[contains(@ng-click,'filteredSearch')]")
    if tag:
        browser.clickElement(tag)
    
    time.sleep(2)
    while browser.getCurrentUrl == url:
        logging.info("Wating for page load...")
        time.sleep(1)
    
    return browser.getCurrentUrl()


def main(argv):
    global browser, CurrentPath, TempPath, ConfigPath
    # CurrentPath = os.path.dirname(os.path.realpath(__file__))
    CurrentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    ConfigPath = os.path.join(CurrentPath, 'config.ini')
    TempPath = os.path.join(CurrentPath, 'temp')
    ResultPath = os.path.join(TempPath, "result_temp.csv")
    

    # ======= CHECK IF WANT TO CONTINUE PREVIOUS SESSION ========
    checkContinue()
    
    # READ PREVIOUS SESSION
    # Get done category url list
    done_cate_file_path = os.path.join(TempPath, "done_cate.txt")
    done_cate_list = readTextFileToList(done_cate_file_path)


    # get current page
    current_page_file_path = os.path.join(TempPath, "current_page.txt")
    current_page = readTextFileToList(current_page_file_path)
    if current_page:
        current_page = int(current_page[0]) + 1
    else:
        current_page = 1

    # proxy_list = []
    # for row in proxies.split():
    #     if row:
    #         proxy_list.append(row.strip())
    
    # # start browser
    # browser = WebBrowser(timeout = 10, isDisableImage = True, isDisableJavascript = True, proxyIpList=proxy_list, changeProxyTotal=50)

    input_file_path = os.path.join(CurrentPath, "input.txt")
    browser = WebBrowser(timeout = 10, isDisableImage = True, isDisableJavascript = True, changeProxyTotal=500)
    # ====== STEP 1: GET ALL PROPERTIES URL FOR A CATEGORY =======
    logging.info("=============== STEP 1: COLLECT PROPERTIES URL =============== ")

    # cate links
    
    cate_links = readTextFileToList(input_file_path)

    # File path to save property url
    property_urls_file_path = os.path.join(TempPath, "property_urls.csv") # category | url
    total = len(cate_links)
    counter = 0
    for link in cate_links:
        counter += 1
        logging.info('Process %d/%d urls', counter, total)
        # Check if link done
        if link in done_cate_list:
            # logging.info("The category link is done: %s", link)
            logging.info('Done %d/%d urls', counter, total)
            continue

        while  True:
            
            url = link.format(12*(current_page-1))
            logging.info("Page %d at url: %s", current_page, url)
            # Get from current page
            result, is_next_page = getPropertyUrlFromPage(url)
            if result:
                # Write result to file
                writeDictToCSV(result, property_urls_file_path, 'a')
                # Save current page status
                writeListToTextFile([current_page], current_page_file_path, 'w')
                # Increase page
                current_page += 1
            
            if not result or not is_next_page:
                current_page = 1
                # Save current page status
                writeListToTextFile([current_page], current_page_file_path, 'w')
                # Save this link done
                writeListToTextFile([link], done_cate_file_path, 'a')
                # Finish this link
                break



    # ======= STEP 2: GO TO EACH URL TO GET PROPERTIES DETAIL ========
    logging.info("=============== STEP 2: COLLECT PROPERTIES DETAIL =============== ")

    # get done properties list
    done_pro_file_path = os.path.join(TempPath, "done_pro.txt")
    done_pro_list = readTextFileToList(done_pro_file_path)

    p_link_list = readCsvToListDict(property_urls_file_path) # category | url
    total = len(p_link_list)
    counter = 0
    for item in p_link_list:
        
        counter += 1
        logging.info('Process %d/%d properties', counter, total)
        if item['url'] in done_pro_list:
            #logging.info("The property link is done: %s", item['url'])
            logging.info('Done %d/%d properties', counter, total)
            continue
        result = getPropertyDetail(item['url'], item['category'], item['title'], item['desc'])
        if result:
            header = [
                'url',
                'category',
                'title',
                'desc',
                'developer',
                'developer_url',
                'stable_release',
                'supported_os',
                'type',
                'License',
                ]
            # Write result to file
            writeDictToCSV([result], ResultPath, 'a', header)

            # Save link done
            writeListToTextFile([item['url']], done_pro_file_path, 'a')
        else:
            logging.info("Fail or not to get: %s", item['url'])
        

    
    # ========= POST DONE ===========
    # Move result file to project directory
    if os.path.isfile(ResultPath):
        result_folder = os.path.join(CurrentPath, "result")
        createFolderIfNotExists(result_folder)
        final_result_file_path = os.path.join(result_folder, "result_at_" + getCurrentDateString("%Y%m%d_%H%M%S") + ".csv")
        shutil.move(ResultPath, final_result_file_path)
    # Rename temp folder
    if os.path.exists(TempPath):
        temp_done = os.path.join(CurrentPath, "temp_at_" + getCurrentDateString("%Y%m%d_%H%M%S"))
        shutil.move(TempPath, temp_done)
        #shutil.rmtree(TempPath)

    browser.exitDriver()


if __name__ == "__main__":
    main(sys.argv)
    logging.info("DONE !!! etuannv@gmail.com ;)")