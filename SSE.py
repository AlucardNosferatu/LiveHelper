import random
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# Replace ScrapeSearchEngine.py with this file renamed
# Enable Selenium crawling to get web content after loading

# Github: https://github.com/sujitmandal
# This program is created by Sujit Mandal
"""
Github: https://github.com/sujitmandal
Pypi : https://pypi.org/user/sujitmandal/
LinkedIn : https://www.linkedin.com/in/sujit-mandal-91215013a/
"""

# search on Google "my user agent"
# userAgent = ('') #my user agent
# search = ('') #Enter Anything for Search
driver = None
httpResponseStatusCodes = {
    100: 'Continue',
    101: 'Switching Protocol',
    102: 'Processing (WebDAV)',
    103: 'Early Hints',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: ' No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status (WebDAV)',
    208: 'Already Reported (WebDAV)',
    226: 'IM Used (HTTP Delta encoding)',
    300: 'Multiple Choice',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: 'unused',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Payload Too Large',
    414: 'URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Range Not Satisfiable',
    417: 'Expectation Failed',
    418: 'I am a teapot',
    421: 'Misdirected Request',
    422: 'Unprocessable Entity (WebDAV)',
    423: 'Locked (WebDAV)',
    424: 'Failed Dependency (WebDAV)',
    425: 'Too Early',
    426: 'Upgrade Required',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',
    451: 'Unavailable For Legal Reasons',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    506: 'Variant Also Negotiates',
    507: 'Insufficient Storage (WebDAV)',
    508: 'Loop Detected (WebDAV)',
    510: 'Not Extended',
    511: 'Network Authentication Required'
}


def Google(search, userAgent):
    url = ('https://google.com/search?q=' + search)
    headers = {'user-agent': userAgent}
    request = requests.get(url, headers=headers)
    results = []
    if request.status_code == 200:
        soup = BeautifulSoup(request.content, 'html.parser')
        for i in soup.find_all('div', {'class': 'yuRUbf'}):
            link = i.find_all('a')
            links = link[0]['href']
            results.append(links)
    else:
        print('HTTP Response Status For Google : {}'.format(httpResponseStatusCodes.get(request.status_code)))
        results.append('HTTP Status : {}'.format(httpResponseStatusCodes.get(request.status_code)))
    return results


def Duckduckgo(search, userAgent):
    url = ('https://duckduckgo.com/html/?q=' + search)
    headers = {'user-agent': userAgent}
    request = requests.get(url, headers=headers)
    results = []
    if request.status_code == 200:
        soup = BeautifulSoup(request.content, 'html.parser')
        for i in soup.find_all('a', attrs={'class': 'result__a'}):
            links = i['href']
            results.append(links)
    else:
        print('HTTP Response Status For Duckduckgo : {}'.format(httpResponseStatusCodes.get(request.status_code)))
        results.append('HTTP Status : {}'.format(httpResponseStatusCodes.get(request.status_code)))
    return results


def Givewater(search, userAgent):
    url = ('https://search.givewater.com/serp?q=' + search)
    headers = {'user-agent': userAgent}
    request = requests.get(url, headers=headers)
    results = []
    if request.status_code == 200:
        soup = BeautifulSoup(request.content, 'html.parser')
        for i in soup.find_all('div', {'class': 'web-bing__result'}):
            link = i.find_all('a')
            links = link[0]['href']
            results.append(links)
    else:
        print('HTTP Response Status For Givewater : {}'.format(httpResponseStatusCodes.get(request.status_code)))
        results.append('HTTP Status : {}'.format(httpResponseStatusCodes.get(request.status_code)))
    return results


def Ecosia(search, userAgent):
    url = ('https://www.ecosia.org/search?q=' + search)
    headers = {'user-agent': userAgent}
    request = requests.get(url, headers=headers)
    results = []
    if request.status_code == 200:
        soup = BeautifulSoup(request.content, 'html.parser')
        for i in soup.find_all('div', {'class': 'result-firstline-container'}):
            link = i.find_all('a')
            links = link[0]['href']
            results.append(links)
    else:
        print('HTTP Response Status For Ecosia : {}'.format(httpResponseStatusCodes.get(request.status_code)))
        results.append('HTTP Status : {}'.format(httpResponseStatusCodes.get(request.status_code)))
    return results


def Bing(search, userAgent):
    global driver
    results = []
    if search is None and driver is not None:
        driver.close()
        driver = None
    else:
        if driver is None:
            driver = webdriver.Chrome()
        URL = ('https://cn.bing.com/search?q=' + search)
        if userAgent is not None:
            headers = {'user-agent': userAgent}
            request = requests.get(URL, headers=headers)
            if request.status_code == 200:
                soup = BeautifulSoup(request.content, "html.parser")
                for i in soup.find_all('li', {'class': 'b_algo'}):
                    link = i.find_all('a')
                    links = link[0]['href']
                    results.append(links)
            else:
                print('HTTP Response Status For Bing : {}'.format(httpResponseStatusCodes.get(request.status_code)))
                results.append('HTTP Status : {}'.format(httpResponseStatusCodes.get(request.status_code)))
        else:
            driver.get(URL)
            time.sleep(1 + 1 * random.random())
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for i in soup.find_all('li', {'class': 'b_algo'}):
                link = i.find_all('a')
                links = link[0]['href']
                results.append(links)
    return results


def Yahoo(search, userAgent):
    url = ('https://search.yahoo.com/search?q=' + search)
    request = requests.get(url)
    results = []
    if request.status_code == 200:
        soup = BeautifulSoup(request.content, 'html.parser')
        for i in soup.find_all(attrs={"class": "d-ib ls-05 fz-20 lh-26 td-hu tc va-bot mxw-100p"}):
            link = i.get('href')
            results.append(link)
    else:
        print('HTTP Response Status For Yahoo : {}'.format(httpResponseStatusCodes.get(request.status_code)))
        results.append('HTTP Status : {}'.format(httpResponseStatusCodes.get(request.status_code)))
    return results


if __name__ == "__main__":
    # Bing(search, userAgent)
    # Yahoo(search, userAgent)
    # Google(search, userAgent)
    # Ecosia(search, userAgent)
    # Givewater(search, userAgent)
    # Duckduckgo(search, userAgent)
    print('Done')