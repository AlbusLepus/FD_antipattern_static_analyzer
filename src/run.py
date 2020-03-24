#!/usr/bin/env python

#===- cindex-dump.py - cindex/Python Source Dump -------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

import func_decomp_precedent

def visit_cxxmethod_children(node, method_node, class_precedent, checked_exprs, method_size):
    from clang.cindex import CursorKind
    
    if (method_size > 0):
	method_size += 1
    elif (node.kind == CursorKind.COMPOUND_STMT):
	method_size += 1
	
    if node.kind == CursorKind.CALL_EXPR:
	called_method_node = node.referenced
	if called_method_node is not None:
	  if called_method_node.semantic_parent.spelling == class_precedent.name:
	    if called_method_node not in checked_exprs:
	      class_precedent.add_call(method_node, called_method_node)
	      checked_exprs.append(called_method_node)
	      
    for child in node.get_children():
	method_size = visit_cxxmethod_children(child, method_node, class_precedent, checked_exprs, method_size)
    return method_size

def visit_cxxmethod(class_precedent, methods_definitions_list):
    for method_def in methods_definitions_list:
	if method_def.semantic_parent.spelling != class_precedent.name:
	    continue
	checked_exprs = []
	class_precedent.define_method(method_def)
	method_size = 0
	for child in method_def.get_children():
	    method_size = visit_cxxmethod_children(child, method_def, class_precedent, checked_exprs, method_size)
	class_precedent.set_biggest_method_size(method_size)

def visit_class_children(node, precedent, methods_definitions_list, depth):
    from clang.cindex import CursorKind, TypeKind
    
    if (node.kind == CursorKind.CLASS_DECL) | (node.kind == CursorKind.STRUCT_DECL) | (node.kind == CursorKind.CLASS_TEMPLATE):
	return
    if (node.kind == CursorKind.CXX_BASE_SPECIFIER) & (depth == 0):
	precedent.set_inherited()
	return
    if (node.kind == CursorKind.CONSTRUCTOR) & (depth == 0):
	precedent.add_constructor()
	return
    if node.kind == CursorKind.DESTRUCTOR:
	return
    if node.kind == CursorKind.FIELD_DECL:
	class_ref = False
	for child in node.get_children():
	    if child.type.kind == TypeKind.RECORD:
		class_ref = True
		break
	precedent.add_field(node, is_class_ref=class_ref)
	return
      
    if (node.kind == CursorKind.CXX_METHOD) | (node.kind == CursorKind.FUNCTION_TEMPLATE):
	precedent.add_method(node, node.is_pure_virtual_method(), node.is_static_method())
	if node.get_definition() is not None:
	    methods_definitions_list.append(node.get_definition())
	return
    
    for child in node.get_children():
	visit_class_children(child, precedent, methods_definitions_list, depth+1)

def get_features(class_node, template=False):
    precedent = func_decomp_precedent.FuncDecompPrecedent(class_node.spelling, class_node.location.file.name)
    methods_definitions_list = []
    for child in class_node.get_children():
	visit_class_children(child, precedent, methods_definitions_list, depth=0)
    
    precedent.gen_callgraph()
    
    visit_cxxmethod(precedent, methods_definitions_list)
    from pprint import pprint
    pprint(('class', precedent.name, precedent.file_name))
    #pprint(('method_definitions', [method_def.spelling for method_def in methods_definitions_list]))
    
    return precedent

def visit_classdecl(node, classes, handled_classes, not_defined_classes, classes_defined_in_file):
    from clang.cindex import CursorKind
    import string
    
    if node.kind == CursorKind.STRUCT_DECL:
	return
    if node.kind == CursorKind.ENUM_DECL:
	return
    if node.kind == CursorKind.FUNCTION_DECL:
	return
    if (node.kind == CursorKind.CLASS_DECL) | (node.kind == CursorKind.CLASS_TEMPLATE):
        if not node.is_definition():
	    node = node.get_definition()
	    if node is None:
		return
        #if node.location.file.name[:28] != '/home/peterterry/LLVM_Clang/':
	if node.location.file.name[:13] == '/usr/lib/gcc/':
	    return
        class_path = string.join([node.location.file.name, node.spelling], ':')
	if (classes.get(class_path) is None) & (class_path not in handled_classes):
	    if node.kind == CursorKind.CLASS_TEMPLATE:
		class_node = get_features(node, template=True)
	    else:
		class_node = get_features(node)
	    classes[class_path] = class_node
	    if class_node.are_methods_defined:
		classes_defined_in_file.add(class_path)
	    else:
		not_defined_classes.add(class_path)
	return
    
    if (node.kind == CursorKind.CXX_METHOD) | (node.kind == CursorKind.FUNCTION_TEMPLATE):
	parent_class = node.semantic_parent
	if parent_class is None:
	    return
	if (parent_class.kind == CursorKind.CLASS_DECL) | (parent_class.kind == CursorKind.CLASS_TEMPLATE):
	    class_path = string.join([parent_class.location.file.name, parent_class.spelling], ':')
	    if class_path in not_defined_classes:
		classes_defined_in_file.add(class_path)
		visit_cxxmethod(classes[class_path], [node])
    
    for child in node.get_children():
	visit_classdecl(child, classes, handled_classes, not_defined_classes, classes_defined_in_file)

def export_precedent(class_prec, writer):
    from pprint import pprint
    import csv
    pprint(('...saving in file...'))
    writer.writerow(class_prec.get_export_info())

def classify(class_prec, clf):
    import PreprocessData
    return clf.predict(PreprocessData.prepare_data([class_prec.get_features()]))[0]

def main():
    from clang.cindex import Index, CompilationDatabase, CompilationDatabaseError, Cursor
    from pprint import pprint
    from optparse import OptionParser
    import re

    parser = OptionParser("usage: %prog [options] {filename} [clang-args*]")
    parser.add_option("", "--anti-pattern", dest="aPat",
                      help="Check if classes in file are FD anti-pattern",
                      action="store_true", default=False)
    parser.add_option("", "--compile-commands", dest="cComs",
                      help="Source file is compile_commands.json (full path) of the project to parse",
                      action="store_true", default=False)
    parser.add_option("", "--file-list", dest="fList",
                      help="Source file is .txt file with the sources of the files to parse",
                      action="store_true", default=False)
    
    parser.disable_interspersed_args()
    (opts, args) = parser.parse_args()
    if len(args) == 0:
        parser.error('invalid number arguments')
    input_file = args[0]
    input_args = args[1:]
    files_list = []
    if (opts.aPat):
	#from sklearn.svm import SVC, LinearSVC
	from sklearn.externals import joblib
	clf = joblib.load('classifier_params.pkl')
    if (opts.cComs):
	if input_file[len(input_file)-21:] != 'compile_commands.json':
	    pprint(('Invalid file: ' + input_file + '. Should be compile_commands.json'))
	    return
	ind = -1;
	for i in xrange(len(input_file)):
	    if input_file[i]== '/':
		ind = i
      
	path_dir = input_file[:ind+1]
	# Step 1: load the compilation database
	compdb = CompilationDatabase.fromDirectory(path_dir)
	# Step 2: query compilation flags
	try:
	    commands = compdb.getAllCompileCommands()
	    for command in commands:
		comp_args = list(command.arguments)
		source_file = comp_args[len(comp_args)-1]
		if source_file[len(source_file)-4:] == '.cpp':
		    files_list.append({ 'source_file': source_file,
					'file_args': comp_args[:len(comp_args)-1] })
	except CompilationDatabaseError:
	    pprint(('Could not load compilation flags for ' + source_file))
    
    elif (opts.fList):
	if input_file[len(input_file)-4:] != '.txt':
	    pprint(('Invalid file format: ' + input_file + '. Should be .txt'))
	    return
	f = open(input_file, 'r')
	for line in f:
	    if line.strip() == '':
		continue
	    comp_args = re.split(' ', line.strip())
	    source_file = comp_args[len(comp_args)-1]
	    if len(comp_args) == 1:
		source_args = input_args
	    else:
		source_args = comp_args[:len(comp_args)-1]
	    if source_file[len(source_file)-4:] == '.cpp':
		files_list.append({ 'source_file': source_file,
				    'file_args': source_args })    
    else:
	if input_file[len(input_file)-4:] == '.cpp':
	    files_list.append({ 'source_file': input_file,
				'file_args': input_args })
	else:
	    pprint(('Invalid file format: ' + input_file + '. Should be .cpp'))
    import csv
    output_file_name = 'result.csv'
    with open(output_file_name, 'w') as csvfile:
	fieldnames = ['name', 'file_path', 'label', 'verb_in_name', 'template', 'is_inherited', 'constructors', 'total_methods', 'nonpublic_methods', 'static_methods',
	       'biggest_method_size', 'total_fields', 'nonpublic_fields', 'fields_class_refs', 'getters', 'setters', 'CG_edges', 'CG_no_entrance_vertexes',
	       'CG_no_out_vertexes', 'CG_comp_num', 'CG_strong_comp_num']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	index = Index.create()    
	classes = {}
	handled_classes = set()
	not_defined_classes = set()
	for src_file in files_list:
	    tu = index.parse(src_file['source_file'], src_file['file_args'])
	    if not tu:
		parser.error("unable to load file")
	    classes_defined_in_file = set()
	    visit_classdecl(tu.cursor, classes, handled_classes, not_defined_classes, classes_defined_in_file)
	    for class_def in classes_defined_in_file:
		if classes[class_def].are_methods_defined:
		    not_defined_classes.discard(class_def)
		    if classes.get(class_def) is not None:
			class_prec = classes.pop(class_def)
			if (opts.aPat):
			    class_prec.mark_class(classify(class_prec, clf))
			if (opts.cComs) | (opts.fList):
			    export_precedent(class_prec, writer)
			else:
			    if class_prec.label == 1:
				pprint(('Class ' + class_prec.name + ' in file ' + class_prec.file_name + ' is a FD anti-pattern.'))
			    elif class_prec.label == 0:
				pprint(('Class ' + class_prec.name + ' in file ' + class_prec.file_name + ' is not a FD anti-pattern.'))
			    pprint((class_prec.name + ' : ', class_prec.get_print_info()))
		    handled_classes.add(class_def)
    	for class_prec in classes:
	    if (opts.aPat):
		classes[class_prec].mark_class(classify(classes[class_prec], clf))
	    if (opts.cComs) | (opts.fList):
		export_precedent(classes[class_prec], writer)
	    else:
	      if classes[class_prec].label == 1:
		  pprint(('Class ' + classes[class_prec].name + ' in file ' + classes[class_prec].file_name + ' is a FD anti-pattern.'))
	      elif classes[class_prec].label == 0:
		  pprint(('Class ' + classes[class_prec].name + ' in file ' + classes[class_prec].file_name + ' is not a FD anti-pattern.'))
	      pprint((classes[class_prec].name + ' : ', classes[class_prec].get_print_info()))
	   
if __name__ == '__main__':
    main()
