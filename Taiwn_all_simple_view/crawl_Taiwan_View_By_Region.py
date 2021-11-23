import pymongo
import requests
import bs4
import re

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Comingo_Collect_Data"]
mycol = mydb['Cities_Region_ViewHref']

newdb = myclient["New_ComingoDB"]
newcol = newdb['EasternTaiwan_Attractions']
urlbase = 'https://www.taiwan.net.tw/'

def get_cites_in_db():
    myquery = {"region": "東部地區"}
    mydoc = mycol.find(myquery)
    return mydoc

def get_url(cities_data):
    href_list = []
    for dict in cities_data:
        href_list.append(dict['href'])
    return href_list

def get_city(cities_data):
    cities_list = []

    for dict in cities_data:
        cities_list.append(dict['city'])
    return cities_list

def crawl_cities(city_list, href_list):

    for i in range(0, len(href_list)):
        current_page = href_list[i]
        city = city_list[i]
        # if i==1:
        #     break;
        print(current_page + '' + city)
        crawl_city_attracions(current_page, city)

def crawl_city_attracions(href, city):
    htmlfile = requests.get(urlbase+href)
    objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')
    attractionsSoup = objSoup.find('ul', 'card-style-columns').find_all('li')

    for attractionSoup in attractionsSoup:
        attraction_href = attractionSoup.find('a')['href']
        attraction_views = attractionSoup.find('p', 'target-like').text.split('：')[1]
        attraction_img = attractionSoup.find('div', 'graphic').find('img')['data-src']

        attractionHtml = requests.get(urlbase+attraction_href)
        detailSoup = bs4.BeautifulSoup(attractionHtml.text, 'lxml')

        attraction_name = detailSoup.find('div', 'title').find('h2').text

        dict = {'景點': attraction_name, '城市' : city, '圖片': attraction_img, 'view': attraction_views}

        tagSoup = detailSoup.find('dl', 'info-table').find_all('dt')
        valSoup = detailSoup.find('dl', 'info-table').find_all('dd')

        for i in range(0, len(tagSoup)):
            tag_name = tagSoup[i].text
            tag_val = valSoup[i].text

            if tag_name == '網站：' :
                try:
                    tag_href = valSoup[i].find('a')['href']
                except TypeError:
                    tag_href = 'none'
                    pass
                dict["網站"] = tag_val
                dict['網站_href'] = tag_href

            elif tag_name == '經度/緯度：':
                tag_val = tag_val.split('/')
                dict['X'] = tag_val[0]
                dict['Y'] = tag_val[1]
            elif tag_name == '電話：':
                dict['phone'] = tag_val
            else:
                dict[tag_name[:-1]] = tag_val


        hashtags = detailSoup.select('div.hashtag > a')
        hashtag_list = []
        for hashtag in hashtags:
            hashtag_list.append(hashtag.text)

        dict['hashtag'] = hashtag_list

        content = ""
        introSoup = detailSoup.select('div.wrap > p')

        for intro in introSoup:
            content += intro.text + '\n'

        dict['介紹'] = content

        transport = detailSoup.find('article').text

        dict['transport'] = transport
        newcol.insert_one(dict)
        print(dict)

if __name__ == "__main__":
    cities_data = get_cites_in_db()
    city_list = get_city(cities_data)
    cities_data = get_cites_in_db()
    href_list = get_url(cities_data)
    print(city_list)
    print(href_list)
    crawl_cities(city_list, href_list)