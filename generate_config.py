import json

def generate_config(title, creator, language='zh', folder='jpg', width=800, height=1280, cover=''):
    config = {}
    config['title'] = title
    config['creator'] = creator
    config['language'] = language
    config['folder'] = folder
    config['width'] = width
    config['height'] = height
    config['cover'] = cover
    j = json.dumps(config)
    return j
