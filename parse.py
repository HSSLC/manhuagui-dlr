import lzstring, re, json
from trans import tr




def packed(functionFrame, a, c, data):
    def deb(ic, ia):
        if ic < ia:
            return ''
        else:
            return e(int(ic / ia))
    def e(innerC):
        tmp1 = deb(innerC, a)
        innerC = innerC % a
        tmp2 = tr(innerC, 36)
        tmp3 = chr(innerC + 29)
        return tmp1 + [tmp2, tmp3][innerC > 35]
    c-=1
    d = dict();
    while c+1:
        d[e(c)] = [data[c], e(c)][data[c] == '']
        c-=1
    pieces = re.split(r'(\b\w+\b)', functionFrame)
    js = ''.join([d[x] if x in d else x for x in pieces])
    return json.loads(re.search(r'^.*\((\{.*\})\).*$', js).group(1))