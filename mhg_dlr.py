import os
import manhuagui

# test
m = manhuagui.manhuagui_comic(17332, skip_existed=True)
m.load_info()

m.download_chapter(0)