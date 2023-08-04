from unittest import skip
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

HTTP_HEADER = {
    'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://www.manhuagui.com/',
    'sec-fetch-dest': 'image',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
}



class manhuagui_comic:
    _CHANNEL_BASE = '.hamreus.com' # image bed base
    _CHANNELS = ['i', 'eu', 'us']
    _DOWNLOAD_FOLDER = 'Downloads'

    def __init__(self, bid : int, proxies : list=None, proxy_config : dict={'mode': 'none', 'verify': True}, convert : bool=True, tunnel : int=0, skip_existed : bool=False, page_delay : float=1, subdomain : str='tw'):
        self._host = f"https://{subdomain}.manhuagui.com"
        self._comic_url_base = self._host + '/comic/'
        
        self._bid = bid # book id
        self._url = self._comic_url_base + str(bid) # comic url
        self._convert = convert # convert to jpg
        self._page_delay = page_delay # delay between pages

        try:
            self._tunnel = f'https://{self._CHANNELS[tunnel]}{self._CHANNEL_BASE}' # set which image bed to use
        except:
            raise Exception('tunnel %d not exists' % tunnel)
        
        
        self._proxies = proxies # proxy host settings
        # if: proxy is on and proxy config is not null
        # check: proxy mode
        # check: proxy verify settings
        if proxies and proxy_config and (not proxy_config['mode'] in ['none', 'single', 'pool'] or not type(proxy_config['verify']) is bool):
            raise ValueError("invalid proxy config")
        
        self._proxy_config = proxy_config # proxy action settings
        self._skip_existed = skip_existed # skip existed file

        # initialize metadata
        self._load_book_metadata()
    
    
    def _load_book_metadata(self): # load book info
        try:
            res = None
            res = self._requests_get(self._url)
            res.raise_for_status()
        except:
            raise Exception(f"Network error: {res.status_code if res else 'OTHER'}")

        metadata = {}
        bs = bs4.BeautifulSoup(res.text, 'html.parser')

        # set title
        metadata['title'] = bs.select('.book-title h1')[0].text

        # author
        authors = []
        for author in bs.select('a[href^="/author"]'):
            authors.append(author.text)
        metadata['authors'] = authors

        # chapters
        section_titles = bs.select('.chapter>h4')
        chapter_sections = bs.select('.chapter-list')
        if not chapter_sections: # some pages store the chapter info in element's attr
            chapters_html = bs4.BeautifulSoup(lzstring.LZString().decompressFromBase64(bs.select('#__VIEWSTATE')[0].attrs.get('value')), 'html.parser')
            section_titles = chapters_html.select('h4')
            chapter_sections = chapters_html.select('.chapter-list')
        
        sections = []
        chapters = []
        for i, chapter_section in enumerate(chapter_sections):
            # run in each .chapter-list
            section_title = section_titles[i].text
            section_chapter_list = []
            for ul in chapter_section.select('ul'):
                # run in each .chapter-list ul
                chapter_list_in_one_ul = []
                for a in ul.select('a'):
                    # run in each .chapter-list ul li
                    chapter_list_in_one_ul.append({'chapter_name': a.attrs['title'], 'url': a.attrs['href']})

                chapter_list_in_one_ul.reverse()
                chapters += chapter_list_in_one_ul
                section_chapter_list += chapter_list_in_one_ul

            sections.append({'title': section_title, 'list': section_chapter_list})
        
        metadata['sections'] = sections
        metadata['chapters'] = chapters

        #save
        self.metadata = SimpleNamespace(**metadata)
        self.raw_metadata = metadata

    def write_metadata(self):
        chapter_folder = os.path.join(self._DOWNLOAD_FOLDER, self.metadata.title)
        os.makedirs(chapter_folder, exist_ok=True)
        with open(os.path.join(chapter_folder, 'config.json'), 'w', encoding='utf-8') as f:
            config = {
                'title': self.metadata.title,
                'authors': '、'.join(self.metadata.authors),
                'direction': 'rl',
                'language': 'zh',
                'folder': 'jpg',
                'width': 800,
                'height': 1280,
                'cover': '',
                'bid': self._bid,
            }
            json.dump(config, f, ensure_ascii=False, indent=4)
    #private functions
    def _requests_get(self, *args, **kwargs): # requests wrapper of switch proxy config
        if self._proxy_config['mode'] == 'single':
            return requests.get(*args, **kwargs, proxies=self._proxies[0], verify=self._proxy_config['verify'])
        elif self._proxy_config['mode'] == 'pool':
            return requests.get(*args, **kwargs, proxies=random.choice(self._proxies), verify=self._proxy_config['verify'])
        else:
            return requests.get(*args, **kwargs)

    def _get_chapter_struct(self, url): # load chapter info
        lz = lzstring.LZString()
        try:
            res = self._requests_get(url)
        except:
            raise Exception(f'Request failed: {url}')
        m = re.match(r'^.*\}\(\'(.*)\',(\d*),(\d*),\'([\w|\+|\/|=]*)\'.*$', res.text)
        return _packed(m.group(1), int(m.group(2)), int(m.group(3)), lz.decompressFromBase64(m.group(4)).split('|'))

    def _download_page(self, url : str, e, m, rawfolder, jpgfolder, filename, max_retry=10, retry_interval=2):
        if self._skip_existed and os.path.isfile(os.path.join(rawfolder, filename)):
            # return True if file skipped
            return True
        
        for i in range(max_retry):
            try:
                res = None
                res = self._requests_get(url, params={'e': e, 'm': m}, headers=HTTP_HEADER, timeout=10) # download image
                res.raise_for_status()
            except Exception as e:
                print(f"Error: {e}, retrying ({i + 1})...")
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

            # return when success
            return
        
        # if failed
        raise Exception('Network error: %s' % res.status_code if res else 'OTHER')

    def _download_chapter(self, url : str): # download chapter
        """Download a chapter

        params:
            url : /comic/xxxxx/xxxxx.html
        
        return:
            yield (page_url, filename, total_page_count, current_page)
        """

        # load chapter info
        chapter_info = self._get_chapter_struct(url)

        # get chapter name
        if not chapter_info:
            raise Exception(f"Failed to get metadata: {url}")
        chapter_name = chapter_info['cname'] # chapter name

        print(f"{chapter_name}...")

        # replace iligal file path name in title and chapter name
        illegal_path_regex = r'[\\/:*?"<>|]'
        legal_path_bookname = re.sub(illegal_path_regex, '_', self.metadata.title)
        legal_path_chaptername = re.sub(illegal_path_regex, '_', chapter_name)

        # make dir
        rawfolder = os.path.join(self._DOWNLOAD_FOLDER, legal_path_bookname, 'raw', legal_path_chaptername)
        os.makedirs(rawfolder, exist_ok=True)
        jpgfolder = os.path.join(self._DOWNLOAD_FOLDER, legal_path_bookname, 'jpg', legal_path_chaptername)
        os.makedirs(jpgfolder, exist_ok=True)

        # get chapter info
        length = chapter_info['len']    # pages count
        e = chapter_info['sl']['e']     # verify code
        m = chapter_info['sl']['m']     # verify code
        path = chapter_info['path']     # image path

        # download pages
        for i, filename in enumerate(chapter_info['files']):
            page_url = self._tunnel + path + filename
            yield (page_url, filename, length, i) # report progress
            # download image
            if not self._download_page(page_url, e, m, rawfolder, jpgfolder, f'{i}_{filename}'): # return True means file skiped
                time.sleep(self._page_delay) # delay when file is not skiped

    
    def download_chapter(self, index, callback=None, by='chapters', section=None):
        """Download a chapter, by index in chapters or section.chapters
        
        params:
            index : index of chapter
            callback : callback function during downloading, default is print progress
            by : download by chapters or sections
            section : section index, only used when by is sections
        """

        # default callback
        if callback is None:
            callback = lambda page_url, filename, total_page_count, current_page_number: print(f"{page_url} ({current_page_number + 1}/{total_page_count})")
        
        # get url by index
        if by == 'chapters':
            chapter_url = self._host + self.metadata.chapters[index]['url']
        elif by == 'sections':
            try:
                chapter_url = self._host + self.metadata.sections[section]['list'][index]['url']
            except:
                raise Exception('Specific section error')
        else:
            raise Exception('Downloading index reference must be chapters or sections')
        
        # download chapter
        for progress in self._download_chapter(chapter_url):
            callback(*progress)

def convert_base(value, base):
    """Converts an integer to a string in any base"""
    d = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    if value == 0:
        return '0'

    result = ''
    while value > 0:
        remainder = value % base
        result = d[remainder] + result
        value //= base

    return result

def _packed(functionFrame, a, c, data): # parse meta data
    e = lambda innerC: ('' if innerC < a else e(int(innerC / a))) + (chr(innerC % a + 29) if innerC % a > 35 else convert_base(innerC % a, 36))
    c -= 1
    d = {}
    while c + 1:
        d[e(c)] = e(c) if data[c] == '' else data[c]
        c -= 1
    pieces = re.split(r'(\b\w+\b)', functionFrame)
    js = ''.join([d[x] if x in d else x for x in pieces]).replace('\\\'', '\'')
    return json.loads(re.search(r'^.*\((\{.*\})\).*$', js).group(1))