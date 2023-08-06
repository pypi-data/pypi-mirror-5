=======
EStruct
=======

EStruct provides an extended packaging/unpackaging library that that provided by the standard library's Struct module.
It provides packaging of conditional elements and arrays. The library was originally written by the author to simplify 
packing and unpacking binary data within mpeg4 file.

Typical usage::

	#!/usr/bin/env python
	
	from estruct.estruct import EStruct
	import sys
	from datetime import date
	
	packager = EStruct("Student", "Student.Name Student.Address Student.DOB", "![50s50sQ]")
	records=[]
	with open(sys.argv[1],"rb") as f:
		records=packager.unpack(f.read())
    	
	for r in records:
		print r.Student.Name, r.Student.Address, date.fromordinal(r.Student.DOB)
		
EStruct is also hosted on GitHub at https://github.com/simblack/EStruct

 		
Installation
============
::

	pip install EStruct


EStruct object
==============

The EStruct object __init__ method takes three parameters, the unpacked class name, the fields within the class and the packaging format.

*EStruct.__init__(self, name, fields_string, format_string)*

name
----

This is simply the name of the object that is created when unpacking values.

fields_string
-------------

The fields string is a description that contains fields and sub fields.
The string needs to be a space separated list of fields. Nested structures can be created by using a dot notation '.', i.e.
object.field or object.sub_object.field.
        
Example::

    'f1 f2 f3.a1 f3.a2 f4 f5.a1.b1 f5.a1.b2 f5.a2.b1 f5.a2.b2'
    This would create the object with fields:
        f1,f2,f3,f4,f5
    f3 is of a type of an object with fields:
        a1, a2
    f5 is of a type of an object with fields:
        a1, a2 with both fields of an object of type with fields b1 and b2 

format_string
-------------
::

    format= byteorder + format_string
    byte_order= '@'|'='|'<'|'>'|'!'
        @ native byte-order    native size        native alignment
        = native byte-order    standard size      no alignment
        < little endian        standard size      no alignment
        > big endian           standard size      no alignment
        ! network              standard size      no alignment
        
    format_string=      conditonal_format | array_format | normal_format | empty_format
    
    emptry_format=
    
    conditionl_format=  '(' + condition + '?' + true_format + ':' + false_format + ')' 
    condition=          [python evaluation]
    true_format=        format_string
    false_format=       format_string
    An empty format_string implies that no field is required for packinging.
    
    array_format=       count[format_string]
    
    count=              empty_count | constant_count | field_count
    empty_count=
    constant_count=    (0..9)*
    field_count=       '{' + [field_name] + '}'
   
The *\[field name\]* is any field defined prior to this packing element.
The *\[python evaluation\]* is a valid python statement equating to a True or False result. 
Any field name prior to this packing element may be used. Also for evaulation of array's the index value *INDEX* may be used
to specify the current index.
    
Examples
~~~~~~~~
Network endian, 32 bit integers followed by a 64 but value if *f1==1* else another 32 bit integer::

	!II(f1==1?Q|I)

Network endian, 32 bit integers followed by an array with the number of elements as specified in the field
*f1*. The array elements are a 32 bit integer followed by a number of characters, where that number is set in 
the field *f2\[INDEX\].a1*, the index is the current iteration of the outer array.::

	!I{f1}[I{f2[INDEX].a1}[c]]

	
Unpacking
=========

The unpack method is used to unpack binary data into an object
 
*EStruct.unpack(self, data, **kargs)*

Keyword arguments may also be passed if they are required for evaluations.
The method returns an object as described by the fields string of the constructor.

::

	struct=EStruct('Test','f1 f2','!I{f1}[I]')
	
	data=[0,0,0,3,0,0,0,2,0,0,0,1,0,0,0,0]
	data_str="".join([chr(x) for x in data])
	obj=struct.unpack(data_str)
	
	print obj.f1, obj.f2
		

Packing
=======

The pack method is used to pack values into a binary string

*EStruct.pack(self, *args, **kargs)*

The correct number of arguments must be passed for packing, according to the packing format.
Keyword arguments may also be passed if they are required for evaluations.
The method returns the packed binary string.

::

	struct=EStruct('Test','f1 f2','!I{f1}[I]')
	packed_result=self.struct.pack(3,[2,1,0])
	
	print packed_result.encode("hex")