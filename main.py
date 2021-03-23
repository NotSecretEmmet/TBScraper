import urllib
from urllib.error import URLError, HTTPError
import bs4 as bs
import json
from pprint import pprint
from restaurant import Restaurant
from proxy import retreive_proxy_list
from scraping_utils import random_sleep_wait

BASE_URL = 'https://www.thuisbezorgd.nl'
USER_AGENT_LIST = [
    ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15'),
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'),
    ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'),
    ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0'),
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'),
]

def setup_opener():
    ''' Setup the opener to handle requests.
    Adds different user-agents in order to avoid detection.
    NEED TO ADD PROXIES!! 
    Returns the opener object. '''
    proxy = urllib.request.ProxyHandler({}) # https://docs.python.org/3.5/howto/urllib2.html#proxies
    opener = urllib.request.build_opener(proxy) #https://docs.python.org/3/library/urllib.request.html -> 
    urllib.request.install_opener(opener)
    opener.addheaders = USER_AGENT_LIST
    return opener

def parse_region(url, opener):
    ''' Function to parse the region page.
    The region page, is the page listing all restaurants in a specific delarea/region. '''
    region_url = url
    try:
        region_website = opener.open(region_url)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    else:
        html = region_website.read()
        soup = bs.BeautifulSoup(html, 'html.parser')

        # Extract the restaurant var from the first script brackets
        raw_script = soup.body.find_all('script')[0].string
        # Manipulate resulting string in order to be able to convert data into a list
        # of list, where each list element contains information regarding a specific restaurant.
        raw_script = raw_script.replace('var restaurants = ', '') #
        raw_script = '[' + raw_script[4:].lstrip()
        raw_script = raw_script.split('var polygons')[0]
        raw_script = raw_script.replace('];', ']').rstrip()
        raw_script = raw_script[:-1].rstrip() + ']'
        raw_script = raw_script.replace('true', 'True')
        raw_script = raw_script.replace('false', 'False')
        raw_script = raw_script.replace("null", "'null'")
        restaurant_list = list(eval(raw_script))
        
        for restaurant in restaurant_list:
            restaurant_id = restaurant[0]
            restaurant_name = restaurant[4]
            # The -11th variable is an information dictionary containing the url.
            restaurant_url = BASE_URL + restaurant[-11]['url'].replace('\/','/')
            
        # Check if restaurant already exists by querying DB by restaurant ID
        # For now (no DB setup), check if resaurant id present in class variable rid_list
        if not restaurant_id in Restaurant.rid_list:
            a = Restaurant(restaurant_id, restaurant_url, opener)
            pprint(vars(a))
            random_sleep_wait()

def main():
    ''' Main procedure.
    Starts by setting up the opener to handle the get requests.
    Next, calls the main_url, extracts all the delivery areas(delareas) and stores
    them in a dictionary. 
    Finally, loops over the items in said dictionary, calling the scrape_region
    for each (sub)delarea.  '''
    opener = setup_opener()
    
    main_url = BASE_URL + '/eten-bestellen-noord-holland'
    try:
        main_list_website = opener.open(main_url)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    else:
        html = main_list_website.read()
        soup = bs.BeautifulSoup(html, 'html.parser')
        # Retreive all regions/delareas 
        delareas = soup.find_all('div', class_='delarea')
        # Create a dictionary of all delivery areas, with key : name, value : url
        delarea_dict = {}
        for delarea in delareas:
            delarea_dict[f"{delarea.text}"] = f'{delarea.a["href"]}'
    random_sleep_wait()

    # Next, iterate through each delarea.
    # 2 possible outcomes: 
        # Option 1: There are subregions within the region/delarea.
            # In this case, each subregion/delarea is added to the delivery area dictionary, after which
            # the specific delarea page is scrapped by calling the scrape_region function.
        # Option 2: There are no subregions, and hence the scrape_region function is called directly. 
    delarea_iterator = delarea_dict.copy()
    for name, url in delarea_iterator.items():
        print(f'checking for subregions in {name}')
        try:
            website = opener.open(BASE_URL + url)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        else:
            html = website.read()
            soup = bs.BeautifulSoup(html, 'html.parser')
            delareas = soup.find_all('div', class_='delarea')
            if len(delareas) > 0:
                # Option 1:
                print(f'subregions found in {name}')
                for delarea in delareas:
                    delarea_dict[f"{delarea.text}"] = f'{delarea.a["href"]}'
                    print(f'parsing region: {delarea.text}')
                    parse_region(BASE_URL + delarea.a["href"], opener)
                # Remove parent delarea <- Might be redundant.
                delarea_dict.pop(name)
            else:
                # Option 2:
                print(f'No subregions found in {name}')
                print(f'parsing region: {name}')
                parse_region(BASE_URL + url, opener)
            random_sleep_wait()

main()


# test_region = '/eten-bestellen-1036'
# parse_region(test_region, opener)

# # test_restaurant_url = 'https://www.thuisbezorgd.nl/menu/payal'
# # testrestaurant = Restaurant('test_rid', test_restaurant_url, opener)
# # pprint(vars(testrestaurant))