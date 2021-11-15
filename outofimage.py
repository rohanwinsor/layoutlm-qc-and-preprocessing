import glob
import json
import cv2
datas = glob.glob("jsons/*.json")
for name in datas:
    data = json.load(open(name, 'r'))
    for key, value in data.items():
        key = key.split('.')[0] + ".jpeg"
        img = cv2.imread('images/' + key)
        img_height, img_width, _ = img.shape
        for v in value['regions']:
            if v.get('shape_attributes') and v.get('region_attributes'):
                if img_height <= v.get('shape_attributes').get('y') + v.get('shape_attributes').get('height'):
                    print("=="*60)
                    print("JSON Name         ::".upper(), name)
                    print("IMG Name          ::".upper(), key)
                    print("img_height        ::".upper(), img_height)
                    print("img_width         ::".upper(), img_width)
                    print("shape_attributes  ::".upper(), v.get('shape_attributes'))
                    print("region_attributes ::".upper(), v.get('region_attributes'))