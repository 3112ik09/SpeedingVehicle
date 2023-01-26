import torch
import cv2


def applyAlgo(v):
    model = torch.hub.load('ultralytics/yolov5', 'custom', 'yolov5m.pt')
    model.classes = [2, 3, 7]
    model.conf = 0.35
    cap = cv2.VideoCapture(v)

    while True:
        img = cap.read()[1]
        if img is None:
            break
        result = model(img)
        df = result.pandas().xyxy[0]
        for ind in df.index:
            x1, y1 = int(df['xmin'][ind]), int(df['ymin'][ind])
            x2, y2 = int(df['xmax'][ind]), int(df['ymax'][ind])
            label = df['name'][ind]
            label = df['name'][ind]
            conf = df['confidence'][ind]
            text = label + ' ' + str(conf.round(decimals=2))
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

            cv2.imshow('Video', img)
        if cv2.waitKey(33) == 27:
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    applyAlgo("cars1.mp4")
