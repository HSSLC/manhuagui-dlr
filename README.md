# manhuagui-dlr

manhuagui下載工具  
* 純Python製作，執行過程不需要任何外部JS環境。  
* 初始化完後就能完全放置，過程中只有主控台視窗，可以繼續使用電腦不受影響。  
* 支援proxy與proxy pool。
  
此為重構的第二版，作為函式庫有更好的模組化，也可以獨立使用。  
若要找第一版（舊版），請切換至[v1](../../tree/v1)分支。

## 使用方式
作為獨立使用請直接執行`mhg_dlr.py`，並依互動提示操作。

## 調整參數
在原始碼`mhg_dlr.py`中有註解標示可以修改參數，其規格如下：
```py
manhuagui.manhuagui_comic(checked_id,
    proxies: list = None,
    proxy_config: dict = { 'mode': 'none','verify': True },
    convert: bool = True,
    tunnel: int = 0,
    skip_existed: bool = False,
    page_delay: float = 1,
    subdomain: str = 'tw'
)
```
其參數分別為：
```
proxies: 代理伺服器列表
    [
        {
            'http': 'http://your.proxy:port',
            'https': 'http://your.proxy:port'
        },
        ...
    ]

proxy_config: 代理伺服器行為設定
    {
        'mode': {'none'（預設，無） | 'single'（單一代理伺服器） | 'pool'（隨機代理伺服器）},
        'verify': {True（預設） | False}
    }

convert: 是否轉檔成jpg
    {True（預設） | False}

tunnel: 圖片來源分流線路
    {0（預設，i） | 1（eu） | 2（us）}

skip_existed: 是否跳過已下載的圖片（當檔名已存在）
    {True | False （預設）}

page_delay: 每頁之間的下載間隔時間（秒）
    float: （預設為0.5）

    如果下載間隔太短會被ban IP好幾天，請自行取決調整大小

subdomain: 主頁面的來源
    {'tw'（預設，繁體中文） | 'www' | ...}

    網址前面的那個子網域，將會影響目錄中的語言
```
## Requirements
* lzstring
* requests
* Pillow
* BeautifulSoup4

```bash
pip install -r requirements.txt
```

## License
引用、重製需標註來源，自做發言禁止。  
僅供個人學術交流使用，勿作為其他用途。