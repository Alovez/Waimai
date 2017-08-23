from selenium import webdriver
import signal
from selenium.webdriver.common.keys import Keys
import selenium
import urllib.request
import urllib.parse
import bs4
import time
import sqlite3
from waimai.celery import app as celery_app
from waimai.constants import WeekDay
from datetime import datetime
import re
import json
from waimai.settings import WEB_DRIVER_ENGINE, CHROME_PATH, PHANTOMJS_PATH, CRAWL_DRIVER


@celery_app.task(name='get_today_menu')
def get_today_menu(weekday):
    weekday = datetime.today().weekday()
    conn = sqlite3.connect('menu_list.db')
    for shop_num in range(1, 4):
        cursor = conn.execute(
            "select SHOP_ID,IS_MOBILE from weekday_shop where WEEKDAY='%s' and SHOP_NUM='%s'" % (weekday, shop_num))
        shop_id = ''
        is_mobile = ''
        for item in cursor:
            shop_id = item[0]
            is_mobile = (item[1] == '手机抓取')
        if shop_id != '':
            get_menu_by_id.delay(shop_num, shop_id, is_mobile)


@celery_app.task(name='get_menu_by_id')
def get_menu_by_id(shop_num, id, is_mobile=False):
    if CRAWL_DRIVER == 'selenium':
        if WEB_DRIVER_ENGINE == 'chrome':
            driver = webdriver.Chrome(CHROME_PATH)
        else:
            driver = webdriver.PhantomJS(PHANTOMJS_PATH)
        time.sleep(2)
        if is_mobile:
            driver.get(
                'http://waimai.baidu.com/mobile/waimai?qt=shopmenu&is_attr=1&shop_id=%s&address=龙冠商务中心-银座&lat=4850537.27&lng=12951506' % id)
            list_items = driver.find_elements_by_css_selector('#shopmenu-list li.list-item')
            menu_list = []
            for item in list_items:
                dish_id = json.loads(item.get_attribute('data-item'))['itemId']
                img_src = item.find_element_by_css_selector('div.lazy-div').get_attribute('data-url').replace('%', '%%')
                dish_name = item.find_element_by_css_selector('h4.title').text
                dish_price = item.find_element_by_css_selector('p.price').text
                if [dish_id, dish_name, img_src, dish_price] not in menu_list:
                    menu_list.append([dish_id, dish_name, img_src, dish_price])
            shop_name_element = driver.find_element_by_css_selector('div.top-div>div.center-title')
            shop_name = shop_name_element.text
        else:
            driver.get('http://waimai.baidu.com/waimai/shop/%s' % id)  # 1430724018 1847973726 1438078393
            list_items = driver.find_elements_by_css_selector('section.menu-list li.list-item')
            menu_list = []
            for menu_item in list_items:
                dish_id = menu_item.get_attribute('data-sid').replace('item_', '')
                try:
                    img_item = menu_item.find_element_by_css_selector('div.bg-img')
                    src_match = re.findall('background: url\(\"(.*?)\"\)', img_item.get_attribute('style'), re.S)
                    img_src = src_match[0].strip()
                except:
                    img_src = '暂无图片'
                dish_name = menu_item.find_element_by_css_selector('div.info.fl>h3').text
                dish_price = menu_item.find_element_by_css_selector('div.info.fl strong').text
                if [dish_id, dish_name, img_src, dish_price] not in menu_list:
                    menu_list.append([dish_id, dish_name, img_src, dish_price])
            shop_name_element = driver.find_element_by_css_selector('section.breadcrumb>span')
            shop_name = shop_name_element.text
        if WEB_DRIVER_ENGINE == 'chrome':
            driver.close()
        else:
            driver.service.process.send_signal(signal.SIGTERM)
            driver.quit()
        driver.close()
    else:
        if is_mobile:
            chinese = '龙冠商务中心-银座'
            chinese = urllib.parse.quote(chinese)
            url = u'http://waimai.baidu.com/mobile/waimai?qt=shopmenu&is_attr=1&shop_id=%s&address=%s&lat=4850537.27&lng=12951506' % (
                id, chinese)
            data = urllib.request.urlopen(url).read()
            data = data.decode('utf-8')
            soup = bs4.BeautifulSoup(data, 'html5lib')
            dish_li = soup.select('#shopmenu-list li.list-item')
            shop_name = soup.select('div.top-div div.center-title')[0].string
            menu_list = []
            for li in dish_li:
                dish_id = json.loads(li['data-item'])['itemId']
                dish_name = li.select('h4.title')[0].string
                try:
                    img_src = li.select('div.lazy-div')[0]['data-url'].replace('%', '%%')
                except:
                    img_src = '暂无图片'
                dish_price = li.select('p.price')[0].string
                if len(li.select('.item-empty')) != 0:
                    continue
                if [dish_id, dish_name, img_src, dish_price] not in menu_list:
                    menu_list.append([dish_id, dish_name, img_src, dish_price])
        else:
            url = 'http://waimai.baidu.com/waimai/shop/%s' % id
            data = urllib.request.urlopen(url).read()
            data = data.decode('utf-8')
            soup = bs4.BeautifulSoup(data, 'html5lib')
            dish_li = soup.select('section.menu-list li')
            menu_list = []
            for li in dish_li:
                dish_id = li['data-sid'].replace('item_', '')
                dish_name = li.select('div.info h3')[0].string
                try:
                    img_item = li.select('div.bg-img')[0]['style']
                    src_match = re.findall('background: url\((.*?)\)', img_item, re.S)
                    img_src = src_match[0].strip()
                except:
                    img_src = '暂无图片'
                dish_price = li.select('div.info strong')[0].string
                if len(li.select('div.info .m-break')) != 0:
                    continue
                if [dish_id, dish_name, img_src, dish_price] not in menu_list:
                    menu_list.append([dish_id, dish_name, img_src, dish_price])
            shop_name = soup.select('section.breadcrumb span')[0].string
    conn = sqlite3.connect('menu_list.db')
    is_table = is_table_exist(conn, "today_table_%s" % shop_num)
    if not is_table:
        conn.execute('''CREATE TABLE today_table_%s
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       DISH_ID        TEXT    NOT NULL,
       DISH_PRICE     TEXT    NOT_NULL,
       DISH_IMG       TEXT,
       SHOP           TEXT     NOT NULL,
       SHOP_ID        TEXT     NOT NULL);''' % (shop_num))
        conn.commit()
    else:
        conn.execute("DELETE FROM today_table_%s" % shop_num)
        # conn.execute("update sqlite_sequence SET seq = 0 where name ='today_table'")
        conn.commit()
    item_id = 0
    for item in menu_list:
        conn.execute("INSERT INTO today_table_%s (ID,SHOP_ID,DISH_ID,NAME,DISH_IMG,DISH_PRICE,SHOP) \
                    VALUES (%s, '%s', '%s', '%s', '%s', '%s','%s')" % (
        shop_num, item_id, id, item[0], item[1], item[2], item[3], shop_name))
        item_id += 1
    conn.commit()
    conn.close()

    # for item in menu_list:

    #     n_pos = item.text.find('\n')
    #     name_list.append(item.text[:n_pos])


def get_menu_from_db(shop_num):
    conn = sqlite3.connect('menu_list.db')
    cursor = conn.execute('select ID,NAME,SHOP,DISH_PRICE,DISH_IMG,DISH_ID FROM today_table_%s' % shop_num)
    result = []
    for row in cursor:
        row_list = list(row)
        row_list[4] = row_list[4].replace('%%', '%')
        result.append(row_list)
    conn.close()
    return result


def get_dish_info_by_id(dish_id):
    conn = sqlite3.connect('menu_list.db')
    dish_name = '未知菜品，请确认后重试'
    price = '价格暂缺'
    shop_num = -1
    for i in range(1, 4):
        cursor = conn.execute("select NAME, DISH_PRICE from today_table_%s where DISH_ID='%s'" % (i, dish_id))
        for item in cursor:
            if len(item):
                dish_name = item[0]
                price = item[1]
                shop_num = i
    conn.close()
    return [dish_name, shop_num, price]


def get_shop_id_by_id(dish_id):
    conn = sqlite3.connect('menu_list.db')
    shop_id = '未知饭店，请确认后重试'
    for i in range(1, 4):
        cursor = conn.execute("select SHOP_ID from today_table_%s where DISH_ID='%s'" % (i, dish_id))
        for item in cursor:
            if len(item):
                shop_id = item[0]
    conn.close()
    return shop_id


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
        conn.execute("update weekday_shop set IS_MOBILE='%s' "
                     "where WEEKDAY='%s' and SHOP_NUM='%s'" % (is_mobile, weekday, shop_num))
    else:
        conn.execute("insert into weekday_shop (ID,WEEKDAY,SHOP_NUM,SHOP_ID,IS_MOBILE) "
                     "values ('%s','%s','%s','%s','%s')" % (
                     weekday + shop_num, weekday, shop_num, shop_id, is_mobile))
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
                                      "where WEEKDAY='%s' and SHOP_NUM='%s'" % (weekday, shop_num))
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
        for weekday in range(0, 5):
            weekday_list = []
            for shop_num in range(1, 4):
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
