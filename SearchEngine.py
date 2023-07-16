import json
import pickle
import random
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import endetail_whois as wh
import requests
from ScrapeSearchEngine.ScrapeSearchEngine import Bing
from bs4 import BeautifulSoup
from selenium import webdriver


def crawl_bing(keyword='Enterprise Switch', page_count=2):
    search_results = []
    for i in range(page_count):
        search = quote(keyword, encoding='utf-8') + '&first={}'.format(i * 10)
        search_results += Bing(search, None)
    domain_names = [get_domain_name(url) for url in search_results]
    domain_names = list(set(domain_names))
    search_domains = {}
    [search_domains.__setitem__(url, domain_names.index(get_domain_name(url))) for url in search_results]
    Bing(None, None)
    return search_results, domain_names, search_domains


def crawl_dnb(page_count=8, keyword='Cisco', driver=None):
    if driver is None:
        challenge = True
        driver = webdriver.Chrome()
    else:
        challenge = False
    base_url = 'https://www.dnb.com/site-search-results.html#'
    dnb_results = []
    for i in range(page_count):
        page = i + 1
        keyword_encoded = quote(keyword, encoding='utf-8')
        p_dict = {
            'AllSearch': keyword_encoded,
            'CompanyProfilesPageNumber': page,
            'CompanyProfilesSearch': keyword_encoded,
            'ContactProfilesPageNumber': '1',
            'DAndBMarketplacePageNumber': '1',
            'SiteContentPageNumber': '1',
            'tab': 'Company%20Profiles'
        }
        p_url = '&'.join(['{}={}'.format(key, p_dict[key]) for key in p_dict])
        url = base_url + p_url
        driver.get(url)
        if i == 0 and challenge:
            input('pass challenge')
        else:
            time.sleep(2 + random.random())
        soup = BeautifulSoup(driver.page_source, 'lxml')
        tbody_content = soup.find('tbody')
        if tbody_content is None:
            break
        else:
            dnb_results += process_dnb(tbody_content)
    return dnb_results, driver


def crawl_rdap(domain_names):
    domain_details = {}
    rdap_servers = [
        'https://rdap.markmonitor.com/rdap/domain/{}',
        'https://whois.ename.com/rdap/domain/{}',
        'https://rdap.verisign.com/com/v1/domain/{}',
        'https://rdap.namecheap.com/domain/{}'
    ]
    for url in domain_names:
        i = 0
        print(url)
        try:
            print(rdap_servers[i].format(url))
            request = requests.get(rdap_servers[i].format(url))
            while request.status_code != 200 and i + 1 < len(rdap_servers):
                i += 1
                print(rdap_servers[i].format(url))
                request = requests.get(rdap_servers[i].format(url))
            if request.status_code != 200:
                print('Cannot find RDAP entry.')
                res = None
            else:
                print('Found RDAP entry')
                res = parse_rdap(request)
                if res is None:
                    print('No valid company information, skipped.')
                else:
                    print('Company information extracted.')
            domain_details.__setitem__(url, res)
        except Exception as e:
            print(repr(e))
            domain_details.__setitem__(url, None)
        time.sleep(1 + random.random())
    return domain_details


def crawl_site_info(keyword='Enterprise Switch', page_count=2):
    search_results, domain_names, search_domains = crawl_bing(keyword=keyword, page_count=page_count)
    domain_details = crawl_rdap(domain_names)
    return search_results, domain_names, search_domains, domain_details


# whois py lib need whois cmd tool from microsoft
# https://learn.microsoft.com/zh-cn/sysinternals/downloads/whois
def crawl_whois(domain_names, retry=3):
    domain_details = {}
    pool = ThreadPoolExecutor(max_workers=1)
    for url in domain_names:
        print(url)
        ok = False
        res = 'No match for'
        attempt = 0
        while not ok:
            try:
                lookup = pool.submit(crawl_whois_thread, url)
                res = lookup.result(timeout=5)
                ok = True
            except Exception as e:
                print(repr(e))
                pool.shutdown()
                pool = ThreadPoolExecutor(max_workers=1)
                print('线程池重启，连接已切断')
            attempt += 1
            if attempt >= retry:
                break
            time.sleep(attempt * 1 + random.random() * 1)
        if 'No match for' in res:
            res = None
        domain_details.__setitem__(url, res)
        time.sleep(1 + random.random())
    return domain_details


def crawl_whois_thread(url):
    res = wh.get(url, 'whois.internic.net')
    return res


def filter_dnb(dnb_results):
    temp = []
    ok_ind = [
        'Computer and Peripheral Equipment Manufacturing',
        'Computer Systems Design and Related Services',
        'Household Appliances and Electrical and Electronic Goods Merchant Wholesalers',
        'Wired and Wireless Telecommunications (except Satellite)',
        'Communications Equipment Manufacturing',
        'Other Electrical Equipment and Component Manufacturing'
    ]
    for dnb_result in dnb_results:
        if dnb_result['industry'] in ok_ind:
            temp.append(dnb_result)
    dnb_results = temp
    return dnb_results


def get_domain_name(url):
    domain_name = url.replace('http://', '').replace('https://', '').split('/')[0].split('.')
    if domain_name[0] == 'www':
        domain_name.pop(0)
    domain_name = '.'.join(domain_name)
    return domain_name


def parse_rdap(request):
    res = json.loads(request.content)
    if 'entities' in res.keys():
        res = [entity['vcardArray'][1] for entity in res['entities'] if 'registrant' in entity['roles']]
        for i in range(len(res)):
            while len(res[i]) > 0 and res[i][0][0] != 'org':
                res[i].pop(0)
            while len(res[i]) > 1:
                res[i].pop(-1)
            if len(res[i]) > 0:
                res[i] = res[i][0]
        if len(res) > 0:
            if len(res[0]) >= 4:
                res = res[0][3]
            else:
                res = None
        else:
            res = None
    else:
        res = None
    return res


def process_dnb(tbody_content):
    results = []
    for hit in tbody_content.contents:
        name = '\n'.join([content.text for content in hit.contents[0].contents]).split('\nBusiness Credit Reports\n')[0]
        url = hit.contents[0].contents[0].attrs['href']
        industry = hit.contents[1].text
        loc_type = hit.contents[2].text
        region = hit.contents[3].text
        results.append(
            {'name': name, 'industry': industry, 'loc_type': loc_type, 'region': region, 'url': url}
        )
    return results


def process_whois(domain_detail):
    temp = domain_detail.split('\n')
    temp_ = []
    while not temp[0].startswith('>>>'):
        temp_.append(temp.pop(0).strip())
    temp = temp_
    whois_dict = {}
    [whois_dict.__setitem__(line.split(': ')[0], line.split(': ')[1]) for line in temp]
    return whois_dict['Registrar WHOIS Server']


# def whois2rdap(p_dict):
#     whois_res = p_dict['whois_res']
#     url = p_dict['url']
#     rdap_server = 'https://' + process_whois(whois_res) + '/rdap/domain/{}'
#     # todo: this is not a common paradigm that all RDAP follow,
#     #  need to find a way to lookup RDAP address automatically
#     request = requests.get(
#         rdap_server.format(url),
#         headers={
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
#                           'like Gecko) Chrome/114.0.0.0 Safari/537.36'
#         }
#     )
#     return request


def main(product_key='Enterprise Switch', product_page=2, dnb_page=2):
    search_results, domain_names, search_domains, domain_details = crawl_site_info(
        keyword=product_key,
        page_count=product_page
    )
    driver = None
    domain2dnb = {}
    for domain_key in domain_details.keys():
        if domain_details[domain_key] is not None:
            company_keyword = domain_details[domain_key]
            dnb_results_raw, driver = crawl_dnb(page_count=dnb_page, keyword=company_keyword, driver=driver)
            dnb_results = filter_dnb(dnb_results_raw)
            domain2dnb.__setitem__(domain_key, {'filtered': dnb_results, 'raw': dnb_results_raw})
    pickle.dump(
        {
            'search_results': search_results,
            'domain_names': domain_names,
            'search_domains': search_domains,
            'domain_details': domain_details,
            'domain2dnb': domain2dnb
        },
        open(product_key + '.pkl', 'wb')
    )


if __name__ == '__main__':
    main(product_key='Enterprise Switch', product_page=200, dnb_page=1)
