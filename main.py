# Development by HSSLCreative
# Date: 2020/5/6

import re, time, bs4, requests, lzstring
from download import downloadCh
from generate_config import generate_config

check_re = r'^https?://([a-zA-Z0-9]*\.)?manhuagui\.com/comic/([0-9]+)/?'
request_url = 'https://tw.manhuagui.com/comic/%s'
host = 'https://tw.manhuagui.com'

def main():
    print('僅供學術研究交流使用，勿作為商業用途')
    while True:
        print('輸入URL:')
        #格式:https://*.manhuagui.com/comic/XXXXX
        #是否進入章節都沒關係
        #例如https://*.manhuagui.com/comic/XXXXX/XXXXX.html也行
        #反正要得只有id
        url = input()
        try:
            checked_id = re.match(check_re, url).group(2)
            break
        except:
            print('無效的網址')
            continue
    try:
        res = requests.get(request_url % checked_id)
        res.raise_for_status()
    except:
        print('錯誤:可能是沒網路或被ban ip?')
        return
    bs = bs4.BeautifulSoup(res.text, 'html.parser')
    title = bs.select('.book-title h1')[0]
    print('標題: %s' % title.text)
    authors_link = bs.select('a[href^="/author"]')
    authors = []
    for author in authors_link:
        authors.append(author.text)
    authors = '、'.join(authors)
    config_json = generate_config(title.text, authors)
    links = bs.select('.chapter-list a')
    if not links:
        links = bs4.BeautifulSoup(lzstring.LZString().decompressFromBase64(bs.select('#__VIEWSTATE')[0].attrs.get('value')), 'html.parser').select('.chapter-list a')
    links.reverse()
    ch_list = []
    for link in links:
        ch_list.append([link.attrs['title'], link.attrs['href']])
    print('編號 對應名稱')
    for ch_index in range(len(ch_list)):
        ch = ch_list[ch_index]
        print(str(ch_index).ljust(4), ch[0])
    print('輸入上列編號(ex:1-2 5-8 10 -> 1, 2, 5, 6, 7, 8, 10)')
    choose_chs = input()
    tmp = re.findall(r'[0-9]+\-?[0-9]*', choose_chs)
    choose_block_list = []
    config_writed = False
    for block in tmp:
        try:
            block = block.split('-')
            for i in range(len(block)):
                block[i] = int(block[i])
                if block[i] > len(ch_list) or block[i] < 0:
                    raise Exception('out of range')
            if len(block) >= 2:
                if block[1] < block[0]:
                    block[0], block[1] = block[1], block[0]
                choose_block_list.append([block[0], block[1]])
            else:
                choose_block_list.append([block[0], block[0]])
        except:
            continue
    for area in choose_block_list:
        block = ch_list[area[0]:area[1]+1]
        for ch in block:
            if not config_writed:
                downloadCh(host + ch[1], config_json)
            else:
                downloadCh(host + ch[1])
                config_writed = True
            print('延遲5秒...')
            #每話間隔5秒
            time.sleep(5)
main()

#各話間會延遲5秒 各頁間會延遲1秒
#防止被ban ip
#目前延遲數值是保守值 可自行依注解更改
#反正執行後就能afk了
