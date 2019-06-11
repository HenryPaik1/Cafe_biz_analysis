# get cafe from daum map
# get coordinate
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import re
import pickle
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Mongodb():
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://192.168.0.100:27017/")
    
    def _connect_db_col(self, db_name, col_name):
        self.db = self.client[db_name]
        self.collection = self.db[col_name]

    def mongo_insert_many(self, db_name, col_name, data):
        self._connect_db_col(db_name, col_name)
        r = self.collection.insert_many(data)
        print(r.inserted_ids)
    
    def drop(self, db_name, col_name):
        self._connect_db_col(db_name, col_name)
        self.collection.drop()
        print('droped')

mong_obj = Mongodb()

def make_dict(cafe_list):
    data_set = list()
    for elem in cafe_list:
        data = dict()
        data['name'] = elem.find_element_by_css_selector('a.link_name').text
        data['addr'] = elem.find_element_by_css_selector('div.addr > p:nth-child(1)').text
        data['rate'] = elem.find_element_by_css_selector('div.rating.clickArea > span.score .num').text
        data['category'] = elem.find_element_by_css_selector('div.head_item.clickArea > span').text
        data['num_review'] = elem.find_element_by_css_selector('div.rating.clickArea > a > em').text
        data_set.append(data)
    return data_set

def make_search_key(num):
    
    with open('resource/add_complete_{}.pickle'.format(num), 'rb') as f:
        a = pickle.load(f)
    for gu, road_ls in a.items():
        addr = [gu + ' ' + road + ' 카페' for road in road_ls]
    return addr

def get_cafe_from_daum(addr_pkl_num, db_name, db_col):
   
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    #options.add_argument('headless')
    #options.add_argument('window-size=1920x1080') #size조절도 가능(반응형 웹 크롤링할 때)

    driver = webdriver.Chrome("/home/ubuntu/chromedriver",options=options)
    url = 'https://map.kakao.com/'
    driver.get(url)

    # 안내메시지 클릭
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[10]/div/div[2]/a'))).click()
    # 안내메시지2 클릭
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dimmedLayer"]'))).click()
    
    addr_ls = make_search_key(addr_pkl_num)
    for search_key in addr_ls: 
        driver.find_element_by_xpath('//*[@id="search.keyword.query"]').\
        clear()
        time.sleep(0.5)
        key = search_key
        driver.find_element_by_xpath('//*[@id="search.keyword.query"]').\
        send_keys(key)

        # enter
        driver.find_element_by_xpath('//*[@id="search.keyword.query"]').\
        send_keys(Keys.RETURN)
        time.sleep(2)

        # 장소 더보기 클릭
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="info.search.place.more"]'))).click()
        except:
            pass 
        #q = list()
        # 한번 검색에 5*7 = 35페이지까지 제공
        for j in range(8):
        #for j in range(2):
            # page1 result
            time.sleep(2)
            cafe_list = driver.find_elements_by_xpath('//*[@id="info.search.place.list"]/li')
            d = make_dict(cafe_list)
            print('phaze: ', j+1, 'page ', 1)
            end_flag = False

            # element가 최대 5page까지만 배정
            for i in range(2, 5+1):
            #for i in range(2, 3):
                print('phaze: ', j+1, 'page ', i)
                xpath = '//*[@id="info.search.page.no{}"]'.format(i)
                try:
                    # 5page 미만이면 wait -> raise error -> 크롤링 end
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
                    time.sleep(1)
                    cafe_list = driver.find_elements_by_xpath('//*[@id="info.search.place.list"]/li')
                    d = d + make_dict(cafe_list)
                # 5page 미만 break for loop
                except:
                    end_flag = True
                    print('end')
                    break

            # insert data to mongodb
            # save unit: phaze
            mong_obj.mongo_insert_many(db_name, db_col, d)
            # 마지막 페이지인 경우 다음페이지 실행안함
            if end_flag:
                break

            # 다음 페이지
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="info.search.page.next"]'))).click()
        print('complete cafe save')
    driver.quit()

    
    
    
# test code    
#get_cafe_from_daum('강동구 진황도로 카페', 'test2', 'no')

def get_seoul_sales(db_name, col_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument('headless')
    #options.add_argument('window-size=1920x1080') #size조절도 가능(반응형 웹 크롤링할 때)

    driver = webdriver.Chrome(chrome_options=options)
    url = 'http://sg.sbiz.or.kr/index.sg?supDev=1#/statis/sales/'
    driver.get(url)

    #지역 콤보박스선택
    print('site loaded')
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="areaSelText"]'))).click()
    #서울선택
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="megaSelList"]/ul/li[2]/a'))).click()
    #확인

    driver.find_element_by_xpath('//*[@id="StatisLayerPopAddress"]/div/a[1]').click()

    #업종 콤보박스선택
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="upjongSelText"]'))).click()
    #음식선택
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="upjong1SelList"]/ul/li[2]/a'))).click()
    #카페선택
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="upjong2SelList"]/ul/li[12]/a'))).click()
    # 확인
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="LayerPopCategory"]/div/a[1]'))).click()

    # 현황보기
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="StatisCtrl"]/div[3]/div[2]/div[5]/a'))).click()

    # get list
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="resultList"]/table/tbody/tr[1]/td[1]/a/span'))).click()
    sales_list = driver.find_elements_by_xpath('//*[@id="resultList"]/table/tbody/tr')

    d = list()

    for ls in sales_list[1:]:
        data = dict()
        temp = ls.text.split(' ')
        data['gu'] = temp[0]
        data['18_1st_M_avg'] = temp[2]
        data['18_1st_M_per'] = temp[3]
        data['18_2nd_M_avg'] = temp[4]
        data['18_2nd_M_per'] = temp[5]
        d.append(data)
    # insert data
    mong_obj.mongo_insert_many(db_name, col_name, d)
    driver.quit()
    print('seoul_sales_complete')


#def get_coordinates(addr_ls):
def get_coordinates(addr_ls, db_name, col_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    #options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    url = 'https://www.google.com/maps'
    driver.get(url)
    d = list()
    for addr in addr_ls:
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
    
    mong_obj.mongo_insert_many(db_name, col_name, d)
    driver.quit()
    print('coordinates_complete')

# test code 
# get_coordinates(['가양동 카페', '문정동 카페'])
