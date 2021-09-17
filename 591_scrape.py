# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 11:26:05 2021

@author: User
"""

#591租屋

from selenium import webdriver
from shutil import which
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options


# options = Options()
# options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗
chrome_path = which("chromedriver")
driver = webdriver.Chrome(executable_path = chrome_path)
driver.get("https://rent.591.com.tw/?kind=0&region=1")
driver.save_screenshot("C://Users//User//Documents//Data Processing//2021_Zita_bs4//591_front_page.png")


#Click off popup
try:
    close = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="area-box-close"]')))
    close.click()
    time.sleep(2)
    close2 = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[7]/a[1]')))
    close2.click()
    # temporarily ignore位置存取
except:
    pass


#My Conditions
htype = driver.find_element_by_xpath('//*[@id="search-kind"]/span[3]').click()
time.sleep(1)
rent = driver.find_element_by_xpath('//*[@id="search-price"]/span[4]').click()
region = driver.find_element_by_xpath('//*[@id="search-location"]/span[2]').click()
region_selected = driver.find_element_by_xpath('//*[@id="optionBox"]/li[2]/label').click()
not_top_floor = driver.find_element_by_xpath('//*[@id="container"]/section[3]/section/div[6]/ul/li[2]/label').click()
posted_by_lanlord = driver.find_element_by_xpath('//*[@id="container"]/section[3]/section/div[6]/ul/li[3]/label/input').click()
device = driver.find_element_by_xpath('//*[@id="rentOption"]/button').click()
time.sleep(2)
#必須要往下滑，選單內容才可以顯示的出
driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
device_air_conditioner = driver.find_element_by_xpath('//*[@id="rentOption"]/ul/li[2]/a/label/em').click()
device_hot_water = driver.find_element_by_xpath('//*[@id="rentOption"]/ul/li[4]/a/label/em').click()
device_washer = driver.find_element_by_xpath('//*[@id="rentOption"]/ul/li[8]/a/label/em').click()
time.sleep(3)


#Sort ascendingly by rent price
sort_btn = driver.find_element_by_xpath('//*[@id="container"]/section[5]/div/div[1]/div[3]/div[3]/div[4]').click()

import pandas as pd
from bs4 import BeautifulSoup
rent_df = pd.DataFrame({'Title':[], 'Rent_space':[], 'Rent_floor':[], 'Address':[], 'Update_time':[], 'Price':[], 'Link':[], 'Image':[]})
count = 0
page = 0
while True:
    soup = BeautifulSoup(driver.page_source, "lxml")
    rent_list = soup.select('ul.listInfo.clearfix.j-house')
    current = int(soup.select('span.pageCurrent')[0].text)   #591不知為何無法停止scrape next_page，只好用這個方法
    if page == current:
        break
    for house in rent_list:
        try:
            title = house.select('h3 > a')[0].text.strip()
            infos = house.select('p:nth-child(2)')[0].text.replace('\n', '').strip().split('\xa0\xa0|\xa0\xa0')
            space =infos[1].strip()
            floor = infos[2].strip()
            add = house.select('p:nth-child(3) > em')[0].text
            update = house.select('p:nth-child(4) > em:nth-child(2)')[0].text
            price = int(house.select('div.price i')[0].text.replace(",",'').strip())
            link = 'https:'+ house.select('h3 > a')[0].get("href").strip()
            img = house.select('li.pull-left.imageBox > img')[0].get("data-original")
            if "https" not in img:
                img = 'https' + img
            print(title, space, floor, add, update, price, link, img)
            count += 1
        except:
            pass
        rent_df = rent_df.append({'Title':title, 'Rent_space':space, 'Rent_floor':floor, 'Address':add, 'Update_time':update, 'Price':price, 'Link':link, 'Image':img}, ignore_index=True)
    print(count)
    print(page, current)
    
    try:
        next_page = driver.find_element_by_class_name('pageNext')
        print(next_page)
        next_page.click()
        time.sleep(3)
        count = 0
        page += 1
    except:
        break
  


rent_df.to_csv("C://Users//User//Documents//Data Processing//2021_Zita_bs4//rent.csv", encoding = 'utf_8_sig', line_terminator = "\n")


##########################
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import os
import datetime
today = str(datetime.date.today())

#Infos
sender = 'webscrapingprac@gmail.com'
receiver = 'dewboiler2@gmail.com'

#Create Message
msg = MIMEMultipart()
msg['Subject'] = 'New Rents on 591'  #標題
msg['From'] = sender
msg['To'] = ','.join(receiver)  #可以有多個receiver
text = '''591 Rent Scraping.
Conditions:house_type, rent_price, region, not_top_floor, posted_by_lanlord.
Device: air_conditioner, hotwater, washer.
'''
msg.attach(MIMEText(text, 'plain'))

#Adds a csv file as an attachment to the email
part = MIMEBase('application', 'octet-stream')
part.set_payload(open('C://Users//User//Documents//Data Processing//2021_Zita_bs4//rent.csv', 'rb').read())  #打開+閱讀目標csv
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(f'{today}_rent591.csv'))   #filename記得使用os.path.basename，才抓得到檔案!
msg.attach(part)

#Will login to your email and actually send the message above to the receiver
s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
s.login(user = 'webscrapingprac@gmail.com', password = 'tubecity0212')
s.sendmail(sender, receiver, msg.as_string())
s.quit()
driver.close()


'''
結論: 
    1. 純文字檔不是很實用
    2. 找房子其實最重要的是「圖片」
下一個目標: 
    抓資料
    抓圖片
    推撥到line上
'''

