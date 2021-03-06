"""
Package Name: Crunchbase CSV Exporter
Description: This Python command line utility uses Selenium to save search results to a
            CSV file. It is NOT intended to be used as a comprehensive scraper and
            you will have to solve the capcha manually. It allows the user to save any
            search result for a maximum specified number of pages. Please refer to the
            help page for more usage details.
Date: Feb 2019
Author: Victor Xu
"""

import time
import sys
import argparse
import glob

import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from bs4 import BeautifulSoup


class Df_ext(pd.DataFrame):
    """Class extending pd.DataFrame with combine row functionality."""

    def combine_row(self):
        """
        Combines data for rows of the same key(company name)

        Example
        Facebook,na,1 hacker way,550B
        Facebook,15022,na,na

        Will be combined into a single row
        Facebook,15022,1 hacker way,550B
        """

        from tqdm import tqdm

        # Iterate through all unique keys
        keys = self.iloc[:, 0].unique()
        new_df_rows = []
        new_df_rows.append(self.reset_index(drop=True).columns.values)

        for key in tqdm(keys):
            filtered_df = self.loc[self.iloc[:, 0]
                                   == key, :].reset_index(drop=True)
            if filtered_df.shape[0] == 1:
                new_df_rows.append(filtered_df.values)

            else:
                reduced_row_data = []

                for col in filtered_df.columns:
                    # returns None if all rows are np.nan
                    valid_row_idx = filtered_df[col].first_valid_index()

                    if valid_row_idx is None:
                        # All columns are nans
                        valid_row_data_for_this_col = None

                    else:
                        valid_row_data_for_this_col = filtered_df.loc[valid_row_idx, col]

                    reduced_row_data.append(valid_row_data_for_this_col)

                new_df_rows.append(np.array(reduced_row_data).reshape(1, -1))

        new_df_rows = np.vstack(new_df_rows)
        combined = Df_ext(new_df_rows)
        combined.columns = [str(s).strip() for s in combined.iloc[0, :].values]
        combined = combined.iloc[1:, :]

        return combined


def init_driver():
    """Initialize the webdriver"""

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' + \
        '(KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options = Options()
    options.add_argument(f'user-agent={user_agent}')
    options.headless = False
    driver = webdriver.Chrome(
        r'C:\Program Files (x86)\chromedriver.exe',
        options=options)

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
            driver.find_element_by_xpath(
                '//*[@id="mat-input-1"]').send_keys(username)
            driver.find_element_by_xpath(
                '//*[@id="mat-input-2"]').send_keys(password)
            driver.find_element_by_xpath(
                '//*[@id="mat-tab-content-0-0"]' +
                '/div/login/form/div/button[2]').click()

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

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', metavar="", type=str, help='url to scrape')
    parser.add_argument(
        '-m',
        '--max-pages',
        metavar="",
        type=int,
        help='maximum num of pages to scrape')
    parser.add_argument(
        '-f',
        '--file-name',
        metavar="",
        type=str,
        default='results',
        help='output csv file name')
    parser.add_argument(
        '-M',
        '--multi-urls-from-file',
        metavar="",
        type=str,
        help='read in a list of urls and desired csv save file names from a csv file')
    parser.add_argument(
        '-c',
        '--combine-csvs',
        metavar="",
        type=str,
        help='combines all csv files in the scraped_data directory and removed all duplicates')
    args = parser.parse_args()

    return args


def process_html_for_data(rows_data, soup):
    """Scrapes html and returns data as a list of list, where each child list
    represents a row

    Args:
        rows_data: list
            List storing all search results. Each element within rows_data is a list containing
            results for a single row

        soup: BeautifulSoup
            a BeautifulSoup object representing the search result page

    Returns
        rows_data: list
            With new search results appended
    """

    rows = soup.find_all('div', class_='component--grid-row')

    for row in rows:
        cells = row.find_all('div', class_='component--grid-cell')
        single_row_data = []
        for cell in cells:
            single_row_data.append(cell.get_text().strip().replace('—', ''))

        rows_data.append(single_row_data)

    return rows_data


def process_html_for_col_name(rows_data, soup):
    """
    Gets the column names
    Args:
        rows_data: list
            List storing all search results. Each element within rows_data is a list containing
            results for a single row

        soup: BeautifulSoup
            a BeautifulSoup object representing the search result page

    Returns
        rows_data: list
            With new search results appended
    """

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


def scrape_all(driver, url, csv_file_name):
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

    save_to_csv(rows_data, csv_file_name)

    return


def save_to_csv(rows_data, csv_file_name):
    """Saves scraped data to csv"""

    columns = rows_data.pop(0)
    df = pd.DataFrame(rows_data, columns=columns)
    df = df.drop(df.columns[0], axis=1)
    df[df.columns[0]] = df[df.columns[0]].apply(
        lambda x: x.split('.')[1].strip())
    file_name = 'scraped_data\\' + csv_file_name + '.csv'
    df.to_csv(file_name)
    print("Wrote to", file_name)

    return


def combine_csvs(output_file_name):
    """
    Combines all CSVs into a single master csv using the Df_ext.combine_row() method.
    Each company in the output csv will retain all information from separate csvs.
    """

    # Get all file names in the scraped_data directory
    file_list = [pd.read_csv(filename)
                 for filename in glob.glob("scraped_data/*.csv")]
    df = pd.concat(file_list, axis=0, sort=False)
    df = df.drop('Unnamed: 0', axis=1)

    # # Remove duplicats and combine rows
    df = df.drop_duplicates()
    df_ext = Df_ext(df)
    df_ext = df_ext.combine_row()
    df_ext.to_csv(output_file_name)

    return


if __name__ == "__main__":
    # Parse args
    args = parse_all_args()

    # Combine csv
    if args.combine_csvs is not None:
        combine_csvs(args.combine_csvs)
        sys.exit(1)

    driver = init_driver()

    cred = load_user_pass()
    login(driver, cred)
    time.sleep(2)

    # Loading URL from file
    if args.multi_urls_from_file is not None:
        with open("urls.txt", 'r') as f:
            urls_file_names = f.readlines()

        for url_file_name in urls_file_names:
            url, file_name = url_file_name.split(',')
            file_name = file_name.strip()

            scrape_all(driver, url, file_name)

    # Loading URL from command line
    else:
        scrape_all(driver, args.url, args.file_name)

    driver.close()
