import time
import sys
import argparse

import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from bs4 import BeautifulSoup

def init_driver():
    """Initialize the webdriver"""
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options = Options()
    options.add_argument(f'user-agent={user_agent}')
    options.headless = False
    driver = webdriver.Chrome('C:\Program Files (x86)\chromedriver.exe', options=options)

    return driver


def login(driver, cred):
    """Logs in and saves the cookies"""

    driver.implicitly_wait(5)
    username = cred[0]
    password = cred[1]

    logged_in = False
    while not logged_in:
        try:
            driver.get("https://www.crunchbase.com/login")
            driver.find_element_by_xpath('//*[@id="mat-input-1"]').send_keys(username)
            driver.find_element_by_xpath('//*[@id="mat-input-2"]').send_keys(password)
            driver.find_element_by_xpath('//*[@id="mat-tab-content-0-0"]/div/login/form/div/button[2]').click()

            time.sleep(3)
            check_recapcha(driver)
            logged_in = True
            print("Successfully logged in")
        
        except (StaleElementReferenceException, NoSuchElementException):
            check_recapcha(driver)

    return


def load_user_pass():
    """Read username and password from file"""

    with open('cred.txt', 'r') as f:
        user_name = f.readline()
        password = f.readline()
    
    return (user_name, password)


def parse_all_args():
    """Parses arguments and returns it"""

    parser=argparse.ArgumentParser()
    parser.add_argument('-l', '--login', action='store_true',  help='login to CB')
    parser.add_argument('-u', '--url', type=str, help='url to scrape')
    parser.add_argument('-m', '--max-pages', type=int, help='maximum num of pages to scrape')
    parser.add_argument('-f', '--file-name', type=str, 
                                default='results', help='output csv file name')
    args = parser.parse_args()

    return args


def process_html_for_data(rows_data, soup):
    """Scrapes html and returns data as a list of list, where each child list 
    represents a row"""

    rows = soup.find_all('div', class_='component--grid-row')

    for row in rows:
        cells = row.find_all('div', class_='component--grid-cell')
        single_row_data = []
        for cell in cells:
            single_row_data.append(cell.get_text().strip().replace('—',''))
    
        rows_data.append(single_row_data)

    return rows_data


def process_html_for_col_name(rows_data, soup):
    """Gets the column names"""

    cols = soup.find_all('grid-column-header')

    col_names = []
    for col in cols:
        col_names.append(col.get_text())
    
    rows_data.append(col_names)

    return rows_data


def check_recapcha(driver):
    """Checks and solves recapcha"""

    try:
        # This currently do not work. You have to manually press the check
        recapcha_elem = driver.find_element_by_id('px-captcha')
        action = ActionChains(driver)
        action.move_by_offset(30, 15).click_and_hold().perform()
        time.sleep(7.5)
        action.release().perform()

        solved = True
        return solved

    except NoSuchElementException:
        return None



def parse_to_soup_obj(driver):
    """
    Returns the current page as a soup object
    """
    
    html_element = driver.find_element_by_xpath("//*")
    html_string = html_element.get_attribute("outerHTML")

    return BeautifulSoup(html_string, 'html.parser')



def scrape_all(driver, url):
    """Scrape current url and returns results in a list"""

    rows_data = []
    not_finished = True

    i = 1
    driver.get(url)

    # btn for next page
    btn_xpath = "/html/body/chrome/div/mat-sidenav-container" + \
        "/mat-sidenav-content/search/page-layout/div/div/form" + \
            "/div[2]/results/div/div/div[1]/div/results-info/h3/a[2]"

    while not_finished:
        # Just checks and waits 10 seconds for now. Have to manually solve if
        # capcha is present
        check_recapcha(driver)

        page_soup = parse_to_soup_obj(driver) 

        if i == 1:
            process_html_for_col_name(rows_data, page_soup)
        
        process_html_for_data(rows_data, page_soup)

        # grab next page url
        try:
            print("Next page")
            url = driver.find_element_by_xpath(btn_xpath).click()
        
        except (NoSuchElementException, ElementClickInterceptedException):
            not_finished = False

        if i > args.max_pages:
            print("Reached max pages.")
            not_finished = False
        
        i += 1

    save_to_csv(rows_data)

    return


def save_to_csv(rows_data):
    """Saves scraped data to csv"""

    columns = rows_data.pop(0)
    df =  pd.DataFrame(rows_data, columns=columns)
    df = df.drop(df.columns[0], axis=1)
    df[df.columns[0]] = df[df.columns[0]].apply(lambda x: x.split('.')[1].strip()) 
    file_name = 'scraped_data\\' + args.file_name + '.csv'
    df.to_csv(file_name)
    print("Wrote to", file_name)

    return


if __name__ == "__main__":
    driver = init_driver()

    # Parse args
    args = parse_all_args()

    cred = load_user_pass()
    login(driver, cred)
    time.sleep(2)

    scrape_all(driver, args.url)
    
    driver.close()