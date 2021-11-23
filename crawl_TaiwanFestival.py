import requests
import bs4
import pymongo


urlbase = 'https://www.taiwan.net.tw/'
current_page = 'm1.aspx?sNo=0001019'

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
newdb = myclient["New_ComingoDB"]
newcol = newdb['New_Taiwan_Festival']
# newcol.create_index( ["month", "name", "地址"] , name="FestivalTimePlaceIndex", unique=True)

NorthCities = ["新北市", "臺北市", "基隆市", "宜蘭縣", "新竹縣", "新竹市", "桃園市"]
CentralCities = ["臺中市", "苗栗縣", "彰化縣", "南投縣", "雲林縣"]
SouthCities = ["嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣"]
EastCities = ["花蓮縣", "臺東縣"]
OffshoreCities = ["澎湖縣", "金門縣", "連江縣"]



def get_address(url):
    target = url
    X = target.split(',')[1]
    Y = target.split(',')[0]

    return X[:X.find("&")], Y[Y.rfind("daddr=") + len("daddr="):]

def change_region(region_num):
    region_name = ''
    if region_num == 1:
        region_name = '北部地區'
    elif region_num == 2:
        region_name = '東部地區'
    elif region_num == 3:
        region_name = '中部地區'
    elif region_num == 4:
        region_name = '南部地區'
    elif region_num == 5:
        region_name = '外島地區'
    return '&keyString=^' + str(region_num), region_name


def change_month(mon):
    return '^^' + str(mon) + '^^', str(mon)


def turn_page(p):
    return '&page=' + str(p)


def crawl_activities(region, month):

    region_href, region = change_region(region)
    mon_href, month = change_month(month)

    print("month : " + str(month) + " region : " + region)

    # 頁數上限
    upper_page = 10

    # 總共頁數
    all_pages = 1

    for p in range(1, upper_page):

        # 若目前page已超過總共頁數上限 跳出
        if p > int(all_pages):
            break
        url = urlbase + current_page + region_href + mon_href + turn_page(p)
        print(url)
        htmlfile = requests.get(url)
        objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

        # 取得頁數上限
        all_pages = objSoup.select('div.sort-item > span > b')[2].text

        calenderObjs = objSoup.find('ul', 'columnBlock-list').find_all('li')  # 給find_all
        # print(calenderObj)
        for calenderObj in calenderObjs:
            img_href = calenderObj.find('img', 'lazyload')['data-src']
            hash_tag = calenderObj.select('div.hashtag > span')[0].text
            name = calenderObj.find('a')['title']
            detail_href = calenderObj.find('a')['href']
            date = calenderObj.find('span', 'date').text.split()[0]
            content = calenderObj.find('p').text

            dict = {'month' : month, 'region' : region, 'name': name, 'image' : img_href,
                 'hashtag' : hash_tag, 'content' : content}

            # 進入festival 單獨頁面
            detailHtml = requests.get(urlbase + detail_href)
            detailSoup = bs4.BeautifulSoup(detailHtml.text, 'lxml')

            tagSoup = detailSoup.find('dl', 'info-table').find_all('dt')
            valSoup = detailSoup.find('dl', 'info-table').find_all('dd')

            for i in range(0, len(tagSoup)):
                tag_name = tagSoup[i].text
                tag_val = valSoup[i]

                if tag_name == '網站：':
                    try:
                        dict['網站'] = tag_val.text
                        tag_href = valSoup[i].find('a')['href']
                        dict['網站_href'] = tag_href
                    except TypeError:
                        tag_href = 'none'
                        pass
                elif tag_name == '地址：':
                        i = 0
                        address_list = []
                        latitude_list = []
                        for address in tag_val:
                            try:
                                tag_href = address.find('a')['href']

                                X, Y = get_address(tag_href)
                            except TypeError:
                                tag_href = 'none'
                                pass
                            # if i == 0:
                            city = address.text[:3]

                            if region == "北部地區" and city in NorthCities:
                                dict['city'] = city
                                dict['地址'] = address.text
                                dict['X'] = X
                                dict['Y'] = Y
                                print(dict)
                                newdict = {}
                                newdict.update(dict)
                                newcol.insert_one(newdict)
                            elif region == "中部地區" and city in CentralCities:
                                dict['city'] = city
                                dict['地址'] = address.text
                                dict['X'] = X
                                dict['Y'] = Y
                                print(dict)
                                newdict = {}
                                newdict.update(dict)
                                newcol.insert_one(newdict)
                            elif region == "南部地區" and city in SouthCities:
                                dict['city'] = city
                                dict['地址'] = address.text
                                dict['X'] = X
                                dict['Y'] = Y
                                print(dict)
                                newdict = {}
                                newdict.update(dict)
                                newcol.insert_one(newdict)
                            elif region == "東部地區" and city in EastCities:
                                dict['city'] = city
                                dict['地址'] = address.text
                                dict['X'] = X
                                dict['Y'] = Y
                                print(dict)
                                newdict = {}
                                newdict.update(dict)
                                newcol.insert_one(newdict)
                            elif region == "外島地區" and city in OffshoreCities:
                                dict['city'] = city
                                dict['地址'] = address.text
                                dict['X'] = X
                                dict['Y'] = Y
                                print(dict)
                                newdict = {}
                                newdict.update(dict)
                                newcol.insert_one(newdict)

                        #     else:
                        #         address_list.append(address.text)
                        #         latitude_list.append((X,Y))
                        #     i = i+1
                        # print(address_list)
                        # print(latitude_list)
                        # dict['更多地址'] = address_list
                        # dict['更多經緯'] = latitude_list
                else:
                    dict[tag_name[:-1]] = tag_val.text


        # 若目前page已達總共頁數上限 跳出
        if p == all_pages:
            break


if __name__ == '__main__':
    for mon in range(1, 13):
        for region in range(1, 6):
            crawl_activities(region, mon)
