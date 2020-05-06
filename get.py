import requests, re, lzstring
from parse import packed

lz = lzstring.LZString()

def get(url):
    print('連線中...')
    try:
        res = requests.get(url)
    except:
        print('%s下載失敗' % url)
        return False
    m = re.match(r'^.*\}\(\'(.*)\',(\d*),(\d*),\'([\w|\+|\/|=]*)\'.*$', res.text)
    return packed(m.group(1), int(m.group(2)), int(m.group(3)), lz.decompressFromBase64(m.group(4)).split('|'))
