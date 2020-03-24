
# coding: utf-8

# In[1]:

import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_predict
get_ipython().magic(u'matplotlib inline')
from sklearn import tree


# In[2]:

import ReadingFile
import PreprocessData

X, y = ReadingFile.read_csv('TRAIN_CORPUS.csv')
X


# In[3]:

decision_tree = tree.DecisionTreeClassifier()
decision_tree.fit(X, y)


# In[4]:

import pydotplus
from IPython.display import Image
from matplotlib.pyplot import savefig

feature_names = [ 'verb_in_name', 'template', 'is_inherited',
                  'constructors', 'total_methods', 'nonpublic_methods', 'static_methods', 'biggest_method_size',
                  'total_fields', 'nonpublic_fields', 'fields_class_refs', 'getters', 'setters',
                  'CG_edges', 'CG_no_entrance_vertexes', 'CG_no_out_vertexes',
                  'CG_comp_num', 'CG_strong_comp_num']
target_names = np.array(['regular', 'anti-pattern'])
dot_data = tree.export_graphviz(decision_tree, out_file=None, 
                                feature_names=feature_names, 
                                class_names=target_names, 
                                filled=True, rounded=True,  
                                special_characters=True)  
graph = pydotplus.graph_from_dot_data(dot_data)
pct = Image(graph.create_png())
pct


# In[9]:

from sklearn import metrics

# make predictions
expected = y
predicted = decision_tree.predict(X)
# summarize the fit of the model
print 'CLASSIFICATION REPORT:'
print(metrics.classification_report(expected, predicted))
print 'CONFUSION MATRIX:'
print(metrics.confusion_matrix(expected, predicted))

