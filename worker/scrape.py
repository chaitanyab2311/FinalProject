from bs4 import BeautifulSoup
import requests
import string
import time
from db import *
import random
import logs


def Removewords(tag):
    CleanWord = [letter for letter in tag if letter in string.digits or letter == "."]
    return "".join(CleanWord)

def GetEbayItems(soup):

    final = []
    result_items = soup.find_all("li",{"class":"s-item s-item__pl-on-bottom"})

    
    for item_count,item in enumerate(result_items,1):
        item_name =  item.find("h3",{"class":"s-item__title"}).text
       
        if(item_name):
            item_price = item.find("span",{"class":"s-item__price"})
            item_price_striped =  item_price.getText()
            item_url = item.find("div",{"class":"s-item__image"})
            children = item_url.findChildren("a" , recursive=False)
            for child in children:
                item_url = child['href']

            item_image_url = item.find("img",{"class":"s-item__image-img"})['src']

            if(item_price_striped != ''):
                final.append({
                    'productname' : item_name,
                    'productprice' : item_price_striped,
                    'website' : 'Ebay',
                    'product_url': item_url,
                    'product_image_url': item_image_url
                })

            
        if item_count == 10:
            break
    return final



def GetAmazonitems(soup):

    final = []
    
    try:
        result_items = soup.find_all("div",{"class": "s-include-content-margin s-latency-cf-section s-border-bottom s-border-top"})

        for item_count,item in enumerate(result_items,1):
            item_name =  item.find("a",{"class":"a-link-normal a-text-normal"}).text
            item_price =  item.find("span",{"class":"a-offscreen"})
            item_price = Removewords(str(item_price))
            item_url = item.find("a",{"class":"a-link-normal s-no-outline"})['href']
            item_image_url = item.find("img",{"class":"s-image"})['src']
            
            if(item_price != ''):
                final.append({
                    'productname' : item_name,
                    'productprice' : item_price,
                    'website' : 'Amazon',
                    'product_url': item_url,
                    'product_image_url': item_image_url
                })
            if item_count == 10: 
                break
    except AttributeError as Ae:
        pass
    return final


def getBestBuyitems(soup):

    final = []
    
    try:
        count = 0
        print(len(soup.find_all("li", {'class': 'sku-item'})))
        for brand in soup.find_all("li", {'class': 'sku-item'}): 
            print(brand)
            item_name_soup = brand.find("h4",{"class":"sku-header"})
            children = item_name_soup.findChildren("a" , recursive=False)
            for child in children:
                item_name = child.text
                item_url = child['href']
                break
            
            item_soup = brand.find("div",{"class":"priceView-hero-price priceView-customer-price"})
            children = item_soup.findChildren("span" , recursive=False)
            for child in children:
                item_price_striped = child.text
                break

            product_image_soup = brand.find("img",{"class":"product-image"})
            item_image_url = product_image_soup['src']

            product_url_soup = brand.find("img",{"class":"product-image"})
            item_image_url = product_image_soup['src']
            print(item_name)
            print(item_price_striped)
            final.append({
                            'productname' : item_name,
                            'productprice' : item_price_striped,
                            'website' : 'bestbuy',
                            'product_url': item_url,
                            'product_image_url': item_image_url
                        })
            count = count + 1
            
            if count == 10:
                break

    except AttributeError as Ae:
        pass

    return final


def parseInput(mystring):
    mystring = mystring.strip()
    while '  ' in mystring:
        mystring = mystring.replace('  ', ' ')
    return mystring.replace(' ', '%20')


def start_scraping(search):

    logs.enqueueDataToLogsExchange("Started scraping",'info')
    
    final_result = {}
    items = presentindatabase(search)

    if len(items) > 0:
        return items

    else:
    #ebay
        ebay_link = "http://www.ebay.com/sch/i.html?_from=R40&_trksid=p2050601.m570.l1313.TR10.TRC0.A0.H0.X"+search+".TRS0&_nkw="+search+"&_sacat=0"
        Ebay_Items = None
        ebay = requests.get(ebay_link)
        ebay_soup = BeautifulSoup(ebay.content,"html.parser")
        exception_counter_e = 1
        try:
            Ebay_Items = GetEbayItems(ebay_soup)
        except Exception as e:
            exception_counter_e += 1
            if exception_counter_e == 5 :
                Ebay_Items = GetEbayItems(ebay_soup)
            else: 
                print(e)
                print("can't get results from ebay..")
        


        #amazon
        amazon_link = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="+search
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
        Amazon_Items = None
        amazon = requests.get(amazon_link,headers = headers)
        amazon_soup = BeautifulSoup(amazon.content,"html.parser")
        exception_counter = 1
        try:
            Amazon_Items = GetAmazonitems(amazon_soup)
        except:
            exception_counter+=1
            if exception_counter != 5 :
                Amazon_Items = GetAmazonitems(amazon_soup)
            else: 
                print("can't get results from Amazon")


        #best buy 
        front_url = "https://www.bestbuy.com/site/searchpage.jsp?cp="
        middle_url = "&searchType=search&st="
        search_term = parseInput(search)
        Best_Buy_Items = None
        end_url = "&_dyncharset=UTF-8&id=pcat17071&type=page&sc=Global&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All%20Categories&ks=960&keys=keys"
        url = front_url + str(1) + middle_url + search_term + end_url
        
        agent = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',  # noqa: E501
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache'
            }
            
        s = requests.Session()
        page = s.get(url, headers=agent)
        best_buy_soup = BeautifulSoup(page.text, 'html.parser')
        exception_counter = 1
        try:
            Best_Buy_Items = getBestBuyitems(best_buy_soup)
        except:
            exception_counter+=1
            if exception_counter != 5 :
                Best_Buy_Items = getBestBuyitems(best_buy_soup)
            else: 
                print("can't get results from Best Buy")
            


    final_result['ebay'] = Ebay_Items
    final_result['amazon'] = Amazon_Items
    final_result['bestbuy'] = Best_Buy_Items
    
    return final_result

