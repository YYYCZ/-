import cv2
import win32gui, win32ui, win32con, win32api

def window_capture(filename):
    hwnd = 0  # 窗口的编号，0号表示当前活跃窗口
    # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    hwndDC = win32gui.GetWindowDC(hwnd)
    # 根据窗口的DC获取mfcDC
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # mfcDC创建可兼容的DC
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建bigmap准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    # 获取监控器信息
    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    # print w,h　　　#图片大小
    # 为bitmap开辟空间
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    # 高度saveDC，将截图保存到saveBitmap中
    saveDC.SelectObject(saveBitMap)
    # 截取从左上角（0，0）长宽为（w，h）的图片
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)

def mouse_capture(save_path = 'temp.png'):
    '进行鼠标截屏，成功返回截图保存至指定路径'

    #先获取全屏并保存
    window_capture(save_path)

    #令opencv读取图片，进行截取
    src_img = cv2.imread(save_path)

    #截取函数
    def mouse_event(event, x, y, flags, params):
        global pt1,pt2            
        if event == cv2.EVENT_LBUTTONDOWN:
            #鼠标左键按下
            pt1 = x,y
        elif event == cv2.EVENT_LBUTTONUP:
            #鼠标左键松开
            pt2 = x,y
            min_x = min(pt1[0],pt2[0])
            min_y = min(pt1[1],pt2[1])
            width = abs(pt1[0] - pt2[0])
            height = abs(pt1[1] -pt2[1])
            cut_img = src_img[min_y:min_y+height, min_x:min_x+width]
            cv2.imwrite(save_path,cut_img)
            cv2.destroyAllWindows()
        elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
            #鼠标移动
            pt2 = x,y
            show_img = src_img.copy()
            cv2.rectangle(show_img,pt1,pt2,(0,255,0),3,cv2.LINE_4)
            cv2.imshow('MOUSE_GRAB_WINDOW',show_img)

    #显示图片，准备截取
    cv2.namedWindow('MOUSE_GRAB_WINDOW',cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("MOUSE_GRAB_WINDOW", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('MOUSE_GRAB_WINDOW',mouse_event)
    cv2.imshow('MOUSE_GRAB_WINDOW',src_img)
    cv2.waitKey(0)

if __name__ == '__main__':
    mouse_capture()