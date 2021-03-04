import requests
import json
import os
from urllib.parse import urlparse
from detection import detect_faces
from utils import create_dirs

import unittest

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

                # Processing
                annotations = image_detections['annotation']
                total_faces += len(annotations)
                cv2_image, faces = detect_faces(path)
                detections += len(faces)

                print(f'Processing... {detections}/{total_faces}')


        self.assertEqual(total_faces, detections, msg=f'DETECTIONS/TOTAL = {detections}/{total_faces}')


if __name__ == '__main__':
    unittest.main()