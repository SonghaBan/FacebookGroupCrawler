#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 23:23:47 2020

@author: song-isong-i
"""

from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time,json,traceback

# =============================================================================
# CONFIG
# =============================================================================

EMAIL = '' #facebook email to sign in
PASSWORD = '' #facebook password
GROUPID = '' #facebook group id (check url of the group)

HEADLESS = False
chrome_dir = './chromedriver'


# =============================================================================
def get_html(url,sel=None):
    if not sel:
        response = requests.get(url)
        return response.text
    else:
        try:
            sel.get(url)
            sel.implicitly_wait(2)
            return sel.page_source
        except:
            return False
        
def new_browser():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
#    prefs = {"profile.managed_default_content_settings.images": 2}
#    options.add_experimental_option("prefs", prefs)
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0")
#    options.add_argument('--proxy-server={}://{}'.format(list(proxy.keys())[0],list(proxy.values())[0]))
    driver = webdriver.Chrome(chrome_dir, chrome_options=options)
    return driver



# =============================================================================
# posts
# =============================================================================

def get_post(p):
    author = p.find_element_by_class_name('fwb').text
    timestamp = int(p.find_element_by_class_name('livetimestamp').get_attribute('data-utime'))
    reg_dtime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    #reg_dtime = p.find_element_by_class_name('livetimestamp').get_attribute('title') #'2/24/20, 11:35 PM'
    try:
        p.find_element_by_class_name('see_more_link').click() #click see more
    except:
        pass
    content = p.find_element_by_class_name('userContent').text
    
    try:
        replies = p.find_elements_by_class_name('_3eol')
        for r in replies:
            r.click()
    except:
        pass
    try:
        replies = p.find_elements_by_class_name('_4sso')
        for r in replies:
            r.click()
    except:
        pass
    comments = p.find_elements_by_class_name('_4eek')
    
    r_comments = []
    for c in comments:
        r_comments.append(c.text)
    
    row = [author,reg_dtime,content,r_comments]
    time.sleep(0.5)
    return row

def write_file(data,idx,directory=None):
    filename = 'fb_results{}.json'.format(idx)
    if directory:
        filename = directory+'/'+filename
    with open(filename,'w') as f:
        json.dump(data,f)

def extract_hashtags(fdata):
    hashtags = []
    for d in fdata:
        if '#' in d[2]:
            tokens = d[2].split()
            for t in tokens:
                if t.startswith('#'):
                    print(t)
                    hashtags.append(t)
    return hashtags


def crawl(myidx=0,cnt=0):
    group_url = 'https://www.facebook.com/groups/{}/?sorting_setting=CHRONOLOGICAL'.format(GROUPID)
    driver = new_browser()
    driver.get('https://facebook.com')
    lf = driver.find_element_by_id('login_form')
    lf.find_element_by_name('email').send_keys(EMAIL)
    lf.find_element_by_name('pass').send_keys(PASSWORD)
    lf.find_element_by_id('loginbutton').click()

    driver.get(group_url)
    posts = driver.find_elements_by_class_name('userContentWrapper')

    allposts = []
    prev = 0
    while True:
        try:
            posts[-1].location_once_scrolled_into_view
            
            time.sleep(myidx/100)
            posts = driver.find_elements_by_class_name('userContentWrapper')
            print(len(posts))
            if len(posts) > prev:
                pass
            else:
                time.sleep(1)
                continue
            for p in posts[myidx:]:
                try:
                    r = get_post(p)
                    allposts.append(r)
                except:
                    r = ['','',p.text,[]]
                    # print(p.text)
                print('----',myidx)
                myidx += 1
            if len(allposts) > 1000:
                cnt+=1
                write_file(allposts,cnt)
            prev = len(posts)
        except KeyboardInterrupt:
            break
                
        except:
            print(traceback.format_exc())
            driver.get(group_url)
            time.sleep(2)

if __name__ == '__main__':
    crawl()

