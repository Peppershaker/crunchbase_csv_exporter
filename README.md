![cb](https://user-images.githubusercontent.com/15576531/63644434-f77ca780-c6b6-11e9-9285-058c5b591d63.jpg)

Crunchbase CSV Exporter
======
**Crunchbase CSV Exporter** is a Python and Selenium based tool to export Crunchbase search results to CSV files. It is intended for Pro trial account holders who do not have access to CB's native export to CSV functionality.

Note: This tool is not intended to be used as a scraper. As such, it makes no attempt to defeat capcha. Prior to logging in, you might have to manually solve the Hold-To-Confirm-Human capcha.

Usage
======
```
usage: cbexporter.py [-h] [-u] [-m] [-f] [-M] [-c]

optional arguments:
  -h, --help            show this help message and exit
  -u , --url            url to scrape
  -m , --max-pages      maximum num of pages to scrape
  -f , --file-name      output csv file name
  -M , --multi-urls-from-file
                        read in a list of urls and desired csv save file names
                        from a csv file
  -c , --combine-csvs   combines all csv files in the scraped_data directory
                        and removed all duplicates
```


Example
======
### Exporting a single search
Start by populating your cb username and password in the cred.txt file in the project root directory

Next, build the search in CB and copy the url.

For a sigle search exporting the first 10 pages (500 records out of maximum of 1000) and save to mysearch.csv
```
$ ./python -m cbexporter -u URL -m 10 -f mysearch
```

### Exporting multiple searches to multiple CSVs
Alternatively, you can supply a list of URLs and its corresponding csv file names to save the results to through the -M flag. Grabbing the first 500 records.
```
$ ./python -m cbexporter -M urls.txt -m 10
```

The urls.txt file must follow the csv syntax of url,file_name
```
https://crunchbase.search.url1,first_search_csv_file_name
https://crunchbase.search.url2,second_search_csv_file_name
```

### Combine all exported CSVs into a single master CSV
To goal of this feature is to allow you to consolidate information on the same company gathered over multiple searches.

CB allows you to specify columns in search results. As such, this may lead to different searches having different columns. A common situation is as follows.

first.csv

| Company Name  | Mkt Cap | Col2 | Address |
| ------------- | ------------- | ------------- | ------------- |
| Facebook  |||1 Hacker Way|

second.csv

| Company Name  | Mkt Cap | Col2 | Address |
| ------------- | ------------- | ------------- | ------------- |
| Facebook  |500B|||

output

| Company Name  | Mkt Cap | Col2 | Address |
| ------------- | ------------- | ------------- | ------------- |
| Facebook  |500B||1 Hacker Way|

This could be accomplished with joins, but with multiple CSV files it becomes very involved and hard to automate.

Alternatively, you can use the `-c --combine-csvs` flag and specify the save file name. The tool will combine all csvs within the `scraped_data` folder

```
$ ./python -m cbexporter -c combined.csv
```

## Version 
* Version 1.0

## Contact
* Homepage: victorxu.me
* e-mail: victor.c.xu@gmail.com
