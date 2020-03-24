# Web Crawler

A simple web crawler to fetch URLs and log the results.


## Steps to run the crawler

Install the pre-requisite libraries:
```
pip install requirements.txt
```

Run the program as:
```
python crawler.py <url beginning with http:// or https://>
```


## Terminating condition

The program will automatically terminate if there is no item in the crawler queue for a period of 10 seconds (the timeout is set to 10 seconds).

Alternatively, the user can give a KeyboardInterrupt (Ctrl + C).
This will cause the program to terminate after the thread pool shuts down gracefully.


## Running test cases

Run the test cases as:
```
python -m unittest test_crawler.TestCrawler
```