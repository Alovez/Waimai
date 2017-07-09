from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import time
import sqlite3

def get_menu_by_id(id):
    driver = webdriver.Chrome('D:\\UserApp\\chromedriver\\chromedriver.exe')
    time.sleep(2)
    driver.get('http://waimai.baidu.com/waimai/shop/' + id) #1430724018
    time.sleep(5)
    menu_list = driver.find_elements_by_css_selector('li.list-item')
    shop_name_element = driver.find_element_by_css_selector('section.breadcrumb>span')
    shop_name = shop_name_element.text
    is_table = False
    conn = sqlite3.connect('menu_list.db')
    cursor = conn.execute("select name from sqlite_master where type='table' order by name;")
    for row in cursor:
        if row[0] == "today_table":
            is_table = True
    if not is_table:
        conn.execute('''CREATE TABLE today_table
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       SHOP           TEXT     NOT NULL,
       SHOP_ID        TEXT     NOT NULL);''')
        conn.commit()
    else:
        conn.execute("DELETE FROM today_table")
        # conn.execute("update sqlite_sequence SET seq = 0 where name ='today_table'")
        conn.commit()
    item_id = 0
    for item in menu_list:
        n_pos = item.text.find('\n')
        name = item.text[:n_pos]
        conn.execute("INSERT INTO today_table (ID,NAME,SHOP,SHOP_ID) \
                    VALUES (%s, '%s', '%s', '%s' )" % (item_id, name, shop_name, id))
        item_id += 1
    conn.commit()
    conn.close()
    driver.close()

    # for item in menu_list:

    #     n_pos = item.text.find('\n')
    #     name_list.append(item.text[:n_pos])

def get_menu_from_db(shop_num):
    conn = sqlite3.connect('menu_list.db')
    cursor = conn.execute('select ID,NAME,SHOP FROM today_table')
    result = []
    for row in cursor:
        result.append(row)
    conn.close()
    return result