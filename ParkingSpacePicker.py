import pickle
import cv2

width, height = 107, 48 # width, height of the parking space rectangle in the image (in pixels)

try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []


def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)

    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)


def parkingspacepicker():
    while True:
        img = cv2.imread('carParkImg.png')
        for pos in posList:
            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2) # draw a rectangle around the parking space on the image with a thickness of 2 pixels (thickness = -1 means filled rectangle)

        # cv2.imshow("Image", img)
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        cv2.setMouseCallback("Image", mouseClick)
        # cv2.waitKey(1)

