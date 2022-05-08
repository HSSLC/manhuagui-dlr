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

class manhuagui_comic:
    _host = 'https://tw.manhuagui.com' # tw host name
    _comic_url_base = _host + '/comic/' # comic url base
    _tunnel_base = '.hamreus.com' # image bed base
    _tunnels = ['i', 'eu', 'us']

    def __init__(self, bid, proxies=None, proxy_config={'mode': 'none', 'verify': True}, convert=True, tunnel=0):
        self._bid = bid # book id
        self._url = manhuagui_comic._comic_url_base + str(bid) # comic url
        self._convert = convert # convert to jpg
        try:
            self._tunnel = f'https://{manhuagui_comic._tunnels[tunnel]}{manhuagui_comic._tunnel_base}' # set which image bed to use
        except:
            raise Exception('tunnel %d not exists' % tunnel)
        
        
        self._proxies = proxies # proxy host settings
        try:
            # if: proxy is on and proxy config is not null
            # check: proxy mode
            # check: proxy verify settings
            if proxies and proxy_config and (not proxy_config['mode'] in ['none', 'single', 'pool'] or not type(proxy_config['verify']) is bool):
                raise Exception()
        except:
            raise ValueError("invalid proxy config")
        
        self._proxy_config = proxy_config # proxy action settings

    #private functions
    def _requests_get(self, *args, **kwargs): # requests wrapper of switch proxy config
        if self._proxy_config['mode'] == 'single':
            return requests.get(*args, **kwargs, proxies=self._proxies[0], verify=self._proxy_config['verify'])
        elif self._proxy_config['mode'] == 'pool':
            return requests.get(*args, **kwargs, proxies=random.choice(self._proxies), verify=self._proxy_config['verify'])
        else:
            return requests.get(*args, **kwargs)
    
    def _itr(value, num):
        d = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return '' if value <= 0 else manhuagui_comic._itr(int(value/num), num) + d[value % num]

    def _tr(value, num):
        tmp = manhuagui_comic._itr(value, num)
        return '0' if tmp == '' else tmp

    def _packed(functionFrame, a, c, data): # parse meta data
        e = lambda innerC: ('' if innerC < a else e(int(innerC / a))) + (chr(innerC % a + 29) if innerC % a > 35 else manhuagui_comic._tr(innerC % a, 36))
        c -= 1
        d = {}
        while c + 1:
            d[e(c)] = e(c) if data[c] == '' else data[c]
            c -= 1
        pieces = re.split(r'(\b\w+\b)', functionFrame)
        js = ''.join([d[x] if x in d else x for x in pieces]).replace('\\\'', '\'')
        return json.loads(re.search(r'^.*\((\{.*\})\).*$', js).group(1))

    def _load_chapter_info(self, url): # load chapter info
        lz = lzstring.LZString()
        try:
            res = self._requests_get(url)
        except:
            raise Exception('request failed: %s' % url)
        m = re.match(r'^.*\}\(\'(.*)\',(\d*),(\d*),\'([\w|\+|\/|=]*)\'.*$', res.text)
        return manhuagui_comic._packed(m.group(1), int(m.group(2)), int(m.group(3)), lz.decompressFromBase64(m.group(4)).split('|'))

    def _download_page(self, url, e, m, rawfolder, jpgfolder, filename, max_retry=10, retry_interval=2, skip_existed=False):
        if skip_existed and os.path.isfile(os.path.join(rawfolder, filename)):
            return
        http_header = {'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
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
                res = self._requests_get(url, params={'e': e, 'm': m}, headers=http_header, timeout=10) # download image
                res.raise_for_status()
            except:
                time.sleep(retry_interval)
                continue
            
            # save image file
            file = open(os.path.join(rawfolder, filename), 'wb')
            for chunk in res.iter_content(100000):
                file.write(chunk)
            file.close()

            # convert webp to jpg
            if self._convert:
                im = Image.open(os.path.join(rawfolder, filename))
                im.save(os.path.join(jpgfolder, filename + '.jpg'), 'jpeg')
            return
        raise Exception('Network error: %s' % res.status_code if res else 'OTHER')

    def _download_chapter(self, url, delay): # download chapter
        chapter_info = self._load_chapter_info(url) # load chapter info
        if not chapter_info:
            raise Exception('Failed to get metadata: %s' % url)
        # bname = j['bname']
        chapter_name = chapter_info['cname'] # chapter name

        # replace iligal file path name in title and chapter name
        illegal_path_regex = r'[\\/:*?"<>|]'
        legal_path_bookname = re.sub(illegal_path_regex, '_', self.metadata.title)
        legal_path_chaptername = re.sub(illegal_path_regex, '_', chapter_name)

        # make dir
        rawfolder = os.path.join(legal_path_bookname, 'raw', legal_path_chaptername)
        os.makedirs(rawfolder, exist_ok=True)
        jpgfolder = os.path.join(legal_path_bookname, 'jpg', legal_path_chaptername)
        os.makedirs(jpgfolder, exist_ok=True)

        length = chapter_info['len'] # pages count
        e = chapter_info['sl']['e'] # verify code
        m = chapter_info['sl']['m'] # verify code
        path = chapter_info['path'] # image path
        for i, filename in enumerate(chapter_info['files']):
            page_url = self._tunnel + path + filename
            yield (page_url, filename, length, i) # report progress
            self._download_page(page_url, e, m, rawfolder, jpgfolder, f'{i}_{filename}') # download image
            time.sleep(delay)
    #methods

    def load_info(self): # load book info
        try:
            res = None
            res = self._requests_get(self._url)
            res.raise_for_status()
        except:
            raise Exception("Network error: %s" % res.status_code if res else 'OTHER')

        metadata = {}
        bs = bs4.BeautifulSoup(res.text, 'html.parser')

        # set title
        metadata['title'] = bs.select('.book-title h1')[0].text

        # author
        authors = []
        for author in bs.select('a[href^="/author"]'):
            authors.append(author.text)
        metadata.setdefault('authors', authors)

        # chapters
        section_titles = bs.select('.chapter>h4')
        chapter_sections = bs.select('.chapter-list')
        if not chapter_sections: # some pages store the chapter info in element's attr
            chapters_html = bs4.BeautifulSoup(lzstring.LZString().decompressFromBase64(bs.select('#__VIEWSTATE')[0].attrs.get('value')), 'html.parser')
            section_titles = chapters_html.select('h4')
            chapter_sections = chapters_html.select('.chapter-list')
        
        sections = {}
        chapters = []
        for i, chapter_section in enumerate(chapter_sections):
            # run in each .chapter-list
            section_title = section_titles[i].text
            chapter_section_list = []
            for ul in chapter_section.select('ul'):
                # run in each .chapter-list ul
                chapter_list_in_one_ul = []
                for a in ul.select('a'):
                    # run in each .chapter-list ul li
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
            chapter_url = manhuagui_comic._host + self.metadata.chapters[index]['url']
        elif by == 'sections':
            try:
                chapter_url = manhuagui_comic._host + self.metadata.sections[section][index]['url']
            except:
                raise Exception('Specific section error')
        else:
            raise Exception('Downloading index reference must be chapters or sections')
        for args in self._download_chapter(chapter_url, delay):
            callback(*args)
