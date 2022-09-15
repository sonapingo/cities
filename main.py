import json
import random
import time

import requests
from bs4 import BeautifulSoup


def get_request(url, attr):
    global ret
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
    trytimes = 10
    for i in range(trytimes):
        try:
            ret = requests.get(url, headers=headers, timeout=5)
            time.sleep(random.randint(0, 1))
            if ret.status_code == 200:
                break
        except:
            print(f'request failed {i} time')
    ret.encoding = 'utf-8'
    # print(ret.url)
    # print(ret.status_code)

    soup = BeautifulSoup(ret.text, 'html.parser')
    list = soup.find_all('tbody')[3]
    if attr:
        trs = list.find_all('tr', attrs={'class': attr})
    else:
        trs = list.find_all('tr')
    return trs


def get_cities(html):
    datas = {}
    for provinces in html:
        for province in provinces:
            province_name = province.a.get_text()
            datas[province_name] = {}
            province_url = base_url + province.a.get('href')
            print(province_name)
            cities = get_request(province_url, 'citytr')
            city_dict = {}
            for city in cities:
                city_name = city.find_all('a')[1].get_text()
                city_url = base_url + city.find_all('a')[1].get('href')
                print(city_name)
                counties = get_request(city_url, 'countytr')
                if len(counties) == 0:
                    towns = get_request(city_url, 'towntr')
                    town_list = []
                    for town in towns:
                        town_name = town.find_all('a')[1].get_text()
                        print(town_name)
                        town_list.append(town_name)
                    city_dict[city_name] = town_list
                    datas[province_name].update(city_dict)
                else:
                    city_dict[city_name] = {}
                    county_dict = {}
                    for county in counties:
                        if len(county.find_all('a')) == 0:
                            continue
                        else:
                            county_name = county.find_all('a')[1].get_text()
                            city_after_url = city.find_all('a')[1].get('href')
                            city_url_list = city_after_url.split('/')
                            city_num = city_url_list[0]
                            county_url = base_url + city_num + '/' + county.find_all('a')[1].get('href')
                            print(county_name)
                            towns = get_request(county_url, 'towntr')
                            town_list = []
                            for town in towns:
                                town_name = town.find_all('a')[1].get_text()
                                print(town_name)
                                town_list.append(town_name)
                            county_dict[county_name] = town_list
                            city_dict[city_name].update(county_dict)
                            datas[province_name].update(city_dict)
    return datas


def writedatas(datas):
    outfile = 'datas/cities.json'
    with open(outfile, "w", encoding='utf-8') as f:
        f.write(json.dumps(datas, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/'
    table = get_request(base_url, 'provincetr')
    datas = get_cities(table)
    writedatas(datas)
    print(datas)
