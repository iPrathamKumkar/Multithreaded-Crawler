# Web Crawler

A simple web crawler to fetch URLs and log the results.


## Steps to run the crawler

Install the pre-requisite libraries:
```
pip install requirements.txt
```

Run the program as:
```
python crawler.py <URL>
```
The url must begin with 'http://' or 'https://'.<br>

The corresponding logs can be found in the 'crawler_logs.log' file.

## Terminating condition

The program will automatically terminate if there is no URL in the crawler queue for a period of 10 seconds.

Alternatively, the user can give a KeyboardInterrupt (Ctrl + C).
This will cause the program to terminate after the thread pool shuts down gracefully.


## Testing the crawler

For testing the crawler, an HTTP server is started at http://localhost:8080.<br>

This server hosts four HTML files (contained in the 'TestFiles' folder) with links pointing to each other.<br>
The server is shut down after running the tests.

## Running test cases

Make sure there is no process running at http://localhost:8080.<br>

Run the test cases as:
```
python -m unittest test_crawler.TestCrawler
```