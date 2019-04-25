import sys
import os
import glob
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.cm as cm

from mathutils import Math_utils
from icon_builder import set_icon
from get_senseki import Senseki

conf_path = './conf/path.conf'
for param in open(conf_path).readlines():
    name, value = param.strip('\n').split('=')
    if name == 'excel_path':
        excel_path = value
    elif name == 'trim_path':
        trim_excel_path = value
    elif name == 'img_path':
        img_path = value
    elif name == 'icon_path':
        icon_path = value

AVERAGE_CHASE_TIME = 0
AVERAGE_DECODING_PROGRESS = 1
EXTRA_DECODING_PROGRESS = 2
ITA_BREAKING = 3
TERROR_ATTACK = 4
NORMAL_ATTACK = 5
OSANPO_TIME = 6
ITA_ATTACKED = 7
HEAL = 8

PLOT = 100
BAR = 101

IFVIC = 201
STAGE = 202
HUNTER = 203


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        global excel_path, img_path

        #initialyze
        self.image = None

        super(MainWindow, self).__init__(parent)

        self.win_widget = Application()
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # add widget
        layout.addWidget(self.win_widget)

        self.setCentralWidget(widget)

        self.initUI()

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('【第五人格】-戦績管理ツール')
        self.show()

    def initUI(self):
        # set menu bar

        # set action

        # Exit
        exitAction = QtWidgets.QAction ('Exit', self)
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        # set excel dir
        excelDir = QtWidgets.QAction ('excel_path', self)
        excelDir.triggered.connect(self.exceldir)
        # set image file path
        imgPath = QtWidgets.QAction ('img_path', self)
        imgPath.triggered.connect(self.imgpath)
        # add stage
        addStage = QtWidgets.QAction ('add Stage', self)
        addStage.triggered.connect(self.addstage)
        # add charator
        addChara = QtWidgets.QAction ('add Charactor', self)
        addChara.triggered.connect(self.addchara)
        # add senseki
        addGame = QtWidgets.QAction ('add Game', self)
        addGame.triggered.connect(self.addgame)
        # show sub window
        subPlot = QtWidgets.QAction ('plot', self)
        subPlot.triggered.connect(self.sub_plot)
        # set defalt win_size
        setwin = QtWidgets.QAction ('set_win_size', self)
        setwin.triggered.connect(self.setwin)
        # set defalt gnum
        setgnum = QtWidgets.QAction ('set_table_num', self)
        setgnum.triggered.connect(self.setgnum)

        # set action into the file menu
        self.menubar = self.menuBar()
        # File
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(excelDir)
        fileMenu.addAction(imgPath)
        fileMenu.addAction(setwin)
        fileMenu.addAction(setgnum)
        fileMenu.addAction(exitAction)
        # Add
        addMenu = self.menubar.addMenu('&Add')
        addMenu.addAction(addStage)
        addMenu.addAction(addChara)
        addMenu.addAction(addGame)
        # Plot
        plotMenu = self.menubar.addMenu('&Plot')
        plotMenu.addAction(subPlot)

    # definition of the functions.
    def setParam(self, param, type=None):
        param_conf_path = './conf/param.conf'
        if type == 'excel':
            if not param[-1] == '\\':
                param = param + '\\'
            excel_path = param
        elif type == 'img_path':
            if not param[-1] == '\\':
                param = param + '\\'
            img_path = param
        elif type == 'set_win':
            data  = open(param_conf_path).readlines()
            ret = []
            for p in data:
                name, value = p.strip('\n').split('=')
                set = int(value)
                if name == 'window_size':
                    set = param
                ret.append((name, set))
            f = open(param_conf_path, "w")
            for s in ret:
                f.write('%s=%s\n' % (s[0], s[1]))
            f.close()
        elif type == 'set_gnum':
            data  = open(param_conf_path).readlines()
            ret = []
            for p in data:
                name, value = p.strip('\n').split('=')
                set = int(value)
                if name == 'gnum':
                    set = param
                ret.append((name, set))
            f = open(param_conf_path, "w")
            for s in ret:
                f.write('%s=%s\n' % (s[0], s[1]))
            f.close()
        elif type == 'stage':
            if self.image is not None:
                cv2.imwrite(
                    icon_path
                    + 'stage/'
                    + param
                    + '.png',
                    self.image
                )
            else:
                raise ValueError('image is None!')
        elif type == 'charactor':
            if self.image is not None:
                cv2.imwrite(
                    icon_path
                    + 'charactor/'
                    + param
                    + '.png',
                    self.image
                )
            else:
                raise ValueError('image is None!')
        else:
            pass

    def exceldir(self):
        subWindow = SubWindow(self, type='excel')
        subWindow.show()

    def imgpath(self):
        subWindow = SubWindow(self, type='img')
        subWindow.show()

    def addstage(self):
        """新しいステージの戦績画像を読み込ませるだけ"""
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open FIle',
            img_path,
            'Images (*.png *.jpg)'
        )
        img = cv2.imread(filename[0])
        if img is not None:
            y = len(img)
            x = len(img[0])
            excel = pd.ExcelFile(trim_excel_path+'trim_vec.xlsx').parse('stage')
            vec = (
                int(excel['sxr'] * y),
                int(excel['exr'] * y),
                int(excel['syr'] * x),
                int(excel['eyr'] * x)
            )
            self.image = img[vec[0]:vec[1], vec[2]:vec[3]]
            subWindow = SubWindow(self, type='stage')
            subWindow.show()

    def setwin(self):
        """新しいステージの戦績画像を読み込ませるだけ"""
        subWindow = SubWindow(self, type='set_win')
        subWindow.show()

    def setgnum(self):
        """新しいステージの戦績画像を読み込ませるだけ"""
        subWindow = SubWindow(self, type='set_gnum')
        subWindow.show()

    def addchara(self):
        """新しいキャラの戦績画像+選んでもらう"""
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open FIle',
            img_path,
            'Images (*.png *.jpg)'
        )
        try:
            img = cv2.imread(filename)
            y = len(img)
            x = len(img[0])
            excel = pd.ExcelFile(excel_path+'total.xlsx').parse('charactor')
            vec = (
                int(excel['sxr'] * x),
                int(excel['exr'] * x),
                int(excel['syr'] * y),
                int(excel['eyr'] * y)
            )
            for xy in zip(
                vec[0], vec[1], vec[2], vec[3]
                ):
                self.image = img[xy[0]:xy[1], xy[2]:xy[3]]
                subWindow = SubWindow(self, type='charactor')
                subWindow.show()
        except:
            pass

    def addgame(self):
        """戦績画像を追加してもらう"""
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open FIle',
            img_path,
            'Images (*.png *.jpg)'
        )
        try:
            s = Senseki(filename)
            s.save(excel_path)
        except:
            pass

    def sub_plot(self):
        """戦績画像を追加してもらう"""
        subWindow = SubPlot(self.win_widget)
        subWindow.show()

    def sub_plot_table(self):
        """戦績画像を追加してもらう"""
        subWindow = SubPlot_table(self.win_widget)
        subWindow.show()


class SubWindow(QtWidgets.QWidget):

    def __init__(self, parent=None, type=None):
        super().__init__()
        self.w = QtWidgets.QDialog(parent)
        self.parent = parent
        self.w.setWindowTitle('test')


        label = QtWidgets.QLabel()
        self.type = type
        if self.type == 'excel':
            label.setText('set directory of excel files.')
        else:
            pass

        self.edit = QtWidgets.QLineEdit()

        button = QtWidgets.QPushButton('set')
        button.clicked.connect(self.setParam)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.edit)
        layout.addWidget(button)

        self.w.setLayout(layout)

    def setParam(self):
        self.parent.setParam(self.edit.text(), self.type)
        self.w.close()

    def show(self):
        self.w.exec_()



class Application(QtWidgets.QWidget):

    def __init__(self):
        global excel_path
        super().__init__()

        ttl_path = excel_path + '/total.xlsx'
        htr_path = excel_path + '/hunter.xlsx'
        svr_path = excel_path + '/surviver.xlsx'
        param_conf_path = './conf/param.conf'

        # 数値を初期化
        self.m = Math_utils(ttl_path, htr_path, svr_path)

        for param in open(param_conf_path).readlines():
            print(param)
            name, value = param.strip('\n').split('=')
            if name == 'window_size':
                self.window_size = int(value)
            elif name == 'gnum':
                self.gnum = int(value)
        # UIの初期化
        self.initUI()

    # UIの初期化
    def initUI(self):
        self.tablayout = QtWidgets.QVBoxLayout(self)

        # タブの初期化
        self.initTab()

        self.setGeometry(0,0,800,600)

    def initTab(self):
        # tab作成
        self.tabs = QtWidgets.QTabWidget()

        # 各tabの生成
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()

        # tabの追加
        self.tabs.addTab(self.tab1,"データ")
        self.tabs.addTab(self.tab2,"グラフ")

        # tab1-内容の設定
        self.initFigure_1()
        self.tab1.layout = QtWidgets.QFormLayout(self)
        self.tab1.layout.addWidget(self.FigureCanvas_1)
        self.tab1.setLayout(self.tab1.layout)

        # tab2-内容の設定
        self.initFigure_2()
        self.tab2.layout = QtWidgets.QFormLayout(self)
        self.tab2.layout.addWidget(self.FigureCanvas_2)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.tablayout.addWidget(self.tabs)
        self.setLayout(self.tablayout)

    # Figureの初期化
    def initFigure_1(self):
        # FigureWidgetにLayoutを追加
        self.Figure_1 = plt.figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas_1 = FigureCanvas(self.Figure_1)
        # LayoutにFigureCanvasを追加

        self.init_Graph_1()

    def initFigure_2(self):
        # Figure用のWidget
        self.Figure_2= plt.figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas_2= FigureCanvas(self.Figure_2)

        self.ax1 = self.Figure_2.add_subplot(1,1,1)

        self.init_Graph_2()

    def init_Graph_1(self):
        plt.style.use('ggplot')
        plt.rcParams.update({'font.size':15})
        self.axis1 = self.Figure_1.add_subplot(2,2,1)
        win = self.m.get_win_rate()
        val_sorted = sorted(win.values(), reverse=True)
        win_sorted = []
        for v in val_sorted:
            for k in win.keys():
                if win[k] == v:
                    if not k in win_sorted:
                        win_sorted.append(k)
        if sum(val_sorted) < 1:
            win_sorted.append('others')
            val_sorted.append(1-sum(val_sorted))
        cmap = [plt.get_cmap("tab10")(i) for i in range(len(val_sorted))]
        plt.pie(
            val_sorted,
            labels=win_sorted,
            colors=cmap,
            counterclock=False,
            startangle=90
        )
        plt.title('win_rate')

        self.axis2 = self.Figure_1.add_subplot(2,2,2)
        hunter = self.m.get_hunter_rate()
        val_sorted = sorted(hunter.values(), reverse=True)
        hunter_sorted = []
        for v in val_sorted:
            for k in hunter.keys():
                if hunter[k] == v:
                    if not k in hunter_sorted:
                        hunter_sorted.append(k)
        if sum(val_sorted) < 1:
            hunter_sorted.append('others')
            val_sorted.append(1-sum(val_sorted))
        cmap = [plt.get_cmap("tab10")(i) for i in range(len(val_sorted))]
        plt.pie(
            val_sorted,
            labels=hunter_sorted,
            colors=cmap,
            counterclock=False,
            startangle=90
        )
        plt.title('hunters')

        self.axis3 = self.Figure_1.add_subplot(2,2,3)
        survs = self.m.get_survs_rate()
        val_sorted = sorted(survs.values(), reverse=True)
        survs_sorted = []
        for v in val_sorted:
            for k in survs.keys():
                if survs[k] == v:
                    if not k in survs_sorted:
                        survs_sorted.append(k)
        if sum(val_sorted) < 1:
            survs_sorted.append('others')
            val_sorted.append(1-sum(val_sorted))
        cmap = [plt.get_cmap("tab10")(i) for i in range(len(val_sorted))]
        plt.pie(
            val_sorted,
            labels=survs_sorted,
            colors=cmap,
            counterclock=False,
            startangle=90
        )
        plt.title('survivers')

        self.axis4 = self.Figure_1.add_subplot(2,2,4)
        maps = self.m.get_stage_rate()
        val_sorted = sorted(maps.values(), reverse=True)
        maps_sorted = []
        for v in val_sorted:
            for k in maps.keys():
                if maps[k] == v:
                    if not k in maps_sorted:
                        maps_sorted.append(k)
        if sum(val_sorted) < 1:
            maps_sorted.append('others')
            val_sorted.append(1-sum(val_sorted))
        cmap = [plt.get_cmap("tab10")(i) for i in range(len(val_sorted))]
        plt.pie(
            val_sorted,
            labels=maps_sorted,
            colors=cmap,
            counterclock=False,
            startangle=90
        )
        plt.title('maps')

        plt.axis('off')

    def init_Graph_2(self):
        """
        first plot is
        * average chase time
        * average osanpo time
        * average extra decoding
        を
        chasetime:折れ線
        osanpotime:hist
        extradecode:hist
        """

        # get values
        values = []
        ctime = self.m.get_ave_ctime(window_size=10)
        otime = self.m.get_osanpo_time(window_size=10)
        values = [(ctime, 'ctime'), (otime, 'otime')]

        # plot
        for value in values:
            self.ax1.plot(
                range(len(value[0])),
                value[0],
                label=value[1]
            )
        self.ax1.legend(loc='upper left')

    def update_Graph2(self, dic):
        """
        sub plot.
        1. get status from subPlot
        2. use plt to plot
        """
        color = ['r', 'b']
        width = 0.3

        # get values
        data_ax1 = (
            self._get_data_ax1([
                dic['radio1_1'][0],
                dic['radio2_1'][0]
            ]),
            [
                dic['GRadio1_1'],
                dic['GRadio2_1']
            ]
        )

        # plot
        self.ax1.clear()
        if (data_ax1[1][0] == BAR) and (data_ax1[1][1] == BAR):
            for i, data in enumerate(data_ax1[0]):
                self.ax1.bar(
                    np.array(range(len(data))) + i * width,
                    data,
                    label=dic['radio'+str(i+1)+'_1'][1],
                    color = color[i],
                    width=width,
                    align='center'
                )
        else:
            for i, data in enumerate(data_ax1[0]):
                if data_ax1[1][i] == PLOT:
                    self.ax1.plot(
                        data,
                        label=dic['radio'+str(i+1)+'_1'][1],
                        color = color[i]
                    )
                elif data_ax1[1][i] == BAR:
                    self.ax1.bar(
                        range(len(data)),
                        data,
                        label=dic['radio'+str(i+1)+'_1'][1],
                        color = color[i],
                        width=0.3,
                        align='center'
                    )

        self.ax1.legend(loc='upper left')

        self.FigureCanvas_2.draw()

    def update_table(self, dic):
        window = tablePlot(self)
        window.setdic(dic)
        window.show()
        # get values

        self.FigureCanvas_3.draw()

    def _get_data_ax1(self, list):
        ret = [None, None]

        if AVERAGE_CHASE_TIME in list:
            if list[0] == AVERAGE_CHASE_TIME:
                ret[0] = self.m.get_ave_ctime(window_size=10)
            else:
                ret[1] = self.m.get_ave_ctime(window_size=10)

        if AVERAGE_DECODING_PROGRESS in list:
            if list[0] == AVERAGE_DECODING_PROGRESS:
                ret[0] = self.m.get_ave_decode(window_size=10)
            else:
                ret[1] = self.m.get_ave_decode(window_size=10)

        if EXTRA_DECODING_PROGRESS in list:
            if list[0] == EXTRA_DECODING_PROGRESS:
                ret[0] = self.m.get_extra_decode(window_size=10)
            else:
                ret[1] = self.m.get_extra_decode(window_size=10)

        if ITA_BREAKING in list:
            if list[0] == ITA_BREAKING:
                ret[0] = self.m.get_ita_break(window_size=10)
            else:
                ret[1] = self.m.get_ita_break(window_size=10)

        if TERROR_ATTACK in list:
            if list[0] == TERROR_ATTACK:
                ret[0] = self.m.get_terror_attack(window_size=10)
            else:
                ret[1] = self.m.get_terror_attack(window_size=10)

        if NORMAL_ATTACK in list:
            if list[0] == NORMAL_ATTACK:
                ret[0] = self.m.get_usual_attack(window_size=10)
            else:
                ret[1] = self.m.get_usual_attack(window_size=10)

        if OSANPO_TIME in list:
            if list[0] == OSANPO_TIME:
                ret[0] = self.m.get_osanpo_time(window_size=10)
            else:
                ret[1] = self.m.get_osanpo_time(window_size=10)

        if ITA_ATTACKED in list:
            if list[0] == ITA_ATTACKED:
                ret[0] = self.m.get_ita_morau(window_size=10)
            else:
                ret[1] = self.m.get_ita_morau(window_size=10)

        return ret

    def _get_data_ax2(self, lst):
        if lst[1] == AVERAGE_CHASE_TIME:
            param = 'param5'
        elif lst[1] == AVERAGE_DECODING_PROGRESS:
            param = 'param1'
        elif lst[1] == HEAL:
            param = 'param4'
        elif lst[1] == ITA_ATTACKED:
            param = 'param4'

        dict = self.m.get_survs_with_param(param, lst[0])
        values = []
        for c in dict.values():
            value = []
            for i in c.values():
                if len(i[:self.window_size]) == 0:
                    cell = 0
                else:
                    cell = int(sum(i[:self.window_size]) / len(i[:self.window_size]))
                value.append(cell)
            values.append(value)
        columns = list(dict.keys())
        indices = list(dict[columns[0]].keys())
        return columns, indices, values


class tablePlot(QtWidgets.QWidget):

    def __init__(self, parent=None, dic=None):
        super().__init__()
        self.w = QtWidgets.QDialog(parent)
        self.w.setWindowTitle('sub_plot_window')
        self.w.setGeometry(500, 500, 600, 600)
        self.parent = parent
        self.window_size = self.parent.window_size
        self.gnum = self.parent.gnum
        self.m = self.parent.m
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        # self.fig = plt.figure()
        self.fig = plt.figure(figsize=(10,10),dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.move(0, 50)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored)
        self.update_table(dic)
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)
        self.widget.layout().addWidget(self.scroll)
        self.lay = QtWidgets.QVBoxLayout()
        self.lay.addWidget(self.widget)
        self.w.setLayout(self.lay)

    def update_table(self, dic):
        self.ax1 = self.fig.add_subplot(1,1,1)
        data_ax1 = (
            [
            dic['ver'][1],
            dic['nakami'][0]
            ]
        )
        index, columns, values = self._get_data_ax2(data_ax1)

        # set table
        self.ax1.clear()
        self.ax1.axis('off')
        index.insert(0, '')
        indices = index * math.ceil((len(columns) / self.gnum))
        c = []
        colors = []
        ind_col = ["w"]
        ind_col += ["#ff7f00" for i in range(len(index) - 1)]
        ind_col *= math.ceil((len(columns) / self.gnum))
        for i in range(math.ceil((len(columns) / self.gnum))):
            if columns[i * self.gnum : ( i + 1 ) * self.gnum] != []:
                add_col = columns[i * self.gnum : ( i + 1 ) * self.gnum]
                if len(add_col) != self.gnum:
                    add_col.extend(['' for _ in range(self.gnum-len(add_col))])
                c.append(add_col)
                add_c = [k[i * self.gnum : (i + 1) * self.gnum] for k in values]
                if len(add_c[0]) != self.gnum:
                    for h in range(len(add_c)):
                        add_c[h].extend([0 for _ in range(self.gnum-len(add_c[h]))])
                c.extend(add_c)
                colors.append(["#1ac3f5" for h in range(self.gnum)])
                colors.extend(
                    [["w" for i in range(self.gnum)] for k in range(len(index) - 1)]
                )

        # set table
        self.ax1.table(
            cellText=c,
            rowLabels=indices,
            rowColours=ind_col,
            cellColours=colors,
            loc='center'
        )
        plt.rcParams["font.size"] = 11.5
        self.ax1.set_title(dic['ver'][1] + '-' + dic['nakami'][1])
        self.canvas.draw()

    def _get_data_ax2(self, lst):
            if lst[1] == AVERAGE_CHASE_TIME:
                param = 'param5'
            elif lst[1] == AVERAGE_DECODING_PROGRESS:
                param = 'param1'
            elif lst[1] == HEAL:
                param = 'param4'
            elif lst[1] == ITA_ATTACKED:
                param = 'param4'

            dict = self.m.get_survs_with_param(param, lst[0])
            values = []
            for c in dict.values():
                value = []
                for i in c.values():
                    if len(i[:self.window_size]) == 0:
                        cell = 0
                    else:
                        cell = int(sum(i[:self.window_size]) / len(i[:self.window_size]))
                    value.append(cell)
                values.append(value)
            columns = list(dict.keys())
            indices = list(dict[columns[0]].keys())
            return columns, indices, values

    def show(self):
        self.w.exec_()

class SubPlot(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.w = QtWidgets.QDialog(parent)
        self.parent = parent
        self.w.setWindowTitle('sub_plot_window')

        self.tablayout = QtWidgets.QVBoxLayout(self)

        self.names = {
            'Average ctime':AVERAGE_CHASE_TIME,
            'ave dprogress':AVERAGE_DECODING_PROGRESS,
            'ex_decoding':EXTRA_DECODING_PROGRESS,
            'ita_breaking':ITA_BREAKING,
            'terror_attack':TERROR_ATTACK,
            'normal_attack':NORMAL_ATTACK,
            'osanpo time':OSANPO_TIME,
            'ita_attacked':ITA_ATTACKED
        }
        self.graph = {
            'plot':PLOT,
            'bar':BAR
        }
        self.vertical = {
            'ifvic':IFVIC,
            'stage':STAGE,
            'hunter':HUNTER
        }
        self.nakami = {
            'Average ctime':AVERAGE_CHASE_TIME,
            'ave dprogress':AVERAGE_DECODING_PROGRESS,
            'heal' : HEAL,
            'ita_attacked':ITA_ATTACKED
        }
        # タブの初期化
        self.initTab()

        self.w.setLayout(self.tablayout)

    def initTab(self):
        # tab作成
        self.tabs = QtWidgets.QTabWidget()

        # 各tabの生成
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()

        # tabの追加
        self.tabs.addTab(self.tab1,"graph")
        self.tabs.addTab(self.tab2,"table")

        # tab1-内容の設定
        self.tab1.layout = QtWidgets.QHBoxLayout(self)
        self.initTab1_UI()
        self.tab1.setLayout(self.tab1.layout)


        self.tab2.layout = QtWidgets.QHBoxLayout(self)
        self.initTab2_UI()
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.tablayout.addWidget(self.tabs)
        self.setLayout(self.tablayout)

    def initTab1_UI(self):
        radios = []
        self.group = QtWidgets.QButtonGroup()
        layout = QtWidgets.QVBoxLayout()
        for i, name in enumerate(self.names.keys()):
            radios.append(QtWidgets.QRadioButton(name))
            radios[i].setCheckable(True)
            radios[i].setFocusPolicy(QtCore.Qt.NoFocus)
            if i == 0:
                radios[i].setChecked(True)
            self.group.addButton(radios[i], i)
            layout.addWidget(radios[i])
        label = QtWidgets.QLabel('===============')
        layout.addWidget(label)
        GRadios = []
        self.ggroup1 = QtWidgets.QButtonGroup()
        for i, name in enumerate(self.graph.keys()):
            GRadios.append(QtWidgets.QRadioButton(name))
            GRadios[i].setCheckable(True)
            GRadios[i].setFocusPolicy(QtCore.Qt.NoFocus)
            if i == 0:
                GRadios[i].setChecked(True)
            self.ggroup1.addButton(GRadios[i], i)
            layout.addWidget(GRadios[i])

        radios2 = []
        self.group2 = QtWidgets.QButtonGroup()
        layout2 = QtWidgets.QVBoxLayout()
        for i, name in enumerate(self.names.keys()):
            radios2.append(QtWidgets.QRadioButton(name))
            radios2[i].setCheckable(True)
            radios2[i].setFocusPolicy(QtCore.Qt.NoFocus)
            if i == 1:
                radios2[i].setChecked(True)
            self.group2.addButton(radios2[i], i)
            layout2.addWidget(radios2[i])
        label2 = QtWidgets.QLabel('===============')
        layout2.addWidget(label2)
        GRadios2 = []
        self.ggroup2 = QtWidgets.QButtonGroup()
        for i, name in enumerate(self.graph.keys()):
            GRadios2.append(QtWidgets.QRadioButton(name))
            GRadios2[i].setCheckable(True)
            GRadios2[i].setFocusPolicy(QtCore.Qt.NoFocus)
            if i == 0:
                GRadios2[i].setChecked(True)
            self.ggroup2.addButton(GRadios2[i], i)
            layout2.addWidget(GRadios2[i])

        # draw button
        button = QtWidgets.QPushButton('Draw')
        button.clicked.connect(self.draw_button)

        self.tab1.layout.addLayout(layout)
        self.tab1.layout.addLayout(layout2)
        self.tab1.layout.addWidget(button)
        self.radios = radios
        self.GRadios = GRadios
        self.radios2 = radios2
        self.GRadios2 = GRadios2

    def initTab2_UI(self):
        radios = []
        self.group_2 = QtWidgets.QButtonGroup()
        layout = QtWidgets.QVBoxLayout()
        for i, name in enumerate(self.vertical.keys()):
            radios.append(QtWidgets.QRadioButton(name))
            radios[i].setCheckable(True)
            radios[i].setFocusPolicy(QtCore.Qt.NoFocus)
            if i == 0:
                radios[i].setChecked(True)
            self.group_2.addButton(radios[i], i)
            layout.addWidget(radios[i])
        label = QtWidgets.QLabel('===============')
        layout.addWidget(label)
        GRadios = []
        self.ggroup1_2 = QtWidgets.QButtonGroup()
        for i, name in enumerate(self.nakami.keys()):
            GRadios.append(QtWidgets.QRadioButton(name))
            GRadios[i].setCheckable(True)
            GRadios[i].setFocusPolicy(QtCore.Qt.NoFocus)
            if i == 0:
                GRadios[i].setChecked(True)
            self.ggroup1_2.addButton(GRadios[i], i)
            layout.addWidget(GRadios[i])

        # draw button
        button = QtWidgets.QPushButton('Draw')
        button.clicked.connect(self.draw_button2)

        self.tab2.layout.addLayout(layout)
        self.tab2.layout.addWidget(button)
        self.radios_2 = radios
        self.GRadios_2 = GRadios

    def draw_button(self):
        ret = {}
        for radio in self.radios:
            if radio.isChecked():
                ret['radio1_1'] = (
                    self.names[radio.text()],
                    radio.text()
                )
                break
        for GRadio in self.GRadios:
            if GRadio.isChecked():
                ret['GRadio1_1'] = (
                    self.graph[GRadio.text()]
                )
                break
        for radio in self.radios2:
            if radio.isChecked():
                ret['radio2_1'] = (
                    self.names[radio.text()],
                    radio.text()
                )
                break
        for GRadio in self.GRadios2:
            if GRadio.isChecked():
                ret['GRadio2_1'] = (
                    self.graph[GRadio.text()]
                )
                break

        self.update_Graph2(ret)

    def draw_button2(self):
        ret = {}
        for radio in self.radios_2:
            if radio.isChecked():
                ret['ver'] = (
                    self.vertical[radio.text()],
                    radio.text()
                )
                break
        for GRadio in self.GRadios_2:
            if GRadio.isChecked():
                ret['nakami'] = (
                    self.nakami[GRadio.text()],
                    GRadio.text()
                )
                break
        self.update_table(ret)

    def update_Graph2(self, dic):
        self.parent.update_Graph2(dic)

    def update_table(self, dic):
        window = tablePlot(self.parent, dic)
        window.show()

    def show(self):
        self.w.exec_()







if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
