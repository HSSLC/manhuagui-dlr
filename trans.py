def itr(value, num):
    d = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if value <= 0:
        return ''
    else:
        return itr(int(value/num), num) + d[value % num]
def tr(value, num):
    tmp = itr(value, num)
    if tmp == '':
        return '0'
    else:
        return tmp
