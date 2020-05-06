import re, time, bs4, requests
from download import downloadCh

baseUrl = 'https://www.manhuagui.com/comic/'
host = 'https://www.manhuagui.com'

def main():
    print('僅供學術研究交流使用，勿作為商業用途')
    while True:
        print('輸入URL:')
        url = input()
        try:
            checked_url = re.match(r'^(' + baseUrl + '[0-9]+/?)', url).group(1)
            break
        except:
            print('無效的網址')
            continue
    try:
        res = requests.get(checked_url)
        res.raise_for_status()
    except:
        print('錯誤:可能是沒網路或被ban ip?')
        return
    bs = bs4.BeautifulSoup(res.text, 'html.parser')
    title = bs.select('.book-title h1')[0]
    print('標題: %s' % title.text)
    links = bs.select('.chapter-list a')
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
            downloadCh(host + ch[1])
            print('延遲5秒...')
            time.sleep(5)
main()

#各話間會延遲5秒 各頁間會延遲2秒
#防止被ban ip
#延遲數值是保守值 可自行依注解更改