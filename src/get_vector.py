import pandas as pd
import cv2
import numpy as np
import tkinter
import openpyxl

dic = {}
imgpath = '../data/img/build/img.png'
img = cv2.imread(imgpath)  # y座標, x座標, チャンネル
drawing = False
crd = []

def main():
    cv2.namedWindow('img', cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow('img', 100, 100)
    param = {'startx':100,'starty':200}
    cv2.setMouseCallback('img', onMouse, param)
    while(True):
        cv2.imshow('img',img)
        key = cv2.waitKey(20) & 0xFF
        if key == 0x1b or key == ord("q"):
            break
        else:
            pass
    cv2.destroyAllWindows()

def onMouse(event, x, y, flags, param):
    global drawing, crd, img, name, dic
    if event == cv2.EVENT_RBUTTONDOWN:
        drawing = True
        crd.extend([x, y])
        param['startx'] = x
        param['starty'] = y

    if event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = cv2.imread(imgpath)
            cv2.rectangle(
                img,
                (param['startx'], param['starty']),
                (x, y),
                (225, 225, 225),
                thickness=-1
                )

    if event == cv2.EVENT_RBUTTONUP:
        drawing = False
        img = cv2.imread(imgpath)
        cv2.rectangle(
            img,
            (param['startx'], param['starty']),
            (x, y),
            (0,255,0),
            -1)
        crd.extend([x, y])
        _get_name()

        crd = []


def _get_name():
    def EntryValue(event):
        name = EditBox.get()
        try:
            dic[name].extend(crd)
        except KeyError:
            dic[name] = crd
        root.destroy()
    def deleteValue(event):
        img = cv2.imread(imgpath)
        root.destroy()
    root = tkinter.Tk()
    root.title(u"タグの名前を付けてください")
    root.geometry("200x200")
    EditBox = tkinter.Entry()
    EditBox.insert(tkinter.END, '')
    EditBox.pack()
    Button = tkinter.Button(text=u'設定', width=50)
    Button.bind("<Button-1>",EntryValue)
    Button2 = tkinter.Button(text=u'取り消し', width=50)
    Button2.bind("<Button-1>",deleteValue)
    #左クリック（<Button-1>）されると，DeleteEntryValue関数を呼び出すようにバインド
    Button.pack()
    Button2.pack()
    root.mainloop()

if __name__ == '__main__':
    main()
    excelpath = '../data/excel/trim/trim_vec.xlsx'
    columns = ['starty', 'startx', 'endy', 'endx']
    with pd.ExcelWriter(excelpath) as writer:
        for key in dic.keys():
            mat = np.array(dic[key]).reshape((-1,4))
            df = pd.DataFrame(mat, columns=columns)
            df.to_excel(writer, sheet_name=key)
