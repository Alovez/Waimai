from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import time
import sqlite3
from waimai.celery import app as celery_app
from waimai.constants import WeekDay
from datetime import datetime
from celery.schedules import crontab

@celery_app.task(name='get_today_menu')
def get_today_menu(weekday):
    weekday = datetime.today().weekday()
    conn = sqlite3.connect('menu_list.db')
    for shop_num in range(1, 4):
        cursor = conn.execute("select SHOP_ID,IS_MOBILE from weekday_shop where WEEKDAY='%s' and SHOP_NUM='%s'" % (weekday, shop_num))
        shop_id = ''
        is_mobile = ''
        for item in cursor:
            shop_id = item[0]
            is_mobile = (item[1] == '手机抓取')
        if shop_id != '':
            get_menu_by_id.delay(shop_num, shop_id, is_mobile)

@celery_app.task(name='get_menu_by_id')
def get_menu_by_id(shop_num,id,is_mobile=False):
    driver = webdriver.PhantomJS('/root/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
    time.sleep(2)
    if is_mobile:
        driver.get('http://waimai.baidu.com/mobile/waimai?qt=shopmenu&is_attr=1&shop_id=%s&address=龙冠商务中心-银座&lat=4850537.27&lng=12951506' % id)
        menu_list = driver.find_elements_by_css_selector('li.list-item.item-img')
        shop_name_element = driver.find_element_by_css_selector('div.top-div>div.center-title')
        shop_name = shop_name_element.text
    else:
        driver.get('http://waimai.baidu.com/waimai/shop/' + id) #1430724018
        menu_list = driver.find_elements_by_css_selector('li.list-item')
        shop_name_element = driver.find_element_by_css_selector('section.breadcrumb>span')
        shop_name = shop_name_element.text
    # TODO: 抓取图片
    conn = sqlite3.connect('menu_list.db')
    is_table = is_table_exist(conn, "today_table_%s"%shop_num)
    if not is_table:
        conn.execute('''CREATE TABLE today_table_%s
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       SHOP           TEXT     NOT NULL,
       SHOP_ID        TEXT     NOT NULL);''' % (shop_num))
        conn.commit()
    else:
        conn.execute("DELETE FROM today_table_%s"%shop_num)
        # conn.execute("update sqlite_sequence SET seq = 0 where name ='today_table'")
        conn.commit()
    item_id = 0
    for item in menu_list:
        n_pos = item.text.find('\n')
        name = item.text[:n_pos]
        conn.execute("INSERT INTO today_table_%s (ID,NAME,SHOP,SHOP_ID) \
                    VALUES (%s, '%s', '%s', '%s' )" % (shop_num ,item_id, name, shop_name, id))
        item_id += 1
    conn.commit()
    conn.close()
    driver.close()

    # for item in menu_list:

    #     n_pos = item.text.find('\n')
    #     name_list.append(item.text[:n_pos])

def get_menu_from_db(shop_num):
    conn = sqlite3.connect('menu_list.db')
    cursor = conn.execute('select ID,NAME,SHOP FROM today_table_%s'%shop_num)
    result = []
    for row in cursor:
        result.append(row)
    conn.close()
    return result

def get_shop(shop_id):
    conn = sqlite3.connect('menu_list.db')
    cursor = conn.execute("select SHOP from today_table_%s limit 1" % shop_id)
    result = ''
    for item in cursor:
        result = item[0]
    conn.close()
    return result

def change_shop_table(weekday, shop_num, shop_id, is_mobile):
    conn = sqlite3.connect('menu_list.db')
    is_table = is_table_exist(conn, "weekday_shop")
    if not is_table:
        conn.execute('''CREATE TABLE weekday_shop
           (ID INT PRIMARY KEY     NOT NULL,
           WEEKDAY           TEXT    NOT NULL,
           SHOP_NUM       TEXT     NOT NULL,
           SHOP_ID        TEXT     NOT NULL,
           IS_MOBILE      TEXT     NOT NULL);''')
        conn.commit()
    is_shop_exist = False
    cursor = conn.execute("select SHOP_ID from weekday_shop where WEEKDAY='%s' and SHOP_NUM='%s'" % (weekday, shop_num))
    for row in cursor:
        is_shop_exist = True
    if is_shop_exist:
        conn.execute("update weekday_shop set SHOP_ID='%s' "
                     "where WEEKDAY='%s' and SHOP_NUM='%s'" % (shop_id, weekday, shop_num))
    else:
        conn.execute("insert into weekday_shop (ID,WEEKDAY,SHOP_NUM,SHOP_ID,IS_MOBILE) "
                     "values ('%s','%s','%s','%s','%s')" % (weekday * 10 + shop_num,weekday, shop_num, shop_id, is_mobile))
    conn.commit()
    conn.close()

def get_shop_table():
    conn = sqlite3.connect('menu_list.db')
    if is_table_exist(conn, 'weekday_shop'):
        result = []
        for weekday in range(0, 5):
            weekday_list = []
            for shop_num in range(1, 4):
                cursor = conn.execute("select SHOP_ID, IS_MOBILE from weekday_shop "
                                      "where WEEKDAY='%s' and SHOP_NUM='%s'" % (weekday,shop_num))
                shop_id = ''
                is_mobile = ''
                for item in cursor:
                    shop_id = item[0]
                    is_mobile = item[1]
                if shop_id == '':
                    shop_id = '未设置'
                    is_mobile = 'N/A'
                weekday_list.append([shop_id, shop_num, is_mobile])
            result.append([WeekDay[weekday], weekday_list])
        return result
    else:
        result = []
        for weekday in range(0,5):
            weekday_list = []
            for shop_num in range(1,4):
               weekday_list.append(['未设置', shop_num, 'N/A'])
            result.append([WeekDay[weekday], weekday_list])
        return result

def is_table_exist(conn, table):
    cursor = conn.execute("select name from sqlite_master where type='table' order by name;")
    is_table = False
    for row in cursor:
        if row[0] == table:
            is_table = True
    return is_table
