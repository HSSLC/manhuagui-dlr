import lzstring
import re
import os
import requests
import random
import json
import bs4
import time
from PIL import Image
from types import SimpleNamespace

class manhuagui:
    _host = 'https://tw.manhuagui.com'
    _comic_url_base = _host + '/comic/'
    __tunnel_base = '.hamreus.com'
    _tunnels = ['i', 'eu', 'us']

    def __init__(self, bid, proxies=None, proxy_config={'mode': 'none', 'verify': True}, convert=True, tunnel=0):
        self.__bid = bid
        self.__url = manhuagui._comic_url_base + str(bid)
        self.__convert = convert
        try:
            self.__tunnel = manhuagui.__tunnel_base + manhuagui._tunnels[tunnel]
        except:
            raise Exception('tunnel %d not exists' % tunnel)
        
        
        self.__proxies = proxies
        try:
            if proxies and proxy_config and (not proxy_config['mode'] in ['none', 'single', 'pool'] or not type(proxy_config['verify']) is bool):
                raise Exception()
        except:
            raise ValueError("invalid proxy config")
        self.__proxy_config = proxy_config

    #private functions
    def __requests_get(self, *args, **kwargs):
        if self.__proxy_config['mode'] == 'single':
            return requests.get(*args, **kwargs, proxies=self.__proxies[0], verify=self.__proxy_config['verify'])
        elif self.__proxy_config['mode'] == 'pool':
            return requests.get(*args, **kwargs, proxies=random.choice(self.__proxies), verify=self.__proxy_config['verify'])
        else:
            return requests.get(*args, **kwargs)
    
    def __itr(value, num):
        d = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return '' if value <= 0 else manhuagui.__itr(int(value/num), num) + d[value % num]

    def __tr(value, num):
        tmp = manhuagui.__itr(value, num)
        return '0' if tmp == '' else tmp

    def __packed(functionFrame, a, c, data):
        e = lambda innerC: ('' if innerC < a else e(int(innerC / a))) + (chr(innerC % a + 29) if innerC % a > 35 else manhuagui.__tr(innerC % a, 36))
        c-=1
        d = {}
        while c+1:
            d[e(c)] = e(c) if data[c] == '' else data[c]
            c-=1
        pieces = re.split(r'(\b\w+\b)', functionFrame)
        js = ''.join([d[x] if x in d else x for x in pieces]).replace('\\\'', '\'')
        return json.loads(re.search(r'^.*\((\{.*\})\).*$', js).group(1))

    def __load_ch_info(self, url):
        lz = lzstring.LZString()
        try:
            res = self.__requests_get(url)
        except:
            raise Exception('request failed: %s' % url)
        m = re.match(r'^.*\}\(\'(.*)\',(\d*),(\d*),\'([\w|\+|\/|=]*)\'.*$', res.text)
        return manhuagui.__packed(m.group(1), int(m.group(2)), int(m.group(3)), lz.decompressFromBase64(m.group(4)).split('|'))

    def __download_page(self, url, e, m, rawfolder, jpgfolder, filename, max_retry=10, retry_interval=2):
        h = {'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.manhuagui.com/',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        for _ in range(max_retry):
            try:
                res = None
                res = self.__requests_get(url, params={'e':e, 'm':m}, headers = h, timeout=10)
                res.raise_for_status()
            except:
                time.sleep(retry_interval)
                continue
            file = open(os.path.join(rawfolder, filename), 'wb')
            for chunk in res.iter_content(100000):
                file.write(chunk)
            file.close()
            if self.__convert:
                im = Image.open(os.path.join(rawfolder, filename))
                im.save(os.path.join(jpgfolder, filename + '.jpg'), 'jpeg')
            return
        raise Exception('network error: %s' % res.status_code if res else 'OTHER')

    def __download_chapter(self, url, delay):
        j = self.__load_ch_info(url)
        if not j:
            raise Exception('failed to get metadata: %s' % url)
        #bname = j['bname']
        cname = j['cname']

        iligal_path_regex = r'[\\/:*?"<>|]'
        pathable_bname = re.sub(iligal_path_regex, '_', self.metadata.title)
        pathable_cname = re.sub(iligal_path_regex, '_', cname)

        rawfolder = os.path.join(pathable_bname, 'raw', pathable_cname)
        os.makedirs(rawfolder, exist_ok=True)
        jpgfolder = os.path.join(pathable_bname, 'jpg', pathable_cname)
        os.makedirs(jpgfolder, exist_ok=True)

        length = j['len']
        e = j['sl']['e']
        m = j['sl']['m']
        path = j['path']
        for i, filename in enumerate(j['files']):
            page_url = self.__tunnel + path + filename
            yield (page_url, filename, length, i)
            self.__download_page(page_url, e, m, rawfolder, jpgfolder, '%d_%s' % (i, filename))
            time.sleep(delay)
    #methods

    def load_info(self):
        try:
            res = None
            res = self.__requests_get(self.__url)
            res.raise_for_status()
        except:
            raise Exception("network error: %s" % res.status_code if res else 'OTHER')

        metadata = {}
        bs = bs4.BeautifulSoup(res.text, 'html.parser')

        #title
        metadata.setdefault('title', bs.select('.book-title h1')[0].text)

        #author
        authors = []
        for author in bs.select('a[href^="/author"]'):
            authors.append(author.text)
        metadata.setdefault('authors', authors)

        #chapters
        section_titles = bs.select('.chapter>h4')
        chapter_sections = bs.select('.chapter-list')
        if not chapter_sections:
            chapters_html = bs4.BeautifulSoup(lzstring.LZString().decompressFromBase64(bs.select('#__VIEWSTATE')[0].attrs.get('value')), 'html.parser')
            section_titles = chapters_html.select('h4')
            chapter_sections = chapters_html.select('.chapter-list')
        
        sections = {}
        chapters = []
        for i, chapter_section in enumerate(chapter_sections):
            #run in each .chapter-list
            section_title = section_titles[i].text
            chapter_section_list = []
            for ul in chapter_section.select('ul'):
                #run in each .chapter-list ul
                chapter_list_in_one_ul = []
                for a in ul.select('a'):
                    #run in each .chapter-list ul li
                    chapter_list_in_one_ul.append({'chname': a.attrs['title'], 'url': a.attrs['href']})

                chapter_list_in_one_ul.reverse()
                chapters += chapter_list_in_one_ul
                chapter_section_list += chapter_list_in_one_ul

            sections.setdefault(section_title, chapter_section_list)
        
        metadata.setdefault('sections', sections)
        metadata.setdefault('chapters', chapters)

        #save
        self.metadata = SimpleNamespace(**metadata)
    
    def download_chapter(self, index, delay=0.5, callback=lambda page_url, filename, length, i: print('%s\n%s/%s...\r' % (page_url, i + 1, length), end=''), by='chapters', section=None):
        if by == 'chapters':
            chapter_url = manhuagui._host + self.metadata.chapters[index]['url']
        elif by == 'sections':
            try:
                chapter_url = manhuagui._host + self.metadata.sections[section][index]['url']
            except:
                raise Exception('specific section error')
        else:
            raise Exception('download index reference must be chapters or sections')
        for args in self.__download_chapter(chapter_url, delay):
            callback(*args)
