import sys
import requests
import bs4 as bs

def retreive_soup(url):
    '''Performs the get request to the url,
    tests response, and returns the html soup.'''
    response = requests.get(url=url)
    if response.raise_for_status() is None:
        return bs.BeautifulSoup (response.content, 'html.parser')
    else:
        print(response.raise_for_status())
        sys.exit()

def retreive_proxy_dict(soup):
    '''Parces the html, returning a dictionary
    containing all the proxy variables.'''
    proxy_list_raw = []
    proxy_data = soup.find('tbody')
    proxies = proxy_data.find_all('tr')
    for prox in proxies:
        cols = prox.find_all('td')
        proxi_i = {
            'ip' : cols[0].text,
            'port' : cols[1].text,
            'country' : cols[3].text,
            'https' : cols[6].text,
        }
        proxy_list_raw.append(proxi_i)
    return proxy_list_raw

def filter_proxies(proxy_list, country, https_only):
    '''Returns a list of filtered proxies. If a country is
    given, all proxies other than given country are dropped.
    If no proxies for given country can be found, all 
    availible country options are printend. If htpps_only,
    then all non-https proxies are dropped.'''
    if country is not None:
        filt_proxies = [x for x in proxy_list if x['country'] == country]
        if not len(filt_proxies):
            print(f'No proxies found for {country}')
            unique_countries = set([x['country'] for x in proxy_list])
            print(f'Availible countries: {", ".join(unique_countries)}')
            sys.exit()
    if https_only:
        filt_proxies = [x for x in proxy_list if x['https'] == 'yes']
        if not len(filt_proxies):
            print(f'No https proxies found.')
            sys.exit()        
    return filt_proxies

def format_proxy_list(raw_proxy_list):
    '''Formats the final proxies into a list in a
    format that can be directly entered into a request.'''
    proxy_list = []
    for proxy in raw_proxy_list:
        if proxy['https'] == 'yes':
            proxy_list.append(f'https://{proxy["ip"]}:{proxy["port"]}')
        else:
            proxy_list.append(f'http://{proxy["ip"]}:{proxy["port"]}')
    return proxy_list 

def retreive_proxy_list(country=None, https_only=False):
    URL = 'https://www.free-proxy-list.net/anonymous-proxy.html'
    soup = retreive_soup(URL)
    raw_proxies = retreive_proxy_dict(soup)
    if country is not None or https_only:
        raw_proxies = filter_proxies(raw_proxies, country, https_only)
    proxy_list = format_proxy_list(raw_proxies)
    return proxy_list

if __name__ == "__main__":
    retreive_proxy_list()

