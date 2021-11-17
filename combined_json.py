import numpy as np
import cv2
import os
import glob
import json
import random
from tqdm import tqdm
from transformers import BertTokenizer, RobertaTokenizer, DistilBertTokenizer
import re

def seg_file(file_path, tokenizer, max_len):
    subword_len_counter = 0
    output_path = file_path[:-4]
    with open(file_path, "r", encoding="utf8") as f_p, open(
        output_path, "w", encoding="utf8"
    ) as fw_p:
        for line in f_p:
            line = line.rstrip()

            if not line:
                fw_p.write(line + "\n")
                subword_len_counter = 0
                continue
            token = line.split("\t")[0]

            current_subwords_len = len(tokenizer.tokenize(token))

            # Token contains strange control characters like \x96 or \x95
            # Just filter out the complete line
            if current_subwords_len == 0:
                continue

            if (subword_len_counter + current_subwords_len) > max_len:
                fw_p.write("\n" + line + "\n")
                subword_len_counter = 0
                continue

            subword_len_counter += current_subwords_len

            fw_p.write(line + "\n")


def seg(model_path, train_file_path, box_file_path, img_file_path):
    tokenizer = BertTokenizer.from_pretrained(model_path, do_lower_case=True)
    seg_file(
        train_file_path,
        tokenizer,
        510,
    )
    seg_file(
        box_file_path,
        tokenizer,
        510,
    )
    seg_file(
        img_file_path,
        tokenizer,
        510,
    )


def bbox_string(box, width, height):
    assert 1 > (box[1] / height), "MAN SMTG WRG!!"
    assert 1 > (box[3] / height), "MAN SMTG WRG!!"
    return (
        str(int(1000 * (box[0] / width)))
        + " "
        + str(int(1000 * (box[1] / height)))
        + " "
        + str(int(1000 * (box[2] / width)))
        + " "
        + str(int(1000 * (box[3] / height)))
    )


if __name__ == "__main__":
    json_dir = "jsons/*.json"
    image_dir = "images"
    model_path = "/mnt/c/Users/rohan/Downloads/model"
    train_file_path = f"train.txt.tmp"
    box_file_path = f"train_box.txt.tmp"
    img_file_path = f"train_image.txt.tmp"

    all_annots = {}
    for json_file in glob.glob(json_dir):
        with open(json_file) as json_file_handle:
            json_data = json.load(json_file_handle)
            all_annots = {**all_annots, **json_data}
    # sample_n = 100
    # all_annots = dict(random.sample(all_annots.items(), sample_n))
    with open(train_file_path, "w") as train:
        with open(box_file_path, "w") as train_box:
            with open(img_file_path, "w") as train_img:
                for key, annot in tqdm(all_annots.items(), total=len(all_annots)):
                    file_name = key.split(".")[0] + ".jpeg"
                    if (
                        os.path.isfile(os.path.join(image_dir, file_name))
                        and "SoniaSuri[20_0]" not in file_name
                        and "PodishettiAnilkumar[13_0]" not in file_name
                    ):
                        img = cv2.imread(os.path.join(image_dir, file_name))
                        img_height, img_width, _ = img.shape
                        for i in annot["regions"]:
                            try:
                                if i.get("region_attributes").get("text"):
                                    text = i["region_attributes"]["text"]
                                    assert len(re.split("\s+", text)) == 1
                                    x1 = i["shape_attributes"]["x"]
                                    y1 = i["shape_attributes"]["y"]
                                    x2 = (
                                        i["shape_attributes"]["x"]
                                        + i["shape_attributes"]["width"]
                                    )
                                    y2 = (
                                        i["shape_attributes"]["y"]
                                        + i["shape_attributes"]["height"]
                                    )
                                    label = i["region_attributes"]["label"].strip()
                                    if label == "":
                                        label = "O"
                                    bbox_str = bbox_string(
                                        [x1, y1, x2, y2], img_width, img_height
                                    )
                                    train.write(f"{text}\t{label}\n")
                                    train_box.write(f"{text}\t{bbox_str}\n")
                                    train_img.write(f"{text}\t{bbox_str}\t{img_width} {img_height}\t{file_name}\n")
                            except Exception as e:
                                print("ERROR ::", e)
                                pass
                train.write("\n")
                train_box.write("\n")
                train_img.write("\n")
    seg(model_path, train_file_path, box_file_path, img_file_path)
