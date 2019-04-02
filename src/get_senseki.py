import os
import sys
import glob
import random
import string

import cv2
from PIL import Image
import matplotlib.pyplot as plt
from pyocr import get_available_tools
import pyocr.builders
import numpy as np
import pandas as pd
import openpyxl

class Senseki(object):
    """
    Img class
    attribute:
        senseki(dict): stores values for the game.
            Keys: ifvic, stage, charactor-n
    """
    def __init__(self, image_path):
        self.senseki = {}

        # get image of the game
        self._get_image(image_path)
        game_id = self._gen_id(10)
        self.senseki['game_id'] = game_id

        # set csv paths
        self.trim_csv_data = '../data/excel/trim/trim_vec.xlsx'
        self.icon_path = '../data/img/icons/'

        # default charactor names. can be changed when a large update comes.
        charactors = [
            'ifvic',
            'charactor',
            'stage'
            ]
        numbers = [
            'time',
            'param1',
            'param2',
            'param3',
            'param4',
            'param5']

        # set charactor data and their values to the dictionary.0
        for charactor in charactors:

            # get icon to detect
            icon = self._get_icon(charactor=charactor)

            # detect charactor
            name = self._detect_icon_charactor(targets=icon, charactor=charactor)

            # set values on dictionary
            self.senseki[charactor] = name

        for number in numbers:

            # get icon
            icon = self._get_icon(charactor=number)

            # get value(scalar or list)
            value = self._get_value(icon)

            # set values on dictionary
            self.senseki[number] = value

    def _gen_id(self, n):
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)

    def _get_image(self, image_path):
        """
        get self.image to analyze
        return void
        set self.image
        """
        self.image = cv2.imread(image_path) # self.imageは戦績画面
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

    def _detect_icon_charactor(self, targets=None, charactor=None):
        """
        method to detect which charactor is in the given image.

        argument:
            img: image file opened with opencv.
            charactor: ifvic, stage, charactor
        return name: charactor name or ifvic or stage name. (string)
        """
        if charactor == 'ifvic':
            icon_paths = glob.glob(self.icon_path + 'ifvic/*.png')
        elif charactor == 'charactor':
            icon_paths = glob.glob(self.icon_path + 'charactor/*.png')
        elif charactor == 'stage':
            icon_paths = glob.glob(self.icon_path + 'stage/*.png')
        else:
            raise ValueError('charactor is not defined.')
        names = []
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        det = cv2.AKAZE_create()
        for _target in targets:
            if charactor == 'charactor':
                target = cv2.resize(_target, dsize=(150, 150))
            else:
                target = cv2.resize(_target, dsize=(250, 100))
            detector = {}

            t_kp, t_des = det.detectAndCompute(target, None)
            for compare in icon_paths:
                detector[self._get_distance(charactor, t_des, compare, bf, det)] \
                     = os.path.basename(compare).rstrip('.png')
            min_key = min(detector.keys())
            names.append(detector[min_key])
        return names

    def _get_distance(self, charactor, t_des, compare, bf, det):
        comp = cv2.imread(compare, cv2.IMREAD_GRAYSCALE)
        if charactor == 'charactor':
            comp = cv2.resize(comp, dsize=(150, 150))
        else:
            comp = cv2.resize(comp, dsize=(250, 100))
        c_kp, c_des = det.detectAndCompute(comp, None)
        match = bf.match(t_des, c_des)
        dist = [m.distance for m in match]
        return sum(dist) / len(dist)

    def _get_icon(self, charactor=None):
        """
        get icon image
        argument:
            charactor: charactor type
                ifvic, stage, charactor-n (0<= n <= 4)
        return img: icon image. (numpy array)
        """
        vecs = self._get_icon_vec(charactor=charactor)
        if charactor == 'charactor':
            imgs = [self.gray[vec[0]:vec[1], vec[2]:vec[3]]
                for vec in vecs]
        if charactor[:5] == 'param':
            imgs = []
            _imgs = [self.image[vec[0]:vec[1], vec[2]:vec[3]]
                for vec in vecs]
            for img in _imgs:
                # 画素の色を取得
                ltop = img[0][0]
                rbtm = img[-1][-1]
                min_col = np.array([
                    min(ltop[0], rbtm[0])-10,
                    min(ltop[1], rbtm[1])-10,
                    min(ltop[2], rbtm[2])-10
                    ])
                max_col = np.array([
                    max(ltop[0], rbtm[0])+10,
                    max(ltop[1], rbtm[1])+10,
                    max(ltop[2], rbtm[2])+10
                ])
                img_mask = cv2.inRange(img, min_col, max_col)
                result = cv2.bitwise_and(img, img, mask=img_mask)
                imgs.append(result)

        else:
            imgs = [self.image[vec[0]:vec[1], vec[2]:vec[3]]
                for vec in vecs]
        return imgs

    def _get_icon_vec(self, charactor=None):
        """
        get trimming vector from csv file.
        argument: ifvic, stage, charactor-n
        return: list of coordinations for trimming icon.
        """
        data = pd.ExcelFile(self.trim_csv_data).parse(charactor)
        return [
            [
            data['startx'][i], # starting x-coordinate
            data['endx'][i],# width
            data['starty'][i], # starting y-coordinate
            data['endy'][i] # height
            ]
            for i in range(len(data['startx']))
            ]

    def _get_value(self, images):
        # images is the list of images
        tool = get_available_tools()[0]
        ret = []
        builder = pyocr.builders.DigitBuilder(tesseract_layout=6)
        builder.tesseract_configs.append("digits")
        for img in images:
            ret.append(
                tool.image_to_string(
                    Image.fromarray(img),
                    lang='eng',
                    builder=builder
                )
            )
        return ret

    def save(self, outdir=None):
        """
        save excel files

        default outdir: $PROJ_DIR/data/excel/history/
        * total.xlsx: game_id, ifvic, hunter, surviver, custom
        * hunter.xlsx: game_id, hunter, params
        * surviver.xlsx:
            sheet_1: game_id, survivers
            sheet_2-sheet_6: param1-5
        """
        # search excel files
        excel_files = glob.glob(outdir+'*.xlsx')
        new = False
        if excel_files == []:
            # excel_fileを新規に作成するとき
            excel_files = [
                outdir + 'total.xlsx',
                outdir + 'hunter.xlsx',
                outdir + 'surviver.xlsx'
            ]
            new = True
            excel = None
        # save to excel files.
        for path in excel_files:
            if not new:
                excel = pd.ExcelFile(path)
            if os.path.basename(path) == 'total.xlsx':
                data = self._build_exceldata(excel, 'total.xlsx')[0]
                # data[0].values.reshape(-1, len(data[0]))
                with pd.ExcelWriter(path) as w:
                    data[0].to_excel(w, sheet_name = data[1], index=False)
            elif os.path.basename(path) == 'hunter.xlsx':
                data = self._build_exceldata(excel, 'hunter.xlsx')[0]
                with pd.ExcelWriter(path) as w:
                    data[0].to_excel(w, sheet_name = data[1], index=False)
            elif os.path.basename(path) == 'surviver.xlsx':
                datas = self._build_exceldata(excel, 'surviver.xlsx')
                with pd.ExcelWriter(path) as w:
                    for data in datas:
                        data[0].to_excel(w, sheet_name=data[1], index=False)

    def _build_exceldata(self, excel, file):
        ret = []
        if excel is not None:
            for e in excel.sheet_names:
                df = excel.parse(e)
                if e == 'total':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['ifvic'][0],
                            self.senseki['charactor'][0],
                            self.senseki['charactor'][1],
                            self.senseki['charactor'][2],
                            self.senseki['charactor'][3],
                            self.senseki['charactor'][4]
                        ],
                            index = [ 'game_id', 'ifvic', 'hunter',
                                        'surviver1', 'surviver2',
                                        'surviver3', 'surviver4']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['ifvic'][0],
                            self.senseki['charactor'][4],
                            self.senseki['charactor'][0],
                            self.senseki['charactor'][1],
                            self.senseki['charactor'][2],
                            self.senseki['charactor'][3]
                        ],
                            index = [ 'game_id', 'ifvic', 'hunter',
                                        'surviver1', 'surviver2',
                                        'surviver3', 'surviver4']
                        )

                elif e == 'hunter':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['charactor'][0],
                            self.senseki['param1'][0],
                            self.senseki['param2'][0],
                            self.senseki['param3'][0],
                            self.senseki['param4'][0],
                            self.senseki['param5'][0]
                        ],
                            index = [ 'game_id', 'hunter',
                                        'param1', 'param2', 'param3',
                                        'param4', 'param5']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['charactor'][4],
                            self.senseki['param1'][4],
                            self.senseki['param2'][4],
                            self.senseki['param3'][4],
                            self.senseki['param4'][4],
                            self.senseki['param5'][4]
                        ],
                            index = [ 'game_id', 'hunter',
                                        'param1', 'param2', 'param3',
                                        'param4', 'param5']
                        )
                elif e == 'surviver':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['charactor'][1],
                            self.senseki['charactor'][2],
                            self.senseki['charactor'][3],
                            self.senseki['charactor'][4]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['charactor'][0],
                            self.senseki['charactor'][1],
                            self.senseki['charactor'][2],
                            self.senseki['charactor'][3]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                elif e == 'param1':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param1'][1],
                            self.senseki['param1'][2],
                            self.senseki['param1'][3],
                            self.senseki['param1'][4]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param1'][0],
                            self.senseki['param1'][1],
                            self.senseki['param1'][2],
                            self.senseki['param1'][3]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                elif e == 'param2':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param2'][1],
                            self.senseki['param2'][2],
                            self.senseki['param2'][3],
                            self.senseki['param2'][4]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param2'][0],
                            self.senseki['param2'][1],
                            self.senseki['param2'][2],
                            self.senseki['param2'][3]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                elif e == 'param3':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param3'][1],
                            self.senseki['param3'][2],
                            self.senseki['param3'][3],
                            self.senseki['param3'][4]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param3'][0],
                            self.senseki['param3'][1],
                            self.senseki['param3'][2],
                            self.senseki['param3'][3]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                elif e == 'param4':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param4'][1],
                            self.senseki['param4'][2],
                            self.senseki['param4'][3],
                            self.senseki['param4'][4]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param4'][0],
                            self.senseki['param4'][1],
                            self.senseki['param4'][2],
                            self.senseki['param4'][3]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                elif e == 'param5':
                    if self.senseki['ifvic'][0] != 'sippai':
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param5'][1],
                            self.senseki['param5'][2],
                            self.senseki['param5'][3],
                            self.senseki['param5'][4]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                    else:
                        add_data = pd.Series(
                        [
                            self.senseki['game_id'],
                            self.senseki['param5'][0],
                            self.senseki['param5'][1],
                            self.senseki['param5'][2],
                            self.senseki['param5'][3]
                        ],
                            index = [ 'game_id', 'surviver1',
                                        'surviver2', 'surviver3',
                                        'surviver4']
                        )
                # add history data
                # add to return list
                ret.append([df.append(add_data, ignore_index=True), e])
        else:
            if file == 'total.xlsx':
                if self.senseki['ifvic'][0] != ['sippai']:
                    add_data = pd.DataFrame([
                    [
                        self.senseki['game_id'],
                        self.senseki['ifvic'][0],
                        self.senseki['charactor'][0],
                        self.senseki['charactor'][1],
                        self.senseki['charactor'][2],
                        self.senseki['charactor'][3],
                        self.senseki['charactor'][4]
                    ]],
                        columns = [ 'game_id', 'ifvic', 'hunter',
                                    'surviver1', 'surviver2',
                                    'surviver3', 'surviver4']
                    )
                else:
                    add_data = pd.DataFrame([
                    [
                        self.senseki['game_id'],
                        self.senseki['ifvic'][0],
                        self.senseki['charactor'][4],
                        self.senseki['charactor'][0],
                        self.senseki['charactor'][1],
                        self.senseki['charactor'][2],
                        self.senseki['charactor'][3]
                    ]],
                        columns = [ 'game_id', 'ifvic', 'hunter',
                                    'surviver1', 'surviver2',
                                    'surviver3', 'surviver4']
                    )
                ret.append([add_data, 'total'])
            elif file == 'hunter.xlsx':
                if self.senseki['ifvic'][0] != 'sippai':
                    add_data = pd.DataFrame([
                    [
                        self.senseki['game_id'],
                        self.senseki['charactor'][0],
                        self.senseki['param1'][0],
                        self.senseki['param2'][0],
                        self.senseki['param3'][0],
                        self.senseki['param4'][0],
                        self.senseki['param5'][0]
                    ]],
                        columns = [ 'game_id', 'hunter',
                                    'param1', 'param2', 'param3',
                                    'param4', 'param5']
                    )
                else:
                    add_data = pd.DataFrame([
                    [
                        self.senseki['game_id'],
                        self.senseki['charactor'][4],
                        self.senseki['param1'][4],
                        self.senseki['param2'][4],
                        self.senseki['param3'][4],
                        self.senseki['param4'][4],
                        self.senseki['param5'][4]
                    ]],
                        columns = [ 'game_id', 'hunter',
                                    'param1', 'param2', 'param3',
                                    'param4', 'param5']
                    )
                ret.append([add_data, 'hunter'])
            elif file == 'surviver.xlsx':
                sheet_names = [
                    'surviver',
                    'param1',
                    'param2',
                    'param3',
                    'param4',
                    'param5'
                ]
                for name in sheet_names:
                    if name == 'surviver':
                        if self.senseki['ifvic'][0] != 'sippai':
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['charactor'][1],
                                self.senseki['charactor'][2],
                                self.senseki['charactor'][3],
                                self.senseki['charactor'][4]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        else:
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['charactor'][0],
                                self.senseki['charactor'][1],
                                self.senseki['charactor'][2],
                                self.senseki['charactor'][3]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        ret.append([add_data, name])
                    elif name == 'param1':
                        if self.senseki['ifvic'][0] != 'sippai':
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param1'][1],
                                self.senseki['param1'][2],
                                self.senseki['param1'][3],
                                self.senseki['param1'][4]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        else:
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param1'][0],
                                self.senseki['param1'][1],
                                self.senseki['param1'][2],
                                self.senseki['param1'][3]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        ret.append([add_data, name])
                    elif name == 'param2':
                        if self.senseki['ifvic'][0] != 'sippai':
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param2'][1],
                                self.senseki['param2'][2],
                                self.senseki['param2'][3],
                                self.senseki['param2'][4]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        else:
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param2'][0],
                                self.senseki['param2'][1],
                                self.senseki['param2'][2],
                                self.senseki['param2'][3]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        ret.append([add_data, name])
                    elif name == 'param3':
                        if self.senseki['ifvic'][0] != 'sippai':
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param3'][1],
                                self.senseki['param3'][2],
                                self.senseki['param3'][3],
                                self.senseki['param3'][4]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        else:
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param3'][0],
                                self.senseki['param3'][1],
                                self.senseki['param3'][2],
                                self.senseki['param3'][3]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        ret.append([add_data, name])
                    elif name == 'param4':
                        if self.senseki['ifvic'][0] != 'sippai':
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param4'][1],
                                self.senseki['param4'][2],
                                self.senseki['param4'][3],
                                self.senseki['param4'][4]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        else:
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param4'][0],
                                self.senseki['param4'][1],
                                self.senseki['param4'][2],
                                self.senseki['param4'][3]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        ret.append([add_data, name])
                    elif name == 'param5':
                        if self.senseki['ifvic'][0] != 'sippai':
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param5'][1],
                                self.senseki['param5'][2],
                                self.senseki['param5'][3],
                                self.senseki['param5'][4]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        else:
                            add_data = pd.DataFrame([
                            [
                                self.senseki['game_id'],
                                self.senseki['param5'][0],
                                self.senseki['param5'][1],
                                self.senseki['param5'][2],
                                self.senseki['param5'][3]
                            ]],
                                columns = [ 'game_id', 'surviver1',
                                            'surviver2', 'surviver3',
                                            'surviver4']
                            )
                        ret.append([add_data, name])
        return ret

if __name__ == '__main__':
    img_dir = '../data/img/senseki/'
    outdir = '../data/excel/history/'
    for i, path in enumerate(glob.glob(img_dir + '*.png')):
        s = Senseki(path)
        s.save(outdir)
        print(i)
