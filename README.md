# manhuagui-dlr

manhuagui下載器  
純Python製作，執行過程不需要任何外部JS環境

包含自動webp轉檔jpg，可以選擇關閉

初始化完後就能完全放置，過程中只有主控台視窗，可以繼續使用電腦不受影響  

支援proxy與proxy pool，設定方式請參考更多資訊

執行完後可參考[這裡](https://github.com/HSSLC/kc-generator)做下一步處理成mobi檔案

## requirement:  
* lzstring
* requests
* Pillow
* BeautifulSoup4



# 附註
自作發言禁止。  
僅供學術研究交流使用，勿作為其他用途。

# 更多資訊
https://incognitas.net/works/downloader-1

## 選用功能
圖片檔名預設情況下是用URI編碼過的，若要在下載時維持原文檔名，可以去`download.py`將解碼的片段去除註解  
```
# filename = str(counter) + '_' + os.path.basename(urllib.parse.unquote(url))
```
預設為不解碼是因為非ascii字元可能會出現的問題較多，如亂碼或是容易出現在搜尋結果中