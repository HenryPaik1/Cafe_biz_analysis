from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import time
import pickle
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
package_dir = os.path.dirname(os.path.abspath(__file__))

def get_coordinates(addr_ls, num):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument('headless')
    driver = webdriver.Chrome('/home/ubuntu/chromedriver', chrome_options=options)
    #driver = webdriver.Chrome(chrome_options=options)
    url = 'https://www.google.com/maps'
    driver.get(url)
    d = list()
    i = 0
    for addr in addr_ls:
        i += 1
        data = dict()
        # clear key
        driver.find_element_by_xpath('//*[@id="searchboxinput"]')\
        .clear()
        time.sleep(0.5)
        # send key
        driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys(addr)
        time.sleep(0.5)
        # enter
        driver.find_element_by_xpath('//*[@id="searchboxinput"]')\
        .send_keys(Keys.RETURN)
        time.sleep(3.5)
        # get value
        x, y = re.findall('\d+\.\d+', driver.current_url)[:2]
        data['addr'] = addr
        data['x'] = x
        data['y'] = y
        d.append(data)
        print(x, y)
        if i % 10 == 0:
            with open(package_dir + '/resource/cor_xy_{}.pickle'.format(num), 'wb') as f:
                pickle.dump(d, f)
                print(i, ': saved')
        
    

