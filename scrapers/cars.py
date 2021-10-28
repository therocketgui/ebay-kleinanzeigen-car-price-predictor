from bs4 import BeautifulSoup
import requests
import time
import json
from collections import OrderedDict
import random
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS

def open_data():
    # Get
    with open('data.json') as data_file:
        data = json.load(data_file)
    return data

def save_data(new_data):
    # Load
    _data = open_data()

    for entry in new_data:
        # Append
        _data.append(entry)

    # Store
    with open('data.json', 'w') as f:
        json.dump(_data, f, indent=4)
    return

def get_agent():
    headers_list = [
        # Firefox 77 Mac
        {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
        },
        # Firefox 77 Windows
        {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
        },
        # Chrome 83 Mac
        {
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
        },
        # Chrome 83 Windows
        {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
        }
    ]

    # Create ordered dict from Headers above
    ordered_headers_list = []
    for headers in headers_list:
        h = OrderedDict()
    for header, value in headers.items():
        h[header] = value

    ordered_headers_list.append(h)

    for i in range(1, 4):
        #Pick a random browser headers
        headers = random.choice(headers_list)

    return headers

def req(url):
    gateway = ApiGateway("https://www.ebay-kleinanzeigen.de")
    gateway.start()

    session = requests.Session()
    session.headers = get_agent()
    session.mount("https://www.ebay-kleinanzeigen.de", gateway)

    response = session.get(url)
    # print(response.status_code)

    gateway.shutdown()

    return response

def gateway_start():
    gateway = ApiGateway("https://www.ebay-kleinanzeigen.de")
    gateway.start()
    session = requests.Session()
    session.headers = get_agent()
    session.mount("https://www.ebay-kleinanzeigen.de", gateway)
    return session, gateway

def gateway_stop(gateway):
    gateway.shutdown()
    return

def scrape_iterate_over_pages(page, color):
    session, gateway = gateway_start()
    urls = []
    # for i in range(start, stop):
    time.sleep(0.20)
    try:
        _urls = scrape_list_page(page, session, color)
        urls += _urls
    except Exception as e:
        print(e)
    gateway_stop(gateway)

    return urls

def scrape_pages(urls):
    # Start Gateway:
    session, gateway = gateway_start()
    data = []
    i = 0
    for url in urls:
        # print(page)
        print('Scraping: ' + url)
        try:
            data.append(scrape_page(url, session))
        except Exception as e:
            print(e)
        i += 1
        if i % 8 == 0:
            print('Rotating Gateway')
            # Change gateway every 10 scrapes
            gateway_stop(gateway)
            session, gateway = gateway_start()
    gateway_stop(gateway)
    return data

def scrape_list_page(page, session, color):
    url = 'https://www.ebay-kleinanzeigen.de/s-autos/seite:' + str(
        page) + '/c216+autos.aussenfarbe_s:' + color

    response = session.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    # print(response)
    _urls = []
    # print(soup)
    print('Scraping: ' + url)
    for item in soup.find_all('article', {'class': 'aditem'}):
        _urls.append(item.find('a')['href'])
        # print(_urls)
    return _urls


def scrape_page(page_url, session):
    time.sleep(0.1)
    url = 'https://www.ebay-kleinanzeigen.de' + page_url

    # response = requests.get(url=url, headers=headers)
    response = session.get(url)

    soup = BeautifulSoup(response.content, 'lxml')

    data_details = {}

    for details in soup.find_all("li", {"class": "addetailslist--detail"}):
        _detail = details.text.strip()
        _detail_value = details.find("span",
                                    {"class": "addetailslist--detail--value"}).text.strip()

        _detail_category = _detail.replace(_detail_value, '').strip()

        data_details[_detail_category] = _detail_value

    price = soup.find('h2', {'class': 'boxedarticle--price'}).text.strip()

    data_details['price'] = price
    data_details['url'] = url

    return data_details

def get_exclude_urls():
    return [data['url'] for data in open_data()]

def check_urls(_urls_to_check, _urls):
    urls = []

    for _url in _urls_to_check:
        if _url not in _urls:
            urls.append(_url)
    return urls

if __name__ == "__main__":
    # _exclude_urls = get_exclude_urls()
    # colors = ['schwarz', 'silber', 'weiss', 'blau', 'rot']
    colors = ['grau', 'braun', 'beige', 'gold']

    for color in colors:
        for i in range(1, 51):
            urls = scrape_iterate_over_pages(i, color)
            data = scrape_pages(urls)
            save_data(data)
