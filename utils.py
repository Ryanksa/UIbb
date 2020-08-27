import pygame as pg
from PIL import Image
from win32com.shell import shell, shellcon
import win32api, win32con, win32ui, win32gui, os, math

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
    # convert from PIL to pygame image
    raw = img.tobytes("raw", "RGBA")
    icon = pg.image.frombuffer(raw, img.size, "RGBA")
    return icon

def _dist(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def pointOnLine(point, lineStart, lineEnd):
    d1 = _dist(lineStart, point) + _dist(point, lineEnd)
    d2 = _dist(lineStart, lineEnd)
    if d2 < 20:
        err = 0.3/d2
    else:
        err = 0.1/d2
    return math.isclose(d1, d2, rel_tol=err)
