
# coding: utf-8

import numpy as np
import csv

def read_csv(file_name):
    data = []
    labels = []
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            file_path = row['file_path']
            features = [float(row['verb_in_name']), float(row['template']), float(row['is_inherited']), float(row['constructors']), float(row['total_methods']), float(row['nonpublic_methods']), float(row['static_methods']), float(row['biggest_method_size']),  float(row['total_fields']), float(row['nonpublic_fields']), float(row['fields_class_refs']),  float(row['getters']), float(row['setters']), float(row['CG_edges']), float(row['CG_no_entrance_vertexes']), float(row['CG_no_out_vertexes']), float(row['CG_comp_num']), float(row['CG_strong_comp_num'])]
            label = float(row['label'])
            data.append(features)
            labels.append(label)
    data = np.array(data)
    labels = np.array(labels)
    return data, labels

