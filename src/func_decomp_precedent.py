#!/usr/bin/env python
# -*- coding: utf-8 -*-

#===--- FuncDecompPrecedent.py -------------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

import re
import string
import call_graph
import Method
from clang.cindex import AccessSpecifier

class FuncDecompPrecedent:
    def __init__(self, name, file_name, template=False, label=-1):
	self.__name = name
	self.__file_name = file_name
	self.__constructors = 0
	self.__f2_total_methods = 0
	self.__f2_nonpublic_methods = 0
	self.__static_methods = 0
	self.__biggest_method_size = 0
	self.__f3_total_fields = 0
	self.__f3_nonpublic_fields = 0
	self.__fields_class_refs = 0
	self.__f3_getters = 0
	self.__f3_setters = 0
	self.__template = template
	self.__is_inherited = False
	self.__callgraph = call_graph.CallGraph(name)
	self.__label = label
	self.__check_f1()
      
    @property
    def are_methods_defined(self):
	return self.__callgraph.is_fully_defined
      
    @property
    def name(self):
	return self.__name
      
    @property
    def file_name(self):
	return self.__file_name
      
    @property
    def label(self):
	return self.__label
      
    @property
    def num_of_methods(self):
	return self.__callgraph
      
    def set_inherited(self):
	self.__is_inherited = True
      
    def set_biggest_method_size(self, size):
	if size > self.__biggest_method_size:
	    self.__biggest_method_size = size
      
    def preprocess_name(self):
	name_text = re.sub('\d', r'', self.__name)
	name_text = re.sub('\W', r'', name_text)
	name_text = re.split('_', name_text)
	words_list = []
	if type(name_text) is str:
	    name_text = list(name_text)
	for subtext in name_text:
	    while subtext != '':
		word = re.search(r"[A-Z]?[a-z]*", subtext).group()
		words_list.append(string.lower(word))
		subtext = re.sub(word, r'', subtext)
	return words_list
      
    def __check_f1(self):
	name_words = self.preprocess_name()
	rf = open('verbs.txt', 'r')
	verbs = set(rf.read().split('\n'))
	rf.close()
	verbs.discard('')
	for word in name_words:
	    if word in verbs:
		self.__f1_verb_in_name = True  # feature 1
		return
	self.__f1_verb_in_name = False  # feature 1
      
    def mark_class(self, label):
	if (label == 0) | (label == 1):
	    self.__label = label
      
    def __inc_public_methods__(self):
	self.__f2_total_methods += 1
    
    def __inc_nonpublic_methods__(self):
	self.__f2_nonpublic_methods += 1
	self.__f2_total_methods += 1
      
    def __inc_public_fields__(self):
	self.__f3_total_fields += 1
      
    def __inc_nonpublic_fields__(self):
	self.__f3_nonpublic_fields += 1
	self.__f3_total_fields += 1
      
    def define_method(self, method_node):
	method = Method.Method(method_node.spelling, method_node.type.spelling, method_node.access_specifier)
	self.__callgraph.define(method)
	
    def add_constructor(self):
	self.__constructors += 1
	
    def add_method(self, method_node, is_pure_virtual, is_static):
	method = Method.Method(method_node.spelling, method_node.type.spelling, method_node.access_specifier)
	self.__callgraph.add_node(method, is_pure_virtual)
	if is_static:
	    self.__static_methods += 1
	if method_node.access_specifier == AccessSpecifier.PUBLIC:
	    self.__inc_public_methods__()
	else:
	    self.__inc_nonpublic_methods__()
      
	if method.get_purpose == Method.GETTER:
	    self.__f3_getters += 1
	elif method.get_purpose == Method.SETTER:
	    self.__f3_setters += 1
  
    def add_field(self, field_node, is_class_ref):
	if is_class_ref == True:
	    self.__fields_class_refs += 1
	if field_node.access_specifier == AccessSpecifier.PUBLIC:
	    self.__inc_public_fields__()
	else:
	    self.__inc_nonpublic_fields__()
  
    def gen_callgraph(self):
	self.__callgraph.gen_adjacency_matrix()
    
    def add_call(self, calling_method_node, called_method_node):
	calling_method = Method.Method(calling_method_node.spelling, calling_method_node.type.spelling, calling_method_node.access_specifier)
	called_method = Method.Method(called_method_node.spelling, called_method_node.type.spelling, called_method_node.access_specifier)
	self.__callgraph.call_node(calling_method, called_method)
    
    def get_features(self):
	dict_f = self.get_export_info()
	features = [ dict_f['verb_in_name'], dict_f['template'], dict_f['is_inherited'], dict_f['constructors'], dict_f['total_methods'],
	     dict_f['nonpublic_methods'], dict_f['static_methods'], dict_f['biggest_method_size'], dict_f['total_fields'], dict_f['nonpublic_fields'],
	     dict_f['fields_class_refs'], dict_f['getters'], dict_f['setters'], dict_f['CG_edges'], dict_f['CG_no_entrance_vertexes'],
	     dict_f['CG_no_out_vertexes'], dict_f['CG_comp_num'], dict_f['CG_strong_comp_num'] ]
	
	return features
	
    def get_print_info(self):
	class_methods = [class_method.get_info()
			for class_method in self.__callgraph.nodes]
	self.__callgraph.look_for_edges()
	return { 'name' : self.__name,
		 'label' : self.__label,
		 'file_path' : self.__file_name,
		 'verb_in_name' :  self.__f1_verb_in_name,
		 'template' : self.__template,
		 'is_inherited' : self.__is_inherited,
		 'constructors' : self.__constructors,
		 'total_methods' : self.__f2_total_methods,
		 'nonpublic_methods' : self.__f2_nonpublic_methods,
		 'static_methods' : self.__static_methods,
		 'biggest_method_size' : self.__biggest_method_size,
		 'total_fields' : self.__f3_total_fields,
		 'nonpublic_fields' : self.__f3_nonpublic_fields,
		 'fields_class_refs' : self.__fields_class_refs,
		 'getters' : self.__f3_getters,
		 'setters' : self.__f3_setters,
		 'CG_edges' : self.__callgraph.edges_num,
		 'CG_no_entrance_vertexes' : self.__callgraph.no_entrances_num,
		 'CG_no_out_vertexes' : self.__callgraph.no_outs_num,
		 'CG_comp_num' : self.__callgraph.find_comps(),
		 'CG_strong_comp_num' : self.__callgraph.find_comps(lvl=2),
		 'z_class_methods' : class_methods }
		 #'z_matrix' : self.__callgraph.adjacency_matrix }
  
    def get_export_info(self):
	self.__callgraph.look_for_edges()
	return { 'name' : self.__name,
		 'file_path' : self.__file_name,
		 'verb_in_name' :  float(self.__f1_verb_in_name),
		 'template' : float(self.__template),
		 'is_inherited' : float(self.__is_inherited),
		 'constructors' : float(self.__constructors),
		 'total_methods' : float(self.__f2_total_methods),
		 'nonpublic_methods' : float(self.__f2_nonpublic_methods)/float(self.__f2_total_methods) if self.__f2_total_methods > 0 else 0.0,
		 'static_methods' : float(self.__static_methods),
		 'biggest_method_size' : float(self.__biggest_method_size),
		 'total_fields' : float(self.__f3_total_fields),
		 'nonpublic_fields' : float(self.__f3_nonpublic_fields)/float(self.__f3_total_fields) if self.__f3_total_fields > 0 else 0.0,
		 'fields_class_refs' : float(self.__fields_class_refs),
		 'getters' : float(self.__f3_getters),
		 'setters' : float(self.__f3_setters),
		 'CG_edges' : float(self.__callgraph.edges_num),
		 'CG_no_entrance_vertexes' : float(self.__callgraph.no_entrances_num),
		 'CG_no_out_vertexes' : float(self.__callgraph.no_outs_num),
		 'CG_comp_num' : float(self.__callgraph.find_comps()),
		 'CG_strong_comp_num' : float(self.__callgraph.find_comps(lvl=2)),
		 'label' : float(self.__label) }
  