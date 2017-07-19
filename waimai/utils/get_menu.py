from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import time
import sqlite3
from waimai.celery import app as celery_app


@celery_app.task(name='get_menu_by_id')
def get_menu_by_id(shop_num,id,is_mobile=False):
    driver = webdriver.Chrome('D:\\UserApp\\chromedriver\\chromedriver.exe')
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
    is_table = False
    conn = sqlite3.connect('menu_list.db')
    cursor = conn.execute("select name from sqlite_master where type='table' order by name;")
    for row in cursor:
        if row[0] == "today_table_%s"%shop_num:
            is_table = True
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