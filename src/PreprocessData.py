
# coding: utf-8

import numpy as np
#'verb_in_name', 'template', 'is_inherited', 'constructors', 'total_methods', 'nonpublic_methods'(ALREADY SCALED!),
#'static_methods', 'biggest_method_size', 'total_fields', 'nonpublic_fields'(ALREADY SCALED!), 'fields_class_refs',
#'getters', 'setters', 'CG_edges', 'CG_no_entrance_vertexes', 'CG_no_out_vertexes', 'CG_comp_num',
#'CG_strong_comp_num'

def cut_features(X, mode):
    if mode == '':
        return
    if mode == 'SVCL':
        key_features = [3, 4, 5, 6, 7, 8, 11, 12, 13, 15, 17] # got through tests on LinearSVC
    elif mode == 'SVC':
        key_features = [3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17] # got through tests on SVC
    XX = np.array([[X[i][j] for j in key_features] for i in xrange(len(X))])
    return XX

def cut_feat(X, key_features=[]):
    if len(key_features) == 0:
        return
    else:
        XX = np.array([[X[i][j] for j in key_features] for i in xrange(len(X))])
    return XX

def prepare_features(X):
    new_X = []
    for class_prec in X:
        class_prec[6] = class_prec[6] / class_prec[4] if class_prec[4] > 0 else 0 # static_methods
        class_prec[11] = class_prec[11] / class_prec[4] if class_prec[4] > 0 else 0 # getters
        class_prec[12] = class_prec[12] / class_prec[4] if class_prec[4] > 0 else 0 # setters
        class_prec[13] = class_prec[13] / class_prec[4] if class_prec[4] > 0 else 0 # CG_edges
        class_prec[14] = class_prec[14] / class_prec[4] if class_prec[4] > 0 else 0 # CG_no_entrance_vertexes
        class_prec[15] = class_prec[15] / class_prec[4] if class_prec[4] > 0 else 0 # CG_no_out_vertexes
        class_prec[16] = class_prec[16] / class_prec[4] if class_prec[4] > 0 else 0 # CG_comp_num
        class_prec[17] = class_prec[17] / class_prec[4] if class_prec[4] > 0 else 0 # CG_strong_comp_num
        class_prec[10] = class_prec[10] / class_prec[8] if class_prec[8] > 0 else 0 # fields_class_refs
        
        if class_prec[7] > 2000: # biggest_method_size
            class_prec[7] = 2000
        if class_prec[4] > 300: # total_methods
            class_prec[4] = 300
        if class_prec[8] > 100: # total_fields
            class_prec[8] = 100
            
        new_X.append(class_prec)
    return np.array(new_X)

def scale_data(X, mode):
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.externals import joblib
    
    if mode == 'save':
        scaler = MinMaxScaler().fit(X)
        joblib.dump(scaler, 'scaler_params.pkl')
    else:
        scaler = joblib.load('scaler_params.pkl')
    
    return scaler.transform(X)

def prepare_data(X, mode='read', key_features=[]):
    data = scale_data(prepare_features(X), mode)
    if len(key_features) != 0:
        data = cut_feat(data, key_features)
    return data

