import requests
import bs4
import pymongo

urlbase = 'https://www.taiwan.net.tw/'
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Comingo_Collect_Data"]
mycol = mydb['Cities_Region_ViewHref']

def get_regions():

    current_place = 'm1.aspx?sNo=0001016'

    htmlfile = requests.get(urlbase + current_place)
    objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

    region_dict = {}
    regions_soup = objSoup.find('ul', 'twmap').find_all('a')
    for region_soup in regions_soup:
        region = region_soup.getText()
        region_href = region_soup['href']
        region_dict[region] = region_href

    return region_dict


def get_citys(region_dict):


    for region, href in region_dict.items():
        htmlfile = requests.get(urlbase+href)
        objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

        citiesSoup = objSoup.find('ul', 'circularbtn-list').find_all('li')
        for citySoup in citiesSoup:
            city_Name = citySoup.find('span', 'circularbtn-title').text
            city_href = citySoup.find('a', 'circularbtn')['href']
            cities_dict = {"city" : city_Name, "region" : region, "href" : city_href}
            mycol.insert_one(cities_dict)


if __name__ == '__main__':
    region_dict = get_regions()
    get_citys(region_dict)
    print("finish crawl")

