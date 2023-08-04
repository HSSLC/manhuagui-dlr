import manhuagui
import re
import time

# get book id
check_re = r'^(https?://([a-zA-Z0-9]*\.)?manhuagui\.com/comic/)?([0-9]+)/?'
print('僅供學術交流使用，勿作為其他用途')
url = input('輸入URL或是ID: ')
try:
    checked_id = int(re.match(check_re, url).group(3))
except:
    print('無效的網址')
    exit(1)

# create book object
# 如有調整轉檔、proxy、下載間隔時間、線路分流等需求，請修改以下的建構參數
manhuagui_book = manhuagui.manhuagui_comic(checked_id)
chapters = manhuagui_book.metadata.chapters

print('編號\t章節名稱')
for i, chapter in enumerate(chapters):
    print(f"{i}\t{chapter['chapter_name']}")
print()
print('輸入要下載的章節編號，連續區段以 - 連接，多個連續區段以空白分隔')
print('ex: 輸入1-2 5-8 10 將會下載編號 1, 2, 5, 6, 7, 8, 10 的章節')
select_exp = input()
select_exp = select_exp.split(' ')
select_chapters = []
for exp in select_exp:
    if '-' in exp:
        start, end = exp.split('-')
        select_chapters += list(range(int(start), int(end)+1))
    else:
        select_chapters.append(int(exp))

manhuagui_book.write_metadata()
for chapter_index in select_chapters:
    manhuagui_book.download_chapter(chapter_index)
    time.sleep(5)