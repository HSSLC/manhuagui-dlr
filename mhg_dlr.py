import os
import manhuagui

# test
m = manhuagui.manhuagui_comic(17332, skip_existed=True)
m.download_chapter(1, by='sections', section=1)