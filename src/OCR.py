import ctypes
import os
import easyocr
import win32con
from MouseCapture import mouse_capture
from color_write import printRed

def capture_ocr(img_path = 'temp.png', lan_list = ['ch_sim','en']):
    #置顶并隐藏窗口
    ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), win32con.SW_HIDE)

    #进行截图
    mouse_capture(img_path)

    #弹出窗口，进行ocr
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), win32con.SW_SHOWNORMAL)
    reader = easyocr.Reader(lan_list)
    result = reader.readtext(img_path)

    #显示结果
    if len(result):
        res_str = "\n".join(i[1] for i in result)
    else:
        res_str = ''
        printRed('OCR识别失败！\n')

    #删除图片
    os.remove(img_path)
    return res_str