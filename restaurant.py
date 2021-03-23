import urllib.request
import bs4 as bs
import json
import os

class Restaurant:
  rid_list = []

  def __init__(self, rid, url, opener):
    ''' Parses the restaurant page on TB. 
    Inputs:
    rid : Restaurant ID
    url: The restaurant URL on Thuisbezorgd
    opener: requests handler. '''
    self.rid = rid
    Restaurant.rid_list.append(self.rid)
    self.url = url
    try:
        website = opener.open(self.url)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    else:
      html = website.read()
      soup = bs.BeautifulSoup(html, 'html.parser')
      
      # Retreive restaurant website url
      self.retreive_restaurant_website_url(soup)
      # Parse information in first script bracket: restuarant info:
      self.parse_info_schema_json_information(soup)
      self.split_address_into_street_and_number()
      # Parse infomation in second script bracket: delivery times and locations:
      self.parse_delivery_times_and_locations(soup)
      # Parse information in third script bracket: menu items:
      self.parse_menu_items(soup)
      # Retreive menu catagories:
      self.parse_menu_catagories(soup)
      
      self.dump_json()

  def split_address_into_street_and_number(self):
    ''' Method to split the address in to two-parts: 
    the street and the housenumber. Street will be all characters
    up untill the first character that is a digit. Housenumber will
    be every character in the string after.'''
    try:
      for i, s in enumerate(self.address):
        if s.isdigit():
          num_pos = i
          break
      self.street = self.address[:num_pos].strip()
      self.house_number = self.address[num_pos:]
    except:
      self.street = None
      self.house_number = None

  def retreive_restaurant_website_url(self, soup):
    ''' Method to retreive the restaurant website url.
    Finds the website information within info card section of the page soup, and 
    returns the url contained in the href. '''
    try:
      info_card = soup.find('div', class_='info-card restaurant-info__restaurant-link')
      website_info = info_card.find('div', class_='info-tab-section')
      self.restaurant_website_url = website_info.a['href']
    except AttributeError:
      self.restaurant_website_url = None

  def parse_info_schema_json_information(self, soup):
    ''' Method that parses the required information stored in the restaurant schema JSON.
    First retreives the json information of interest from the soup, storing it in the schema_json
    variable. Next, sets the required information as attributes of the Restaurant instance. '''
    schema_json = json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))

    self.name = schema_json['name']
    self.address = schema_json['address']['streetAddress']
    self.zipcode = schema_json['address']['postalCode']
    self.city = schema_json['address']['addressRegion']
    self.logo_url = schema_json['image']

    # Some restaurants do not (yet) have ratings, hence the try/except block here.
    try:
      self.rating_value = schema_json['aggregateRating']['ratingValue']
      self.rating_count = schema_json['aggregateRating']['reviewCount']
    except KeyError:
      self.rating_value = 0
      self.rating_count = 0

  def parse_delivery_times_and_locations(self, soup):
    ''' Method that parses the information in the second script bracket in order
    to retreive the restaurant delivery times and locations. '''
    raw_script = soup.body.find_all('script')[1].string
    # Modify the script text to be able to convert to json
    raw_script = raw_script.split('var currentRestaurant = ')[1]
    raw_script = raw_script.split('var TranslationsJSobject')[0]
    raw_script = raw_script.replace('};', '}')
    # Convert to json
    script_json = json.loads(raw_script)
    # Extract required information and set as instance attributes.
    self.restaurant_delivery_times = script_json['Times']['deliveryopentimes']
    self.restaurant_delivery_locations = script_json['Locations']

  def parse_menu_items(self, soup):
    ''' Method that parses the information in the second script bracket in order
    to retreive the menu items. '''
    raw_script = soup.body.find_all('script')[2].string
    # Modify to be able to convert to a list of dictionaries
    raw_menu = raw_script.split('var MenucardProducts =')[1]
    raw_menu = raw_menu.replace('];', ']')
    raw_menu = raw_menu.replace('true', 'True')
    raw_menu = raw_menu.replace('false', 'False')
    # Set resulting list of dictionaries of menu items as instance attribute.
    self.menu = list(eval(raw_menu))

  def parse_menu_catagories(self, soup):
    ''' Parses the swipper wrapper in order to extract the menu item catagory 
    names and their corresponsing IDs.'''
    # Locate swiper wrapper inside soup.
    swiper_wrapper = soup.find('div', class_='swiper-wrapper')
    # Set up empty dictionary in which key : catagory name, value : catagory ID
    self.menu_catagory_dict = {}
    for catagory in swiper_wrapper.find_all('a'):
      self.menu_catagory_dict[f'{catagory.text}'] = f'{catagory["data-category"]}'

  def dump_json(self):
    # data = json.loads(str(vars(self)))
    # with open('restaurants.json', 'r') as json_file:
    #   parsed = json.dumps(data, indent=1)
    data = str(vars(self))
    json.dumps(data, indent=4)
    with open('sample_data.txt', 'w') as outfile:
      json.dump(data, outfile)

