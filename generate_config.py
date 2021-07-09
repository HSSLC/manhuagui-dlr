# Development by HSSLCreative
# Date: 2020/5/6

import json

def generate_config(title, creator, language='zh', folder='jpg', width=800, height=1280, cover='', cid=''):
    config = {}
    config['title'] = title
    config['creator'] = creator
    config['direction'] = 'rl'
    config['language'] = language
    config['folder'] = folder
    config['width'] = width
    config['height'] = height
    config['cover'] = cover
    config['cid'] = cid
    j = json.dumps(config)
    return j
