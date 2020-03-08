import cv2
import math

faceProto = "./data/opencv_face_detector.pbtxt"
faceModel = "./data/opencv_face_detector_uint8.pb"
genderProto = "./data/gender_deploy.prototxt"
genderModel = "./data/gender_net.caffemodel"

genderList = ["male", "female"]

faceNet = cv2.dnn.readNet(faceModel, faceProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

def highlight(net, frame, threshold = 0.7):
    frameOpencvDnn = frame.copy()
    height = frameOpencvDnn.shape[0]
    width = frameOpencvDnn.shape[1]

    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    faceboxes = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > threshold:
            x1 = int(detections[0, 0, i, 3] * width)
            y1 = int(detections[0, 0, i, 4] * height)
            x2 = int(detections[0, 0, i, 5] * width)
            y2 = int(detections[0, 0, i, 6] * height)
            faceboxes.append([x1, y1, x2, y2])

    return frameOpencvDnn, faceboxes

def resolve(image):
    video = cv2.VideoCapture(image if image else 0)
    padding = 20

    while cv2.waitKey(1) < 0:
        hasFrame, frame = video.read()

        if not hasFrame:
            cv2.waitKey()
            break

        resultImg, faceboxes = highlight(faceNet, frame)
        if not faceboxes:
            print("no face detected")

        genders = []
        for facebox in faceboxes:
            face = frame[
		max(0, facebox[1] - padding) : min(facebox[3] + padding, frame.shape[0] - 1),
                max(0, facebox[0] - padding) : min(facebox[2] + padding, frame.shape[1] - 1)
            ]

            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()

            gender = genderList[genderPreds[0].argmax()]
            genders.append(gender)
        return genders
