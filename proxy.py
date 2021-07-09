import requests
import random

#none for no proxy
#single for single proxy
#pool for random proxy in proxy pool
proxy_config = 'single'
verify = False

#add your proxy list in proxy pool
proxy_pool = [
    {
        'http': 'http://localhost:8888',
        'https': 'http://localhost:8888'
    }
]

#set your single proxy in below
proxy = {
    'http': 'http://localhost:8888',
    'https': 'http://localhost:8888'
}

def requests_get(*args, **kwargs):
    if proxy_config == 'single':
        return requests.get(*args, **kwargs, proxies=proxy, verify=verify)
    elif proxy_config == 'pool':
        return requests.get(*args, **kwargs, proxies=random.choice(proxy_pool), verify=verify)
    else:
        return requests.get(*args, **kwargs)
