import requests
import json
import os
from urllib.parse import urlparse
from detection import detect_faces
from utils import create_dirs
import  cv2

import unittest


MIN_FOUND_OVERLAP_AREA = 50
PREVIEW_MISSING_FACES = False


class Rect():
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def overlap_area(self, rect2):
        rect1 = self
        x_overlap = max(
            0,
            min(rect1.x2, rect2.x2) - max(rect1.x1, rect2.x1)
        )

        # print(f'x_overlap: {x_overlap}')

        y_overlap = max(
            0,
            min(rect1.y2, rect2.y2) - max(rect1.y1, rect2.y1)
        )

        # print(f'y_overlap: {y_overlap}')

        overlap_area = x_overlap * y_overlap
        print(f'overlap_area: {overlap_area}')

        # Get max overlap area
        max_overlap_area = min(self.area(), rect2.area())

        print(f'max_overlap_area: {max_overlap_area}')

        # Percentage
        return int(overlap_area / max_overlap_area * 100 )


    def area(self):
        l = (self.x2 - self.x1)
        w = (self.y2 - self.y1)

        # print(f'l:{l} w:{w}')

        return l * w

    def __str__(self):
        return f'x1:{self.x1} x2:{self.x2} y1:{self.y1} y2:{self.y2}'


def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

def imshow(cv2_image, faces, faces2 ):

    for face in faces:
        x1, x2, y1, y2 = face

        w = x2 - x1
        h = y2 - y1

        cv2.rectangle(
            cv2_image,
            (x1, y1),
            (x1 + w, y1 + h),
            (0, 255, 0),
            2
        )

    for face in faces2:
        x1, x2, y1, y2 = face

        w = x2 - x1
        h = y2 - y1

        cv2.rectangle(
            cv2_image,
            (x1, y1),
            (x1 + w, y1 + h),
            (235, 64, 52),
            2
        )

    resized = ResizeWithAspectRatio(cv2_image, width=1280)

    cv2.imshow('MissingFacePreview', resized)
    cv2.waitKey(0)


class TestDataset(unittest.TestCase):

    def test_all_faces_detected(self):
        test_images_cache = './test-dataset'

        total_faces = 0
        detections = 0

        create_dirs(test_images_cache)
        with open('face_detection_dataset.txt', 'r') as dataset_file:
            for line in dataset_file:
                image_detections = json.loads(line)
                url = image_detections['content']
                # print(url)
                url_parsed = urlparse(url)
                filename = os.path.basename(url_parsed.path)

                path = os.path.join(test_images_cache,filename)
                if not os.path.exists(path):
                    print(f'Downloading Image: {path}')
                    r = requests.get(url, stream=True)
                    if r.status_code == 200:
                        with open(path, 'wb') as f:
                            for chunk in r.iter_content(1024):
                                f.write(chunk)

                print(path)

                expected_face_rectangles = []

                # Processing
                annotations = image_detections['annotation']
                for annotation in annotations:

                    height = annotation['imageHeight']
                    width = annotation['imageWidth']
                    points = annotation['points']

                    if 'Face' in annotation['label']:
                        x1 = round(width * points[0]['x'])
                        y1 = round(height * points[0]['y'])
                        x2 = round(width * points[1]['x'])
                        y2 = round(height * points[1]['y'])
                        expected_face_rectangles.append(Rect(x1, x2, y1, y2))
                    else:
                        print('skip not a face')
                        break

                expected = []
                print(f'Expected {len(expected_face_rectangles)} Faces:')
                for efr in expected_face_rectangles:
                    expected.append([efr.x1,efr.x2,efr.y1,efr.y2])
                    print(f'[{efr.x1},{efr.x2},{efr.y1},{efr.y2}]')


                total_faces += len(annotations)
                cv2_image, faces = detect_faces(path)

                print(f'Detected {len(faces)} Faces:')

                for face in faces:
                    x,y,w,h = face
                    print(f'[{x},{x+w},{y},{y+h}]')


                for face in faces:
                    x,y,w,h = face
                    detected_face_rectangle = Rect(x, x + w, y, y + h)

                    face_found = False

                    for expected_face_rectangle in expected_face_rectangles:
                        overlap_area = expected_face_rectangle.overlap_area(detected_face_rectangle)
                        print(f'overlap_area: {overlap_area}')
                        if overlap_area > MIN_FOUND_OVERLAP_AREA:
                            face_found = True
                            break

                    if face_found:
                        detections += 1
                    else:
                        if PREVIEW_MISSING_FACES:
                            imshow(
                                cv2_image,
                                expected,
                                [[x, x + w, y, y + h]]
                            )

                print(f'Processing... {detections}/{total_faces}')
                # break

        self.assertEqual(total_faces, detections, msg=f'DETECTIONS/TOTAL = {detections}/{total_faces}')


if __name__ == '__main__':
    unittest.main()