from pathlib import Path
from PIL import Image
from win32com.shell import shell, shellcon
import win32api, win32con, win32ui, win32gui, os

def load_state(file):
    ret = []
    with open(file, "r") as f:
        for line in f:
            args = line.split(',')
            ret.append((args[0], int(args[1]), int(args[2]), int(args[3]), int(args[4])))
    return ret

def save_state(file, pinned):
    with open(file, "w") as f:
        for app in pinned:
            args = str(app.path) + "," + str(app.x) + "," + str(app.y) + "," + str(app.w) + "," + str(app.h) +"\n"
            f.write(args)

# code modified from https://stackoverflow.com/questions/21070423/
def get_icon(PATH, size):
    norm_path = os.path.abspath(PATH)

    SHGFI_ICON = 0x000000100
    SHGFI_ICONLOCATION = 0x000001000
    if size == "small":
        SHIL_SIZE = 0x00001
    elif size == "large":
        SHIL_SIZE = 0x00002
    else:
        raise TypeError("Invalid argument for 'size'. Must be equal to 'small' or 'large'")

    ret, info = shell.SHGetFileInfo(norm_path, 0, SHGFI_ICONLOCATION | SHGFI_ICON | SHIL_SIZE)
    hIcon, iIcon, dwAttr, name, typeName = info
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), hIcon)
    win32gui.DestroyIcon(hIcon)

    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)

    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    img = Image.frombuffer(
        "RGBA",
        (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
        bmpstr, "raw", "BGRA", 0, 1
    )

    if size == "small":
        img = img.resize((16, 16), Image.ANTIALIAS)
    return img
