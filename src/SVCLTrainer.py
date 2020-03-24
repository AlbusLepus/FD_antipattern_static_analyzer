
# coding: utf-8

# In[1]:

import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import cross_val_predict
from sklearn.svm import LinearSVC
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
svm_clf = LinearSVC()
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


# In[4]:

# test feature importances

from sklearn.feature_selection import RFE
scores = []

for i in xrange(18):
    X, y = clear()
    estimator = LinearSVC()
    selector = RFE(estimator, i+1)
    selector = selector.fit(X, y)
    feature_nums = []
    for j in xrange(len(selector.ranking_)):
        if selector.ranking_[j] == 1:
            feature_nums.append(j)
    X1 = np.array([[X[g][j] for j in feature_nums] for g in xrange(len(X))])
    scores.append(check_score(X1, y, svm_clf))

for i in xrange(len(scores)):
    print(i+1, scores[i])


# In[5]:

# getting unimportant features

feature_names = [ 'verb_in_name', 'template', 'is_inherited','constructors', 'total_methods',
                  'nonpublic_methods', 'static_methods', 'biggest_method_size',
                  'total_fields', 'nonpublic_fields', 'fields_class_refs', 'getters', 'setters',
                  'CG_edges', 'CG_no_entrance_vertexes', 'CG_no_out_vertexes',
                  'CG_comp_num', 'CG_strong_comp_num']
X, y = clear()
estimator = LinearSVC()
selector = RFE(estimator, max_num)
selector = selector.fit(X, y)
feature_nums = []
for i in xrange(len(selector.ranking_)):
    if selector.ranking_[i] == 1:
        feature_nums.append(i)
    print(selector.ranking_[i], feature_names[i])
feature_nums


# In[6]:

# cutting out unimportant features

X, y = clear()
XX = np.array([[X[g][j] for j in feature_nums] for g in xrange(len(X))])
svm_clf = LinearSVC()
check_score(XX, y, svm_clf)


# In[7]:

# тест других параметров алгоритма обучения

X, y = clear(key_params=feature_nums)
clfs = []
clfs.append(LinearSVC())
clfs.append(LinearSVC(loss='hinge'))
clfs.append(LinearSVC(dual=False))
clfs.append(LinearSVC(fit_intercept=False))
for clf in clfs:
    print check_score(X, y, clf)


# In[8]:

def learn_stat(X, y, C):
    
    clf = LinearSVC(C=C)
    score = check_score(X, y, clf)
    predicted = cross_val_predict(clf, X, y, cv=10)
    X_score = metrics.accuracy_score(y, predicted)
    return X_score


# In[9]:

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
            
    pl.title("SVCL Score on C for linear")  
    pl.xscale('log')
    pl.xlabel('C-value (log-scale)')
    pl.plot(array, scores, label = 'X', color = 'r')
    
    pl.savefig(file_path)
    
    return opt_C, max_score


# In[10]:

X, y = clear(key_params=feature_nums)


# In[11]:

opt_C, max_score = plot_stat(X, y, 0.01, 10000, 100, 'SVCL_C1.png')
print(opt_C, max_score)


# In[12]:

# Здесь смотрим на предыдущий график и уменьшаем интересующий нас диапазон параметра C
# в целях достижения большей точности

opt_C, max_score = plot_stat(X, y, 0.1, 10, 100, 'SVCL_C2.png')
print(opt_C, max_score)


# In[13]:

X, y = clear(key_params=[])
opt_C_full, max_score_full = plot_stat(X, y, 0.1, 10, 100, 'SVCL_C0_full.png')
print(opt_C_full, max_score_full)


# In[14]:

X, y = clear(key_params=feature_nums)
svm_clf = LinearSVC(C=opt_C)
svm_clf.fit(X, y)
coef = svm_clf.coef_
from sklearn.externals import joblib
joblib.dump(svm_clf, 'SVML_params.pkl') 


# In[15]:

X, y = clear(key_params=[])
svm_clf = LinearSVC(C=opt_C_full)
svm_clf.fit(X, y)
coef_full = svm_clf.coef_
from sklearn.externals import joblib
joblib.dump(svm_clf, 'SVML_full_params.pkl') 


# In[18]:

print 'LinearSVC'
print 'Для полного набора признаков:'
print 'C =', opt_C_full
print 'Точность =', max_score_full
print 'Значимость признаков:'
print coef_full


# In[20]:

print 'LinearSVC'
print 'Для оптимального набора признаков:'
print 'C = ', opt_C
print 'Точность = ', max_score
print 'Значимость признаков:'
print coef

