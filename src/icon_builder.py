import cv2
import glob
import pandas as pd
import tkinter

name = ''
def _get_name():
    def EntryValue(event):
        global name
        name = EditBox.get()
        print(name)
        root.destroy()
    def deleteValue(event):
        img = cv2.imread(imgpath)
        root.destroy()
    root = tkinter.Tk()
    root.title(u"iconの名前を付けてください")
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


def main(indir=None, iconpath=None, excelpath=None):
    imgpaths = glob.glob(indir+'*.png')
    df = pd.ExcelFile(excelpath).parse('stage')
    for imgpath in imgpaths:
        img = cv2.imread(imgpath)
        for xy in zip(
            df["startx"], df["starty"], df["endx"], df["endy"]):
            img_save = img[xy[0]:xy[2], xy[1]:xy[3]]
            while(True):
                cv2.imshow('img',img_save)
                key = cv2.waitKey(20) & 0xFF
                if key == 0x1b or key == ord("q"):
                    break
                elif key == ord('y'):
                    _get_name()
                    if name[0] == 'c':
                        cv2.imwrite(iconpath+'charactor/'+name[1:]+'.png', img_save)
                    if name[0] == 's':
                        cv2.imwrite(iconpath+'stage/'+name[1:]+'.png', img_save)
                    if name[0] == 'v':
                        cv2.imwrite(iconpath+'ifvic/'+name[1:]+'.png', img_save)
                else:
                    pass

if __name__ == '__main__':
    indir = '../data/img/build/'
    iconpath = '../data/img/icons/'
    excelpath = '../data/excel/trim/trim_vec.xlsx'
    main(indir, iconpath, excelpath)
