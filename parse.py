# Development by HSSLCreative
# Date: 2020/5/6

import lzstring, re, json
from trans import tr



#這function名是在致敬反反向工程工程師

def packed(functionFrame, a, c, data):
    def e(innerC):
        return ('' if innerC < a else e(int(innerC / a))) + (chr(innerC % a + 29) if innerC % a > 35 else tr(innerC % a, 36))
    c-=1
    d = {}
    while c+1:
        d[e(c)] = e(c) if data[c] == '' else data[c]
        c-=1
    pieces = re.split(r'(\b\w+\b)', functionFrame)
    js = ''.join([d[x] if x in d else x for x in pieces]).replace('\\\'', '\'')
    return json.loads(re.search(r'^.*\((\{.*\})\).*$', js).group(1))
