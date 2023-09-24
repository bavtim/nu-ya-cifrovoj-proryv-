import gc
import uuid
import time
import cv2
import pandas as pd

from math import sqrt
from ultralytics import YOLO

class GetRecogniseFramesFromVideo:

    def __init__(self):
        
        self.model_detect = YOLO('models/model_detect.pt')
        self.model_segmentation = YOLO('models/model_segmentation.pt')      
            
    def recognize_video(self, video_name):
        
        vidcap = cv2.VideoCapture(video_name)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        
        list_frames = []
        count = 0
        list_trigger = [0]
        
        while(True):
            
            ret, frame = vidcap.read()
            
            if ret:
                y, x = frame.shape[:2]
                result_segmentation = self.model_segmentation(frame)
                result_detect = self.model_detect(frame)
                array_points_segmentation = result_segmentation[0].masks.segments[0]
                tensor_bb = result_detect[0].boxes.xyxy
                tensor_conf = result_detect[0].boxes.conf
                list_coords_rails = []
        
                for iterator_index in range(len(array_points_segmentation)):
                    x_coord_rails = int(x * array_points_segmentation[iterator_index][0])
                    y_coord_rails = int(y * array_points_segmentation[iterator_index][1])
                    list_coords_rails.append([x_coord_rails, y_coord_rails])
                    # Рисование кружочков - границ сегментации
                    # image = cv2.circle(frame, (x_coord_rails, y_coord_rails), radius=3, color=(255, 0, 0), thickness=-1)
        
                for iterator_index_bb in range(len(tensor_bb)):
                    if tensor_conf[iterator_index_bb] < 0.5:
                        continue
                    x_left_top_coord = int(tensor_bb[iterator_index_bb][0])
                    y_left_top_coord = int(tensor_bb[iterator_index_bb][1])
                    x_right_down_coord = int(tensor_bb[iterator_index_bb][2])
                    y_right_down_coord = int(tensor_bb[iterator_index_bb][3])
                    # Рисование прямоугольников - всех найденных объектов
                    # image = cv2.rectangle(image, (x_left_top_coord, y_left_top_coord), (x_right_down_coord, y_right_down_coord),(255,0,0), 3)
                    
                    if (x_left_top_coord + x_right_down_coord)/2 <= 960:
                        for iterator_y in list_coords_rails:
                            if iterator_y[1] < y_right_down_coord:
                                y_line = iterator_y[1]
                                x_line = iterator_y[0]
                            else:
                                break
                        dist = sqrt((abs(x_right_down_coord - x_line))**2 + (y_right_down_coord - y_line)**2)
                        danger_dist = 275 * (y_line/y)
                        if dist <= danger_dist: 
                            frame = cv2.rectangle(frame, (x_left_top_coord, y_left_top_coord), (x_right_down_coord, y_right_down_coord),(0, 255,0), 3)
                            if (count - 7 * fps) > list_trigger[-1]:
                                list_trigger.append(count)
        
                    elif (x_left_top_coord + x_right_down_coord)/2 > 960:
                        for iterator_y in reversed(list_coords_rails):
                            if iterator_y[1] < y_right_down_coord:
                                y_line = iterator_y[1]
                                x_line = iterator_y[0]
                            else:
                                break
                        dist = sqrt((abs(x_left_top_coord - x_line))**2 + (y_left_top_coord - y_line)**2)
                        danger_dist = 275 * (y_line/y)
                        if dist <= danger_dist: 
                            frame = cv2.rectangle(frame, (x_left_top_coord, y_left_top_coord), (x_right_down_coord, y_right_down_coord),(0, 255,0), 3)
                            if (count - 7 * fps) > list_trigger[-1]:
                                list_trigger.append(count)
        
                list_frames.append(frame)
                gc.collect()
                
            else:
                break
            
        self.create_csv(list_trigger, video_name, fps)
            
        name_video = self.create_video_from_frames(list_frames, fps, x, y)
        
        return name_video
        
        
    def create_video_from_frames(self, list_frames, fps, x, y):
        
        name_video = str(uuid.uuid4())
        
        out = cv2.VideoWriter(f'{name_video}.mp4', cv2.VideoWriter_fourcc(*'DIVX'), fps, (x, y))
        
        for iterator_cadr in list_frames:
            out.write(iterator_cadr)
            
        out.release()
        
        return name_video
    
    def create_csv(self, list_trigger, video_name, fps):
        
        list_trigger.remove(0)
        
        timestamps = []
        
        file_name = [video_name]
        
        cases_count = [len(list_trigger)]
        
        for iterator_count_frame in list_trigger:
            time_sec = iterator_count_frame//fps
            str_time = time.strftime('%M:%S', time.gmtime(time_sec))
            timestamps.append(str_time)
            
        timestamps = [timestamps]
        
        df = pd.DataFrame(list(zip(file_name, cases_count, timestamps)),
                  columns = ['filename', 'cases_count', "timestamps"])
        
        df.to_csv("submision.csv", index = False)