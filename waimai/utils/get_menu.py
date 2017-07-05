from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import time

def get_menu_by_id(id):
    driver = webdriver.Chrome('D:\\UserApp\\chromedriver\\chromedriver.exe')
    time.sleep(2)
    driver.get('http://waimai.baidu.com/waimai/shop/' + id) #1430724018
    time.sleep(5)
    menu_list = driver.find_elements_by_css_selector('li.list-item')
    name_list = []
    for item in menu_list:
        n_pos = item.text.find('\n')
        name_list.append(item.text[:n_pos])
    return name_list