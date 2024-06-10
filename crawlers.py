# -*- coding: utf-8 -*-
import numpy as np 
import pandas as pd
import random 
import urllib 
import requests
import time
import os
import re
from bs4 import BeautifulSoup
import threading
import queue
import sys

class IEPCrawler:
    def __init__(self, base_url='iep.utm.edu', num_threads=2, max_retry=5, max_timeout=10):
        """
        A simple crawler for the Internet Encyclopedia of Philosophy (IEP) website.

        Args:
            base_url (str): The base url of the website.
            num_threads (int): The number of threads to use for crawling.
            max_retry (int): The maximum number of retries for a failed request.
            max_timeout (int): The maximum timeout for a request.

        Notes:

        The IEP website is structured in a way that each article has a unique URL.
        The crawler will start from the base URL and recursively follow links to other articles and 
        will store the content of each article in a dictionary with the URL as the key.
        """
        self.base_url = base_url
        self.num_threads = num_threads
        self.max_retry = max_retry
        self.max_timeout = max_timeout
        self.q = queue.Queue()
        self.lock = threading.Lock()
        self.threads = []
        self.visited = set()
        self.failed = set()
        
    def get_links(self, url):
        """
        Get the links from a given URL.

        Args:
            url (str): The URL to get the links from.

        Returns:
            links (list): A list of links on the page.
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a', href=True)]
            return links
        except Exception as e:
            print(f'Error getting links from {url}: {e}')
            return []
        
    def get_content(self, url):
        """
        Get the content from a given URL.

        Args:
            url (str): The URL to get the content from.

        Returns:
            content (str): The content of the page.
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.get_text()
            return content
        except Exception as e:
            print(f'Error getting content from {url}: {e}')
            return ''
        
    def crawl(self, url):
        """
        Crawl the website starting from a given URL.

        Args:
            url (str): The URL to start crawling from.
        """
        self.q.put(url)
        for i in range(self.num_threads):
            t = threading.Thread(target=self._crawl)
            t.start()
            self.threads.append(t)
        for t in self.threads:
            t.join()

    def _crawl(self):
        while not self.q.empty():
            url = self.q.get()
            print(f'Crawling {url}')
            if url in self.visited:
                print(f'{url} already visited')
                continue
            self.visited.add(url)
            links = self.get_links(url)
            print(f'Found {len(links)} links on {url}')
            for link in links:
                print(f'Checking {link}')
                if link is not None and link.startswith('/') and link not in self.visited:
                    link = f'http://{self.base_url}{link}'
                    self.q.put(link)
                    print(f'Adding {link} to queue')
                if link is not None and link.startswith('http') and self.base_url in link and link not in self.visited:
                    self.q.put(link)
                    print(f'Adding {link} to queue')
            content = self.get_content(url)
            if content:
                print(f'Writing {url} to file')
                print(content)
                with self.lock:
                    with open(f'data/{url.replace("/", "_").replace(":", "_").replace("?", "_")}.txt', 'w', encoding='utf-8') as f:
                        f.write(content)
            else:
                print(f'Failed to get content from {url}')
                with self.lock:
                    self.failed.add(url)
            self.q.task_done()

def main():
    crawler = IEPCrawler()
    crawler.crawl('http://iep.utm.edu/')
    print(f'Visited {len(crawler.visited)} pages')
    print(f'Failed to get content from {len(crawler.failed)} pages')

if __name__ == '__main__':
    main()