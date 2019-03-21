# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 16:35:03 2017

@author: huangchang
"""
from __future__ import print_function
from __future__ import division
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import argparse
import sys
import cv2
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import Qt
import image_process
import time
from PIL import Image
import numpy as np

class video_process():
    def __init__(self, args):
        
        #self.image_process = image_process.ImageProcess(args)
        self.image_process = image_process.ImageProcess()
    
    def multi_process(self,parent,video_path_list):
        for video_path in video_path_list:
            try:
                self.process(parent,video_path)
            except:
                continue
    
    def process(self,parent,video_path):
        cap = cv2.VideoCapture(video_path)
        video_result = []
        total_time = []
        if cap.isOpened():
            video_name = os.path.basename(video_path).split('.')[0]
            save_path = os.path.join(parent.result_path,video_name)
            save_label_path = os.path.join(save_path,'{}.txt'.format(video_name))
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            ret, img = cap.read()
            frame_id = 0
            height, width, depth = img.shape

            while ret and img is not None:
                if frame_id % 10 == 0:
                    
                    img_temp = img.copy()
                    img_rgb = cv2.cvtColor(img_temp, cv2.COLOR_BGR2RGB)
                    img_cut = img_rgb[int(5/6*height):height,0:width]
                    
                    t0 = time.time()
                    text_result, image_drawed, detect_time, detect_number, densenet_time, image_shape= self.image_process.run(img_cut)
                    t1 = time.time()
                    current_image_file = os.path.join(save_path,'{}.jpg'.format(frame_id))
                    video_result.append('{}卍{}卍{}'.format(frame_id,text_result,current_image_file))
                    if text_result != None:
                        #print(frame_id,t1-t0,text_result)
                        print('detect_time:{:.3f}'.format(detect_time), 'detect_number:{}'.format(detect_number), 'densenet item:{:.3f}'.format(densenet_time),'densenet image shape:{}'.format(image_shape))
                        total_time.append(float(t1-t0))
                    img_drawed_rgb = cv2.cvtColor(image_drawed, cv2.COLOR_RGB2BGR)
                    img[int(5/6*height):height,0:width] = cv2.resize(img_drawed_rgb, (width,height-int(5/6*height)),interpolation=cv2.INTER_LINEAR)
                    cv2.imwrite(current_image_file,img) 
                    if frame_id == 300:
                        current_image_file = os.path.join(save_path,'{}_raw.jpg'.format(frame_id))
                        cv2.imwrite(current_image_file,img_temp)
                    parent.update_label_image(img)
                    parent.line_text.setText('{}'.format(text_result))
                ret, img = cap.read()
                frame_id += 1  
#                if frame_id == 20000: 
#                    print(np.mean(total_time))
#                    break
            cap.release()
            
            with open(save_label_path,'w') as f:
                for item in video_result:
                    f.write('{}卍{}\n'.format(item,0))
        
class mainwindow(QMainWindow):
    def __init__(self,args):
        super(mainwindow,self).__init__()
        
        self.setWindowTitle('face demo')
        self.setGeometry(100,100,1000,800)
        
        self.create_layout()
        self.create_actions()
        self.create_menus()
        
        self.result_list = []
        self.processor = video_process(args)
        self.result_path = args.result_path
        self.index = 0
        self.right_number = []
        
        if not os.path.exists(args.result_path):
            os.makedirs(args.result_path)
        
        
    def create_actions(self):
        self.click_video = QAction('chose video',self, statusTip = 'open the video file', triggered = self.video_action)
        self.click_video_batch = QAction('chose batch video',self, statusTip = 'open the batch video file', triggered = self.batch_video_action)
        self.load_text = QAction('load text',self, statusTip = 'load the video result text',triggered = self.load)
        self.load_batch_text = QAction('load batch text',self,statusTip = 'load the batch video test result text',triggered = self.load_batch_text_file)
    def create_menus(self):
        self.video = self.menuBar().addMenu('video')
        self.video.addAction(self.click_video)
        self.video.addAction(self.click_video_batch)
        
        self.load = self.menuBar().addMenu('load')
        self.load.addAction(self.load_text)
        self.load.addAction(self.load_batch_text)
        
    def create_layout(self):
        self.layout1 = QHBoxLayout()
        self.image_label = QLabel()
        self.result_list_widget = QListWidget()
        
        self.layout1.addWidget(self.image_label)
        self.layout1.addWidget(self.result_list_widget)
        self.result_list_widget.setFixedWidth(250)
        self.result_list_widget.itemSelectionChanged.connect(self.show_select_image)
        
        self.layout2 = QHBoxLayout()
        self.line_text = QLineEdit()
        self.line_text.returnPressed.connect(self.record_class_number)
        self.layout2.addWidget(self.line_text)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.layout1)
        main_layout.addLayout(self.layout2)
        
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(main_layout)
        
    def video_action(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self, 'chosing the video', filter = '(*.mp4 *.avi *.flv *.m3u8 *.rmvb *.mkv *.ts)')
    
        video_handle = threading.Thread(target = self.processor.process, args = (self,self.video_path,))
        video_handle.setDaemon(True)
        video_handle.start()
        
    def batch_video_action(self):
        self.video_folders = QFileDialog.getExistingDirectory(self,'chose the batch video')
        video_path_list = []
        for video in os.listdir(self.video_folders):
            video_path = os.path.join(self.video_folders,video)
            video_path_list.append(video_path)
        batch_video_handle = threading.Thread(target = self.processor.multi_process,args = (self,video_path_list,))
        batch_video_handle.setDaemon(True)
        batch_video_handle.start()
        
    def load(self):
        self.text_path, _ = QFileDialog.getOpenFileName(self,'load the video result text',filter = '(*.txt)')
        self.result_list = []
        self.result_list_widget.clear()
        with open(self.text_path,'r') as f:
            for item in f.readlines():
                self.result_list.append(item.strip('\n').split('卍'))
        for index in range(len(self.result_list)):
            self.result_list[index][3] = index
               
        for item in self.result_list:
            #list_item = QListWidgetItem('{}:{}:{}'.format(item[1],item[2],item[8]))
            self.result_list_widget.addItem('{}卍{}'.format(item[0],item[3]))
    def load_batch_text_file(self):
        text_directory = QFileDialog.getExistingDirectory(self,'chose the batch test result text file')
        text_path = []
        for directory,folders,files in os.walk(text_directory):
            if len(files) != 0:
                for file in files:
                    if file.split('.')[-1] in ['txt','TXT']:
                        text_path.append(os.path.join(directory,file))
        result_list = []                
        for one_path in text_path:
            with open(one_path,'r') as f:
                for item in f.readlines():
                    result_list.append(item.strip('\n').split(':'))
        temp_class_set = set()
        for item in result_list:
            temp_class_set.add(item[1])
        temp_class = []
        temp_class.extend(temp_class_set)
        self.class_name = sorted(temp_class)
        result_sorted_list = []
        result_sub_sorted_list = []
        for index,item in enumerate(self.class_name):
            for one_item in result_list:
                if one_item[1] == item:
                    result_sub_sorted_list.append(one_item)
            result_sorted_list.append(result_sub_sorted_list)
            result_sub_sorted_list = []
            
        new_result = self.result_sorted(result_sorted_list)  
        self.result_list = []
        self.class_number = []
        for item in new_result:
            self.class_number.append(len(item))
            self.result_list.extend(item)
        for i in range(len(self.result_list)):
            self.result_list[i][8] = i
        self.result_list_widget.clear()
        for item in self.result_list:
            self.result_list_widget.addItem('{}:{}:{}'.format(item[1],item[2],item[8]))
        self.line_text.setText('{}:'.format(self.class_name[0]))
    def result_sorted(self,result):
        new_result = []
        temp = []
        for one_index,one_result in enumerate(result):
            if len(one_result) == 1:
                new_result.append(one_result)
            elif len(one_result) == 2:
                if float(one_result[0][2]) < float(one_result[1][2]):
                    temp.append(one_result[1])
                    temp.append(one_result[0])
                    new_result.append(temp)
                    temp = []
                else:
                    temp.append(one_result[0])
                    temp.append(one_result[1])
                    new_result.append(temp)
                    temp = []
            else:
                new_result.append(self.one_result_sorted(one_result))
            
        return new_result
    def one_result_sorted(self,result):
        temp = 0
        number = len(result) - 2
        new_result = []
        for i in range(number):
            for index,item in enumerate(result):
                if float(item[2]) > temp:
                    max_index = index
                    temp = float(item[2])
            new_result.append(result[max_index])
            del result[max_index]
            temp = 0
        if float(result[0][2]) < float(result[1][2]):
            new_result.append(result[1])
            new_result.append(result[0])
        else:
            new_result.append(result[0])
            new_result.append(result[1])
        
        return new_result
    def show_select_image(self):
        if not len(self.result_list):
            return
        item = self.result_list_widget.currentItem()
        index = item.text().split('卍')[1]
        current_image_path = self.result_list[int(index)][2]
        image = cv2.imread(current_image_path)
        #text = '{}:{}'.format(self.result_list[int(index)][1],self.result_list[int(index)][2])
        self.line_text.setText('{}'.format(self.result_list[int(index)][1]))
        self.update_label_image(image)
        
    def update_label_image(self,image):
        if image is not None and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, depth = image.shape
            qimage = QImage(image, w, h, QImage.Format_RGB888)
            pimage = QPixmap.fromImage(qimage)
            pimage2 = pimage.scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(pimage2)
    def record_class_number(self):
        self.index += 1
        if self.index < len(self.class_name):
            self.right_number.append(self.line_text.text().split(':')[-1])
            self.line_text.setText('{}:'.format(self.class_name[self.index]))
        else:
            self.right_number.append(self.line_text.text().split(':')[-1])
            self.line_text.setText('all ok ! stop now')
            self.index = 0
            with open('results.txt','w') as f:
                for i in range(len(self.class_name)):
                    f.write('{}\t{}\t{}\n'.format(self.class_name[i],self.class_number[i],self.right_number[i]))
def parse_arguments(argv):
    parse = argparse.ArgumentParser()
    parse.add_argument('--result_path', type = str, help = 'path for result of the video',default = 'scene_text_recogition')
    return parse.parse_args(argv)

def main(args):
    app = QApplication(sys.argv)
    example = mainwindow(args)
    example.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
