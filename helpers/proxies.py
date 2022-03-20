import requests
import time
import random
# use to parse html text
from lxml.html import fromstring 
from bs4 import BeautifulSoup

def getProxies():
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')
    proxies = []
    for row in table:
        if row.find_all('td')[4].text =='elite proxy':
            proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
            proxies.append(proxy)
        else:
            pass
    return proxies

def responseThruProxy(url):
  proxies = getProxies()
  
  # to rotate through the list of IPs
  proxy = random.choice(proxies)
   
   
  for i in range(1, 11):
    
      time.sleep(i)
      print("Request #%d" % i)
   
      try:
          response = requests.get(url, proxies={"http": proxy, "https": proxy})
          return response
      except StopIteration:
        continue
        
  print("Failed to find proxy")