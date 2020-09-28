# Development by HSSLCreative
# Date: 2020/5/6

def itr(value, num):
    d = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return '' if value <= 0 else itr(int(value/num), num) + d[value % num]
def tr(value, num):
    tmp = itr(value, num)
    return '0' if tmp == '' else tmp
