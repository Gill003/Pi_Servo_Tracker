import cv2
from picamera2 import Picamera2
import numpy as np
import RPi.GPIO as GPIO
import time
from smbus import SMBus

# I2C setup
addr = 0x08
bus = SMBus(1)

# GPIO setup for servo
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo1 = GPIO.PWM(11, 50)  # pin 11 for servo1, 50Hz
servo1.start(0)
angle = 90

# DNN Configuration for Object Detection
def configDNN():
    classNames = []
    classFile = "/home/gill/Desktop/Object_Detection_Files/coco.names"
    with open(classFile, "rt") as f:
        classNames = f.read().rstrip("\n").split("\n")

    configPath = "/home/gill/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
    weightsPath = "/home/gill/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

    dnn = cv2.dnn_DetectionModel(weightsPath, configPath)
    dnn.setInputSize(320, 320)
    dnn.setInputScale(1.0 / 127.5)
    dnn.setInputMean((127.5, 127.5, 127.5))
    dnn.setInputSwapRB(True)
    
    return dnn, classNames

# Object Recognition function
def objectRecognition(dnn, classNames, image, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = dnn.detect(image, confThreshold=thres, nmsThreshold=nms)

    if not objects:
        objects = classNames
    
    recognisedObjects = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                recognisedObjects.append([box, className])
                if draw:
                    cv2.rectangle(image, box, color=(0, 0, 255), thickness=1)
                    cv2.putText(image, f"{classNames[classId-1]} ({round(confidence*100, 2)}%)", 
                                (box[0]-10, box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    return image, recognisedObjects

# Main loop
if __name__ == "__main__":
    dnn, classNames = configDNN()

    picam2 = Picamera2()
    config = picam2.create_preview_configuration({'format': 'RGB888'})
    picam2.configure(config)
    picam2.start()

    while True:
        pc2array = picam2.capture_array()
        pc2array = np.rot90(pc2array, 2).copy()  # Rotate image if needed

        # Perform object recognition
        result, objectInfo = objectRecognition(dnn, classNames, pc2array, 0.6, 0.6, objects=["teddy bear"])
        
        screen_center_x = pc2array.shape[1] / 2
        screen_center_y = pc2array.shape[0] / 2

        for box, className in objectInfo:
            sendval = 0
            tracked_object_center_x = box[0] + (box[2] / 2)
            tracked_object_center_y = box[1] + (box[3] / 2)

            distance_to_center_x = (screen_center_x - tracked_object_center_x) / 2
            distance_to_center_y = screen_center_y - tracked_object_center_y

            # X-axis control logic
            if 10 < distance_to_center_x <= 30:
                sendval = 5
            elif 30 < distance_to_center_x <= 60:
                sendval = 6
            elif 60 < distance_to_center_x <= 90:
                sendval = 7
            elif 90 < distance_to_center_x <= 110:
                sendval = 8
            elif distance_to_center_x > 110:
                sendval = 9
            elif -30 <= distance_to_center_x < -10:
                sendval = 0
            elif -60 <= distance_to_center_x < -30:
                sendval = 1
            elif -90 <= distance_to_center_x < -60:
                sendval = 2
            elif -110 <= distance_to_center_x < -90:
                sendval = 3
            elif distance_to_center_x < -110:
                sendval = 4

            # Y-axis control logic
            if 10 < distance_to_center_y <= 30:
                sendval += 50
            elif 30 < distance_to_center_y <= 60:
                sendval += 60
            elif 60 < distance_to_center_y <= 90:
                sendval += 70
            elif 90 < distance_to_center_y <= 110:
                sendval += 80
            elif distance_to_center_y > 110:
                sendval += 90
            elif -30 <= distance_to_center_y < -10:
                sendval += 0
            elif -60 <= distance_to_center_y < -30:
                sendval += 10
            elif -90 <= distance_to_center_y < -60:
                sendval += 20
            elif -110 <= distance_to_center_y < -90:
                sendval += 30
            elif distance_to_center_y < -110:
                sendval += 40
            
            bus.write_byte(addr, sendval)

        cv2.imshow("Output", pc2array)
        cv2.waitKey(50)
