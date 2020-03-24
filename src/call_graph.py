#!/usr/bin/env python

#===--- CallGraph.py -----------------------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#
import Method
from clang.cindex import AccessSpecifier

class CallGraph:
    def __init__(self, class_name):
      self.__class_name = class_name
      self.__publics = 0
      self.__defined = 0
      self.__pure_virtuals = 0
      self.__nodes = []
      self.__adjacency_matrix = []
      self.__current_calling_num = -1
    
    @property
    def class_name(self):
	return self.__class_name
    
    @property
    def num_of_nodes(self):
	return len(self.__nodes)
  
    @property
    def num_of_public(self):
	return self.__publics
  
    @property
    def nodes(self):
	return self.__nodes
  
    @property
    def adjacency_matrix(self):
	return self.__adjacency_matrix
    
    #@property
    #def pure_virtuals_num(self):
	#return self.__pure_virtuals
    
    @property
    def is_fully_defined(self):
	return len(self.__nodes) == (self.__defined + self.__pure_virtuals)
  
    def define(self, node):
	self.__current_calling_num = self.check_node(node)
	curr_node = self.__nodes[self.__current_calling_num]
	if not curr_node.is_defined:
	    curr_node.define()
	    self.__defined += 1
      
  
    def check_node(self, node):
	for i in xrange(len(self.__nodes)):
	    if node == self.__nodes[i]:
		return i
	return -1
    
    def add_node(self, node, is_pure_virtual):
    #def add_node(self, node):
	node_num = self.check_node(node)
	if node_num == -1:
	    if is_pure_virtual:
		self.__pure_virtuals += 1
	    if node.access_spec == AccessSpecifier.PUBLIC:
		self.__publics += 1
		self.__start = len(self.__nodes)
	    self.__nodes.append(node)
	return node_num
  
    def gen_adjacency_matrix(self):
	self.__adjacency_matrix = [[0 for i in xrange(len(self.__nodes))] for i in xrange(len(self.__nodes))]
    
    def call_node(self, calling_node, called_node):
	if self.__current_calling_num != -1:
	    if calling_node != self.__nodes[self.__current_calling_num]:
		self.__current_calling_num = self.check_node(calling_node)
      
	if self.__current_calling_num == -1:
	    self.__current_calling_num = self.check_node(calling_node)
      
	called_num = self.check_node(called_node)
    
	if (self.__current_calling_num == -1) | (called_num == -1):
	    return
    
	if (len(self.__adjacency_matrix) == 0):
	    self.gen_adjacency_matrix()
	
	self.__adjacency_matrix[self.__current_calling_num][called_num] = 1
  	  
    def look_for_edges(self):
	self.no_entrances_num = len(self.__nodes)
	self.no_outs_num = len(self.__nodes)
	self.edges_num = 0
	for i in xrange(len(self.__nodes)):
	    entrance_fl = True
	    out_fl = True
	    for j in xrange(len(self.__nodes)):
		if self.__adjacency_matrix[i][j] == 1:
		    self.edges_num += 1
		    if entrance_fl:			
			self.no_entrances_num -= 1
			entrance_fl = False
		if self.__adjacency_matrix[j][i] == 1:		    
		    if out_fl:
			self.no_outs_num -= 1
			out_fl = False
	
    
    def dfs(self, v, comp, used, mode='sort'):
	used[v] = True
	if (mode == 'straight') | (mode == 'reverse'):
	    comp.append(v)
	for i in xrange(len(self.__nodes)):
	    a = v
	    b = i
	    if mode == 'reverse':
		a = i
		b = v
	    if (self.__adjacency_matrix[a][b] != 0) & (not used[i]):
		self.dfs(i, comp, used, mode);
	if mode == 'sort':
	    comp.append(v)
    
    def find_comps(self, lvl=1):
	used = [False for i in xrange(len(self.__nodes))]
	order = []
	comp = []
	comp_num = 0
	for i in xrange(len(self.__nodes)):
		if not used[i]:
		    self.dfs(i, order, used, 'sort');
	used = [False for i in xrange(len(self.__nodes))]
	for i in xrange(len(self.__nodes)):
		v = order[len(self.__nodes) - 1 - i]
		if not used[v]:
		    if lvl == 2:
			self.dfs(v, comp, used, 'reverse')
		    else:
			self.dfs(v, comp, used, 'straight')
		    comp_num += 1
		    comp = []
	return comp_num