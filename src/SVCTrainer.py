
# coding: utf-8

# In[1]:

import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import cross_val_predict
from sklearn.svm import SVC
get_ipython().magic(u'matplotlib inline')
import ReadingFile
import PreprocessData

def clear(key_params=[]):
    X, y = ReadingFile.read_csv('TRAIN_CORPUS.csv')
    X = PreprocessData.prepare_data(X, mode='save', key_features=key_params)
    return X, y

def check_score(X, y, clf, verbose=0):    
    predicted = cross_val_predict(clf, X, y, cv=10, verbose=verbose)
    return metrics.accuracy_score(y, predicted)


# In[2]:

X, y = clear()
svm_clf = SVC(kernel='linear')
svm_clf.fit(X, y)


# In[3]:

# test feature transformation

scores = []

X, y = ReadingFile.read_csv('TRAIN_CORPUS.csv')
scores.append(check_score(X, y, svm_clf))

X, y = ReadingFile.read_csv('TRAIN_CORPUS.csv')
scores.append(check_score(PreprocessData.prepare_features(X), y, svm_clf))

X, y = ReadingFile.read_csv('TRAIN_CORPUS.csv')
scores.append(check_score(PreprocessData.prepare_data(X, mode='save'), y, svm_clf))

scores


# In[6]:

# test feature importances

from sklearn.feature_selection import RFE
scores = []

for i in xrange(18):
    X, y = clear()
    estimator = SVC(kernel='linear')
    selector = RFE(estimator, i+1)
    selector = selector.fit(X, y)
    feature_nums = []
    for j in xrange(len(selector.ranking_)):
        if selector.ranking_[j] == 1:
            feature_nums.append(j)
    X1 = np.array([[X[g][j] for j in feature_nums] for g in xrange(len(X))])
    scores.append(check_score(X1, y, svm_clf))

max_num = 1
for i in xrange(len(scores)):
    print(i+1, scores[i])
    if scores[i] >= scores[max_num - 1]:
        max_num = i + 1


# In[7]:

# getting unimportant features

feature_names = [ 'verb_in_name', 'template', 'is_inherited','constructors', 'total_methods',
                  'nonpublic_methods', 'static_methods', 'biggest_method_size',
                  'total_fields', 'nonpublic_fields', 'fields_class_refs', 'getters', 'setters',
                  'CG_edges', 'CG_no_entrance_vertexes', 'CG_no_out_vertexes',
                  'CG_comp_num', 'CG_strong_comp_num']
X, y = clear()
estimator = SVC(kernel='linear')
selector = RFE(estimator, max_num)
selector = selector.fit(X, y)
feature_nums = []
for i in xrange(len(selector.ranking_)):
    if selector.ranking_[i] == 1:
        feature_nums.append(i)
    print(selector.ranking_[i], feature_names[i])
feature_nums


# In[ ]:

(1, 'constructors')
(1, 'total_methods')
(1, 'nonpublic_methods')
(1, 'static_methods')
(1, 'biggest_method_size')
(1, 'total_fields')
(1, 'getters')
(1, 'CG_edges')
(1, 'CG_no_out_vertexes')
(1, 'CG_comp_num')
(1, 'CG_strong_comp_num')


# In[8]:

# cutting out unimportant features

X, y = clear()
XX = np.array([[X[g][j] for j in feature_nums] for g in xrange(len(X))])
svm_clf = SVC(kernel='linear')
check_score(XX, y, svm_clf)


# In[9]:

# тест других параметров алгоритма обучения

X, y = clear(key_params=feature_nums)
clfs = []
clfs.append(SVC(kernel='linear'))
for clf in clfs:
    print check_score(X, y, clf)


# In[10]:

def learn_stat(X, y, C):
    
    clf = SVC(kernel='linear', C=C)
    score = check_score(X, y, clf)
    predicted = cross_val_predict(clf, X, y, cv=10)
    X_score = metrics.accuracy_score(y, predicted)
    return X_score


# In[11]:

def plot_stat(X, y, minC, maxC, steps, file_path):
    from matplotlib.pyplot import savefig
    opt_C = 0.001
    max_score = 0.0
    array = np.logspace(np.log10(minC), np.log10(maxC), steps)
    scores = np.zeros(len(array))
    vectors = np.zeros(len(array))
    for i in xrange(len(array)):
        scores[i] = learn_stat(X, y, array[i])
        if scores[i] > max_score:
            max_score = scores[i]
            opt_C = array[i]
            
    pl.title("SVC Score on C for linear")  
    pl.xscale('log')
    pl.xlabel('C-value (log-scale)')
    pl.plot(array, scores, label = 'X', color = 'r')
    
    pl.savefig(file_path)
    
    return opt_C, max_score


# In[12]:

X, y = clear(key_params=feature_nums)


# In[13]:

opt_C, max_score = plot_stat(X, y, 0.01, 100000, 100, 'SVC_C1.png')
print(opt_C, max_score)


# In[14]:

# Здесь смотрим на предыдущий график и уменьшаем интересующий нас диапазон параметра C
# в целях достижения большей точности

opt_C, max_score = plot_stat(X, y, 1, 10, 100, 'SVC_C2.png')
print(opt_C, max_score)


# In[16]:

X, y = clear(key_params=[])
opt_C_full, max_score_full = plot_stat(X, y, 1, 10, 100, 'SVC_C0_full.png')
print(opt_C_full, max_score_full)


# In[17]:

X, y = clear(key_params=feature_nums)
svm_clf = SVC(kernel='linear', C=opt_C)
svm_clf.fit(X, y)
coef = svm_clf.coef_
from sklearn.externals import joblib
joblib.dump(svm_clf, 'SVM_params.pkl') 


# In[18]:

X, y = clear(key_params=[])
svm_clf = SVC(kernel='linear', C=opt_C_full)
svm_clf.fit(X, y)
from sklearn.externals import joblib
joblib.dump(svm_clf, 'SVM_full_params.pkl') 


# In[21]:

print 'SVC с линейным ядром'
print 'Для полного набора признаков:'
print 'C =', opt_C_full
print 'Точность =', max_score_full


# In[22]:

print 'SVC с линейным ядром'
print 'Для оптимального набора признаков:'
print 'C = ', opt_C
print 'Точность = ', max_score

