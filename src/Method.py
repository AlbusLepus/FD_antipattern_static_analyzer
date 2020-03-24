#!/usr/bin/env python
# -*- coding: utf-8 -*-

#===--- Method.py --------------------------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

import re
import string
from clang.cindex import AccessSpecifier

GETTER = 1
SETTER = 2
REGULAR = 0

class Method:
  def __init__(self, name, meth_type, access_spec):
    self.__name = name
    self.__type = meth_type
    self.__access_spec = access_spec
    self.__defined = False
    self.__check_purpose()
  
  @property
  def name(self):
    return self.__name
  @property
  def meth_type(self):
    return self.__type
  @property
  def access_spec(self):
    return self.__access_spec
  @property
  def is_defined(self):
    return self.__defined
  
  def __eq__(self, other):
    if (self.__name != other.name) | (self.__type != other.meth_type) | (self.__access_spec != other.access_spec):
      return False
    return True
    
  def __ne__(self, other):
    return not self.__eq__(other)
  
  def define(self):
    self.__defined = True
  
  def preprocess_name(self):
    first_word = self.__name
    name_text = re.sub('\d', r'', self.__name)
    name_text = re.sub('\W', r'', name_text)
    name_text = re.split('_', name_text)
    if type(name_text) is list:
      for word in name_text:
	if word != '':
	  first_word = word
	  break
    first_word = string.lower(re.search(r"[A-Z]?[a-z]*", first_word).group())
    return first_word
  
  def __check_purpose(self):
    first_name = self.preprocess_name()
    if (first_name == 'get') | (first_name == 'has') | (first_name == 'have') | (first_name == 'is') | (first_name == 'are'):
      self.__purpose = GETTER
      return
    if (first_name == 'set') | (first_name == 'add') | (first_name == 'append'):
      self.__purpose = SETTER
      return
    self.__purpose = REGULAR
  
  @property
  def get_purpose(self):
    return self.__purpose
  
  def get_info(self):
    return { 'name' : self.__name,
	     'type' : self.__type,
	     'access_spec' : self.__access_spec,
	     'purpose' : self.__purpose }