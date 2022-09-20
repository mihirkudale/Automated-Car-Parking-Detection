import os
import pickle
import cvzone
import numpy as np
import cv2
from twilio.rest import Client

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48
spaceCounter = 0


def checkParkingSpace(imgPro, img):
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2
    return spaceCounter


def send_massage_to_mobile(parking):
    # Auth token is automatically changed whenever i put all code on github
    # Twilio config
    twilio_account_sid = 'ACc173021189a3e333f1f766616ea8ed18' # Your Account SID from www.twilio.com/console
    twilio_auth_token = 'f12a57da86330a86c52fb7266e8db70d' # Your Auth Token from www.twilio.com/console
    twilio_phone_number = '+19895348077' # Your Twilio number
    destination_phone_number = '+919404612861'
    client = Client(twilio_account_sid, twilio_auth_token)

    sms_sent = False

    if parking > 0:
        if not sms_sent:
            print("SENDING SMS!!!") #
            message = client.messages.create(
                body=str(parking) + " Parking space available!!! You can Go",
                from_=twilio_phone_number,
                to=destination_phone_number
            )
            sms_sent = True
            print("Hope you got the message on your phone")


def send_message(display):
    path = os.path.join("output video", display)
    ca = cv2.VideoCapture(path)
    # print(frame)
    last_frame_num = ca.get(cv2.CAP_PROP_FRAME_COUNT) - 1 # get the last frame number of the video
    ca.set(1, last_frame_num)
    res, img = ca.read()

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1) # Blur the image to reduce noise and improve the edge detection results
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16) # Thresholding the image to get the parking space in white and the rest in black (inverted)
    imgMedian = cv2.medianBlur(imgThreshold, 5) # Median Blurring to remove the noise in the image and get a more smooth image
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
    # print("check parking space")

    parking = checkParkingSpace(imgDilate, img)
    print(parking)

    send_massage_to_mobile(parking)
