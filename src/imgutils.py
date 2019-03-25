import cv2
import os
from PIL import Image
import sys

import pyocr
import pyocr.builders
import numpy as np

class Img(object):
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
        
        # set csv paths
        self.trim_csv_data = './data/vecs/trimmings/trim_vec.csv'
        self.value_csv_data = './data/vecs/values/'
        
        # default charactor names. can be changed when a large update comes.
        charactors = [
            'ifvic',
            'stage',
            'charactor-0',
            'charactor-1',
            'charactor-2',
            'charactor-3',
            'charactor-4']
        
        # set charactor data and their values to the dictionary.0
        for charactor in charactors:
            # get icon to detect
            icon = self._get_icon(charactor=charactor)
            
            # detect charactor
            detected = self._detect_icon_charactor(img=icon, charactor=charactor)
            
            # get values for the charactor.
            numbers = self._get_numbers(self.image, charactor)
            
            # concatenate with charactor name
            detected.extend(numbers)
                
            # set values on dictionary
            self.senseki[charactor] = charactor_value
        
    def _get_image(self, image_path):
        """
        get self.image to analyze
        return void
        set self.image
        """
        self.image = cv2.imread(image_path) # self.imageは戦績画面
        
    def _detect_icon_charactor(self, img=None, charactor=None):
        """
        method to detect which charactor is in the given image.
        
        argument:
            img: image file transferred into NumPy array.
                you can transfer image file to NumPy array by reading
                the image with opencv with values.
            charactor: ifvic, stage, surviver, hunter
        warning:
            when you give charactor=='hunter', then you should give
            'hunter' icon, not surviver, or anything.
        return name: charactor name or ifvic or stage name. (string)
        """
        checking_datas = glob.glob('./data/icons/'+charactor[:9]+'/*.jpg')
        detector = []
        for path in checking_datas:
            checking_img = cv2.imread(path).values
            detector.append(sum(sum((checking_img - img) ** 2)))
        name = os.path.basename(
            checking_datas[np.argmin(detector)]).rstrip('.jpg')
        return [name]
        
    def _get_numbers(self, img, charactor):
        """
        method to get some values from the senseki image.
        
        arguments:
            img: senseki image. self.image
            charactor: ifvic, stage, charactor-n
        return:
            if charactor is ifvic or stage: return []
            if charactor is charactor-n: return[....]
        """
        if not (charactor[:9] == 'charactor'):
            # return [] if charactor is ifvic or stage.
            return []
            
        else:
            # preparation for ocr.
            tool = pyocr.get_available_tools()[0]
        
            # get number images for the charactor.
            charactor_number = charactor[10:]
            value_images = self._get_value_images(number=charactor_number)
            
            # initialize list
            numbers = []
            
            # get number for each images.
            for img in value_images:
                number = tool.image_to_string(
                    Image.fromarray(img),
                    lang="eng",
                    builder=pyocr.builders.TextBuilder(tesseract_layout=6)
                )
                
                # cleaning and save the result
                numbers.append(number.split('\n')[1])
            return numbers

    def _get_icon(self, charactor=None):
        """
        get icon image
        argument:
            charactor: charactor type
                ifvic, stage, charactor-n (0<= n <= 4)
        return img: icon image. (numpy array)
        """
        vec = self._get_icon_vec(charactor=charactor)
        img = self.img[vec[0]:vec[1], vec[2]:vec[3]]
        return img
        
    def _get_icon_vec(self, charactor=None):
        """
        get trimming vector from csv file.
        argument: ifvic, stage, charactor-n
        return: list of coordinations for trimming icon.
        """
        data = pandas.read_csv(self.trim_csv_data)
        return [
            data[charactor][0], # starting x-coordinate
            data[charactor][0] + data[charactor][1],# width
            data[charactor][2], # starting y-coordinate
            data[charactor][2] + data[charactor][3] # height
            ]
    
    def _get_value_images(self, number):
        """
        get trimming vector from csv file.
        argument: number(int)
            charactor number. 0~4
        return: list of images
        """
        vecs =  self._get_value_vec(number=number)
        img = []
        for vec in vecs
            img.append(self.img[vec[0]:vec[1], vec[2]:vec[3]])
        return img
    
    def _get_value_vec(self, number):
        data = pandas.read_csv(
            self.value_csv_data + \
            'charactor-' + \
            str(number) + \
            '.csv').values.tolist()
        ret = []
        for vec in data:
            ret.append(
            vec[0], # starting x-coordinate
            vec[0] + vec[1],# width
            vec[2], # starting y-coordinate
            vec[2] + vec[3] # height
            )
        return ret
                
        