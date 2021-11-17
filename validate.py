import json, re
from collections import Counter
from labels import labels as LABELS


def check_if_labels_are_present_but_no_text(file_name, regions):
    for region in regions:
        if region["region_attributes"].get("label"):
            assert region["region_attributes"].get("text") not in [
                "",
                None,
            ], f"{file_name} has no label for  region {region}"


def check_if_text_is_one_word(file_name, regions):
    for region in regions:
        if region["region_attributes"].get("text"):
            assert (
                len(re.split("\s+", region["region_attributes"]["text"].strip())) == 1
            ), f"{file_name} has more than one word for {region}"


def validate_if_opened_tags_are_closed(file_name, regions):
    labels = []
    for region in regions:
        if region["region_attributes"].get("label"):
            labels.append(region["region_attributes"]["label"].strip())
    for label in LABELS:
        assert labels.count("B-" + label.strip()) == labels.count(
            "E-" + label.strip()
        ), f"{file_name} has unclosed tags for {label}"
    return True

def check_if_bbox_overlaps(file_name, regions):
    for region in regions:
        for region_b in regions:
            if region != region_b:
                rectangle_a  = {"x1":region['shape_attributes']['x'], 
                "y1":region['shape_attributes']['y'], 
                "x2":region['shape_attributes']['x'] + region['shape_attributes']['width'], 
                "y2":region['shape_attributes']['y'] + region['shape_attributes']['height'], 
                }
                rectangle_b  = {"x1":region_b['shape_attributes']['x'], 
                "y1":region_b['shape_attributes']['y'], 
                "x2":region_b['shape_attributes']['x'] + region_b['shape_attributes']['width'], 
                "y2":region_b['shape_attributes']['y'] + region_b['shape_attributes']['height'], 
                }

                iou = get_iou(rectangle_a, rectangle_b)
                print(iou)
                if iou:
                    print(file_name)
                    print(region)
                    print(region_b)
                    exit()
def get_iou(bb1, bb2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bb1 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x, y) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    assert bb1['x1'] < bb1['x2']
    assert bb1['y1'] < bb1['y2']
    assert bb2['x1'] < bb2['x2']
    assert bb2['y1'] < bb2['y2']

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1['x1'], bb2['x1'])
    y_top = max(bb1['y1'], bb2['y1'])
    x_right = min(bb1['x2'], bb2['x2'])
    y_bottom = min(bb1['y2'], bb2['y2'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
    bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou

def check_if_any_unknown_label(file_name, regions):
    global LABELS
    new_labels = []
    for l in LABELS:
        for i in ["b-", "i-", "e-", "s-"]:
            new_labels.append(i + l.strip().lower())
    for region in regions:
        if region["region_attributes"].get("label") and region["region_attributes"].get("label").strip():
            assert (
                region["region_attributes"]["label"].strip().lower() in new_labels
            ), f"{file_name} has unknown label {region}, {new_labels}"

if __name__ == "__main__":
    # check_for_overlap()
    # exit()
    # PATH2JSON = "final_review/maheswari_set_data4/Set 4 mahe.json"
    PATH2JSON = "final_review/complete_annotation.json"
    with open(PATH2JSON, "r") as f:
        data = json.load(f)
    # for key, items in data.items():
    #     validate_if_opened_tags_are_closed(items['filename'], items['regions'])
    # print(f"validate_if_opened_tags_are_closed :: {True}")
    for key, items in data.items():
        check_if_bbox_overlaps(items['filename'], items['regions'])
    print(f"check_if_bbox_overlaps :: {True}")
