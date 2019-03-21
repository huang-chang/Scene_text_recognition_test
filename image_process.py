#-*- coding:utf-8 -*-
from __future__ import division
from __future__ import print_function
import ocr
import cv2
import time
import os
import numpy as np
from PIL import Image
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class ImageProcess:
    
    def run(self, img):
        string = 'a'
        result, image_framed, detect_time, detect_number, densenet_time, image_shape = ocr.model(img, adjust = True)
        for key in result:
            string = string+'**' +result[key][1]
            
        if len(string) > 1:
            return string[3:],image_framed,detect_time, detect_number, densenet_time, image_shape
        else:
            return None,image_framed,detect_time, detect_number, densenet_time, image_shape
            
if __name__ == '__main__':
    
    img_handle = ImageProcess()
    
    image_path = '/home/vcaadmin/Downloads/scene_text_recognition/scene_text_recogition/percific_new1/300_raw.jpg'
    image = cv2.imread(image_path)
    
    cap = cv2.VideoCapture('/home/vcaadmin/Downloads/scene_text_recognition/video/percific_new1.mp4')
    if cap.isOpened():
        ret, img = cap.read()
        frame_id = 0
        height, width, depth = img.shape
        sign = 0
        while ret:
#            if frame_id == 300:
#                sign = 1
#                sign_image = img.copy()
            if frame_id % 10 == 0:
            #if sign == 1:
                t0 = time.time()
                img_temp = img.copy()
                img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img_cut = img_rgb[int(5/6*height):height,0:width]              
                
                result, image_framed, detect_time, detect_number, densenet_time, image_shape = img_handle.run(img_cut) 
                #print(result)
                t1 = time.time()
                if result != None:
                    print(frame_id,'detect_time:{:.3f}'.format(detect_time), 'detect_number:{}'.format(detect_number), 'densenet item:{:.3f}'.format(densenet_time),'densenet image shape:{}'.format(image_shape))
            if frame_id == 400:
                break
            
            ret, img = cap.read()
            frame_id += 1
        cap.release()

