import urllib2
import re
from pandas import *
from bs4 import BeautifulSoup

#main_url = 'http://www.wowdb.tw/item-14159.html'
main_url = 'http://www.wowdb.tw/item-'

def getItemName(itemid):
    url = main_url + str(itemid) + '.html'
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html)
    title = soup.find(id='itemtitle')
    title = str(title)
    pattern = r"(.+)>(.+)(</h1>)"
    match = re.match(pattern, title)
    if match:
        return match.group(2)
    else:
        return str(itemid) + ' does not match anything!'

def main():
    with open('highCorrItemName.dat', 'wb') as f_write:
        f_alliance = read_csv('../corr_result/HighCorr/alliance')
        for itemid in f_alliance['Item ID']:
            f_write.write(getItemName(int(itemid))+'\n')
        f_horde = read_csv('../corr_result/HighCorr/horde')
        for itemid in f_horde['Item ID']:
            f_write.write(getItemName(int(itemid))+'\n')


if __name__ == '__main__':
    main()
        

