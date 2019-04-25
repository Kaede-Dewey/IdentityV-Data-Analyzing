import cv2
import glob
import pandas as pd
import tkinter

name = ''
def _get_name():
    def EntryValue(event):
        global name
        name = EditBox.get()
        root.destroy()
    def deleteValue(event):
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
    Button.pack()
    Button2.pack()
    root.mainloop()


def set_icon(img=None, iconpath=None):
    i = 0
    while(i < 1):
        cv2.imshow('img',img)
        key = cv2.waitKey(20) & 0xFF
        _get_name()
        cv2.imwrite(iconpath+name+'.png', img)
        i += 1
