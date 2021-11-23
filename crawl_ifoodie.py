from selenium import webdriver
import bs4
import requests
import json
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Comingo_Collect_Data"]
mycol = mydb["new_TaiwanBlogRestaurant"]

driverPath = 'C:\cico\geckodriver\chromedriver.exe'
browser = webdriver.Chrome(driverPath)
urlbase = 'https://ifoodie.tw'
url = 'https://ifoodie.tw/ranking/'

cities = ['台北', '高雄', '台南', '台中', '桃園', '宜蘭', '新竹',
          '嘉義', '彰化', '基隆', '花蓮', '南投', '苗栗', '屏東',
          '雲林', '台東']

types = ['weekly', 'monthly']


def changeType(type):
    return str(type) + '/'


def changeCity(city):
    return str(city) + '/'


def isRepeat(restaurant):
    myquery = {"name": restaurant}
    mydoc = mycol.find(myquery)
    if mycol.find(myquery).count() > 0:
        return False
    else:
        return True


def crawl_restaurants(url):
    # print(url)
    browser.get(url)

    objSoup = bs4.BeautifulSoup(browser.page_source, 'lxml')

    blogItemsSoup = objSoup.find_all("div", "blog-item")

    count = 0
    for blogItemSoup in blogItemsSoup:
        restaurant_info_soup = blogItemSoup.find("div", "restaurant")
        restaurant_href = restaurant_info_soup.find("a")["href"]

        print(restaurant_href)
        more_info_href = blogItemSoup.find("h4").find("a")["href"]
        # print(more_info_href)
        href_htmlfile = requests.get(urlbase + more_info_href)
        hrefSoup = bs4.BeautifulSoup(href_htmlfile.text, 'lxml')
        readmore_href = hrefSoup.find("p", "desc below").find("a", "readmore")["href"]

        browser.get(urlbase + restaurant_href)
        htmlfile = requests.get(urlbase + restaurant_href)
        detailSoup = bs4.BeautifulSoup(browser.page_source, "lxml")
        count += 1

        crawl_data = str(detailSoup.find("script", {"id": "__NEXT_DATA__"}))
        data = crawl_data[crawl_data.find("{"):crawl_data.find("</script>")]

        json_data = json.loads(data, strict=False)
        try:
            restaurant_info = json_data['props']["initialState"]["checkins"]["checkinInfo"]["data"][0]['restaurant']

            restaurant = restaurant_info['name']
            city = restaurant_info['city']
            phone = restaurant_info['phone']
            address = restaurant_info['address']
            openingHoursList = restaurant_info['openingHoursList']
            X = restaurant_info['lat']
            Y = restaurant_info['lng']

            try:
                img = detailSoup.find('div', 'default').find('img')['src']
            except AttributeError:
                img = 'none'
                pass
            try:
                avg_price = detailSoup.find("div", "price-outer").text
            except AttributeError:
                avg_price = "none"
                pass
            if isRepeat(restaurant):
                # if isRepeat(restaurant) and city == '新北市':
                dict = {'name': restaurant, 'city': city, '地址': address, 'X': X, 'Y': Y, "img": img, 'phone': phone,
                        'avg_price': avg_price, 'moreinfo_href': readmore_href, 'openingHourList': openingHoursList}
                #     print(readmore_href)
                #     print(restaurant)
                #     print(city)
                #     print(address)
                #     print(phone)
                #     print(openingHoursList)
                #     if avg_price != '新增點擊':
                #         print(avg_price)
                #     print(img)
                #     print(X)
                #     print(Y)
                #     print("=======================================")
                mycol.insert_one(dict)
            else:
                print('----------------repeat----------------')
            #     print(restaurant)
            #     print(city)
        except IndexError:
            pass


if __name__ == "__main__":
    # for type in types:
    for i in range(364, 365):
        # for city in cities:
        for j in range(6, 15):
            crawl_restaurants(url + changeType(types[0]) + changeCity(cities[j]) + str(i) + '/')
    # crawl_restaurants(url + changeType(type) + changeCity(cities[15]) + '/')
