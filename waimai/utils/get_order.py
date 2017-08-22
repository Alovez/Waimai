import sqlite3
import time
from waimai.utils.get_menu import get_dish_info_by_id, get_shop_id_by_id

def get_cart(username):
    conn = sqlite3.connect('order_info')
    cursor = conn.execute("select DISH,SHOP,DISH_ID from order_list"
                          " where NAME='%s' and TIME='%s'" % (username, get_today_date()))
    dishes = []
    for row in cursor:
        dishes.append([row[0],row[1], row[2]])
    return dishes

def add_cart(username, dish_id):
    conn = sqlite3.connect('order_info')
    cursor = conn.execute("select name from sqlite_master where type='table' order by name;")
    is_table = False
    for row in cursor:
        if row[0] == "order_list":
            is_table = True
    if not is_table:
        conn.execute('''CREATE TABLE order_list
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT     NOT NULL,
       DISH           TEXT     NOT NULL,
       DISH_ID        TEXT     NOT NULL,
       SHOP           TEXT     NOT NULL,
       PRICE          TEXT     NOT NULL,
       TIME        TEXT     NOT NULL);''')
        conn.commit()
    id_cursor = conn.execute('select id from order_list order by ID desc limit 0,1')
    last_id = 0
    for row in id_cursor:
        last_id = row[0]
    info = get_dish_info_by_id(dish_id)
    conn.execute("insert into order_list (ID,NAME,DISH,DISH_ID,SHOP,PRICE,TIME) "
                 "values ('%s','%s','%s','%s','%s','%s','%s')" % (last_id + 1, username, info[0], dish_id, info[1], info[2], get_today_date()))
    conn.commit()
    conn.close()

def get_today_date():
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))

def get_order(shop_id):
    conn = sqlite3.connect('order_info')
    cursor = conn.execute("select DISH from order_list "
                          "where SHOP='%s' and TIME='%s'" % (shop_id, get_today_date()))
    dishes = {}
    for item in cursor:
        if item[0] in dishes.keys():
            dishes[item[0]] += 1
        else:
            dishes[item[0]] = 1
    conn.close()
    sorted_dishes = sorted(dishes.items(), key=lambda dishes:dishes[1])
    menu = []
    for item in sorted_dishes:
        menu.append([item[0], dishes[item[0]]])
    return menu

def get_order_by_name_date(username, start_date, end_date):
    conn = sqlite3.connect('order_info')
    if username == 'all':
        sql = "select DISH, PRICE from order_list " \
              "where datetime(TIME) > '%s' and datetime(TIME) <= datetime('%s','+1 day')"  % (start_date, end_date)
    else:
        sql = "select DISH, PRICE from order_list " \
              "where datetime(TIME) > '%s' and datetime(TIME) <= datetime('%s','+1 day')" \
              " and NAME='%s'" % (start_date, end_date, username)
    cursor = conn.execute(sql)
    dishes = []
    for item in cursor:
        dishes.append(item)
    conn.close()
    return dishes

def remove_order(username, dish_id, shop):
    conn = sqlite3.connect('order_info')
    cursor = conn.execute("select ID from order_list "
                          "where NAME='%s' and DISH_ID='%s' and SHOP='%s' and TIME='%s' limit 1" % (username, dish_id, shop, get_today_date()))
    for item in cursor:
        conn.execute('delete from order_list where ID=%s' % item[0])
        conn.commit()
    conn.close()