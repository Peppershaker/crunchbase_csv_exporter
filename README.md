Crunchbase CSV Exporter
======
**Crunchbase CSV Exporter** is a Python and Selenium based tool to export Crunchbase search results to a CSV file. It is intended for Pro trial account holders who does not get access to CB's native export to CSV functionality.

Note: This tool is not intended to be used as a scraper. As such, it makes no attempt to defeat capcha. Prior to logging in, you might have to manually solve the Hold-To-Confirm-Human capcha.

Usage
======
Start by populating your cb username and password in the cred.txt file in the project root directory

Next, build the search in CB and copy the url.

For a sigle search exporting the first 10 pages (500 records out of maximum of 1000) and save to mysearch.csv
```
$ ./python -m cbexporter -u URL -m 10 -f mysearch
```

Alternatively, you can supply a list of URLs and its corresponding csv file names to save the results to through the -M flag. Grabbing the first 500 records.
```
# ./python -m cbexporter -M urls.txt -m 10
```

The urls.txt file must follow the csv syntax of url,file_name
```
https://crunchbase.search.url,first_search
https://crunchbase.search.url2,second_search
```


## Version 
* Version 1.0

## Contact
* Homepage: victorxu.me
* e-mail: victor.c.xu@gmail.com
