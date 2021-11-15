import json
from collections import Counter
from labels import labels as LABELS

with open("complete_annotation.json", "r") as f:
    data = json.load(f)

label = []
all_labels = []
for key, value in data.items():
    for i in value["regions"]:
        try:
            if (
                i["region_attributes"].get("label")
                and i["region_attributes"]["label"].strip() != ""
            ):
                label.append(i["region_attributes"]["label"].strip())
        except Exception as e:
            exit()
    label_dict = Counter(label)
    try:
        for la in LABELS:
            assert label_dict[la] == label_dict[la.replace("B-", "E-")], la
    except:
        print("===" * 70)
        print("ERROR FILE NAME::", key, "\nLABELS DICT ::", label_dict)
        print("===" * 70)
    all_labels.extend(label)
    label = []
