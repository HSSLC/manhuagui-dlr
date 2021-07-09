# Development by HSSLCreative
# Date: 2020/5/6

import re, lzstring
from parse import packed
from proxy import requests_get

lz = lzstring.LZString()

def get(url):
    print('connecting...')
    try:
        res = requests_get(url)
    except:
        print('%s取得失敗' % url)
        return False
    m = re.match(r'^.*\}\(\'(.*)\',(\d*),(\d*),\'([\w|\+|\/|=]*)\'.*$', res.text)
    return packed(m.group(1), int(m.group(2)), int(m.group(3)), lz.decompressFromBase64(m.group(4)).split('|'))
