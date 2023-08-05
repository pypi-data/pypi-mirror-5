#coding=utf8

# Copyright © 2012 Tim Radvan
# 
# This file is part of Kurt.
# 
# Kurt is free software: you can redistribute it and/or modify it under the 
# terms of the GNU Lesser General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) any 
# later version.
# 
# Kurt is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR 
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more 
# details.
# 
# You should have received a copy of the GNU Lesser General Public License along 
# with Kurt. If not, see <http://www.gnu.org/licenses/>.

"""ObjTable - for de/serialising an object and its related objects.

(You probably want to use the classes in kurt.files directly.)

Otherwise, the main class in this file is ObjTable.
"""

from construct import *
from functools import partial
import inspect

from inline_objects import Field, Ref
from fixed_objects import *
import fixed_objects
from user_objects import *
import user_objects


class ObjectAdapter(Adapter):
    """Decodes a construct to a pythonic class representation.
    The class must have a from_construct classmethod and a to_construct 
    instancemethod.
    """
    def __init__(self, classes, *args, **kwargs):
        """Initialize an adapter for a new type/object(s).
        @param classes: class, list of classes, or dict of obj.classID name to 
        class mapping.
            eg ObjectAdapter({"String": String, "Array": Collection}, <subcon>)
        Note: Must use new-style objects, ie. subclasses of object.
        """
        Adapter.__init__(self, *args, **kwargs)
        
        if isinstance(classes, list):
            classes = dict((cls.__name__, cls) for cls in classes)
        self.classes = classes
    
    def _get_class(self, classID):
        if inspect.isclass(self.classes):
            return self.classes
        else:
            return self.classes[classID]
    
    def _encode(self, obj, context):
        """Encodes a class to a lower-level object using the class' own 
        to_construct function.
        If no such function is defined, returns the object unchanged.
        """
        func = getattr(obj, 'to_construct', None)
        if callable(func):
            return func(context)
        else:
            return obj
    
    def _decode(self, obj, context):
        """Initialises a new Python class from a construct using the mapping 
        passed to the adapter.
        """
        cls = self._get_class(obj.classID)
        return cls.from_construct(obj, context)


def obj_classes_from_module(module):
    """Return a list of classes in a module that have a 'classID' attribute."""
    for name in dir(module):
        if not name.startswith('_'):
            cls = getattr(module, name)
            if getattr(cls, 'classID', None):
                yield (name, cls)



### Fixed-format objects ###

fixed_object_classes = []
fixed_object_ids_by_name = {}
fixed_object_cons_by_name = {}

for (name, cls) in obj_classes_from_module(fixed_objects):
    fixed_object_classes.append(cls)
    fixed_object_ids_by_name[name] = cls.classID
    fixed_object_cons_by_name[name] = cls._construct

FixedObjectAdapter = partial(ObjectAdapter, fixed_object_classes)       

fixed_object = FixedObjectAdapter(Struct("fixed_object",
    Enum(UBInt8("classID"), **fixed_object_ids_by_name),
    Switch("value", lambda ctx: ctx.classID, fixed_object_cons_by_name),
))
fixed_object.__doc__ = """Construct for FixedObjects.
Stored in the object table. May contain references."""


### User-class objects ###

user_object_classes = []
user_object_ids_by_name = {}

for (name, cls) in obj_classes_from_module(user_objects):
    user_object_classes.append(cls)
    user_object_ids_by_name[name] = cls.classID

UserObjectAdapter = partial(ObjectAdapter, user_object_classes)

user_object = UserObjectAdapter(Struct("user_object",
    Enum(UBInt8("classID"),
        **user_object_ids_by_name
    ),
    UBInt8("version"),
    UBInt8("length"),
    Rename("field_values", MetaRepeater(lambda ctx: ctx.length, Field)),
))
user_object.__doc__ = """Construct for UserObjects.
Stored in the object table. May contain references."""


### Object Table ###

class PythonicAdapter(Adapter):
    """Converts from FixedObject classes to native Python types.
    * String -- python str
    * UTF8 -- python unicode
    * Dictionary -- dict
    * Array -- list/tuple
    """
    def _encode(self, obj, context):
        if isinstance(obj, str):
            return String(obj)
        elif isinstance(obj, unicode):
            return UTF8(obj)
        elif isinstance(obj, dict):
            return Dictionary(obj)
        elif isinstance(obj, list) or isinstance(obj, tuple):
            return Array(obj)
        elif isinstance(obj, Script):
            return Array(obj.to_array())
        else:
            return obj
    
    def _decode(self, obj, context):
        if isinstance(obj, String):
            return str(obj.value)
        elif isinstance(obj, UTF8):
            return unicode(obj.value)
        elif isinstance(obj, Dictionary):
            return obj.value
        elif isinstance(obj, Array):
            return obj.value
        else:
            return obj

class ObjectAdapter(Adapter):
    def _encode(self, obj, context):
        classID = obj.classID
        if classID in fixed_object_ids_by_name:
            classID = fixed_object_ids_by_name[classID]
        elif classID in user_object_ids_by_name:
            classID = user_object_ids_by_name[classID]
        return Container(
            classID = classID,
            object = obj,
        )
    
    def _decode(self, obj, context):
        return obj.object

_obj_table_entry = PythonicAdapter(ObjectAdapter(Struct("object",
    Peek(UBInt8("classID")),
    IfThenElse("object", lambda ctx: ctx.classID < 99,
        fixed_object,
        user_object,
    ),
)))
_obj_table_entry.__doc__ = """Construct for object table entries, both 
    UserObjects and FixedObjects."""


class ObjectTableAdapter(Adapter):
    def _encode(self, objects, context):
        return Container(
            header = "ObjS\x01Stch\x01",
            length = len(objects),
            objects = objects,
        )
    
    def _decode(self, table, context):
        assert table.length == len(table.objects), "File corrupt?"
        return table.objects


class ObjectNetworkAdapter(Adapter):
    """Object network <--> object table listing objects containing Refs"""
    def _encode(self, root, context):
        orig_objects = []
        
        def get_ref(value):            
            """Returns the index of the given object in the object table, 
            adding it if needed.
            """
            objects = self._objects
            
            value = PythonicAdapter(Pass)._encode(value, context)
            # Convert strs to FixedObjects here to make sure they get encoded 
            # correctly
            
            if isinstance(value, UserObject) or isinstance(value, FixedObject):
                if getattr(value, '_tmp_index', None):
                    index = value._tmp_index
                else:
                    objects.append(value)
                    index = len(objects)
                    value._tmp_index = index
                    orig_objects.append(value) # save the object so we can
                                               # strip the _tmp_indexes later
                return Ref(index)
            else:
                return value # Inline value
        
        def fix_fields(obj):
            obj = PythonicAdapter(Pass)._encode(obj, context)
            # Convert strs to FixedObjects here to make sure they get encoded
            # correctly
            
            if isinstance(obj, UserObject):
                fixed_obj = obj.to_construct(Container())
                fixed_obj.field_values = [get_ref(value) 
                                          for value in fixed_obj.field_values]
                #fixed_obj = obj.__class__(field_values, version = obj.version)
            
            elif isinstance(obj, Dictionary):
                fixed_obj = obj.__class__(dict(
                    (get_ref(field), get_ref(value))
                    for (field, value) in obj.value.items()
                ))
                
            elif isinstance(obj, dict):
                fixed_obj = dict(
                    (get_ref(field), get_ref(value)) 
                    for (field, value) in obj.items()
                )
                
            elif isinstance(obj, list):
                fixed_obj = [get_ref(field) for field in obj]
                
            elif isinstance(obj, Form):
                fixed_obj = obj.__class__(**dict(
                    (field, get_ref(value)) 
                    for (field, value) in obj.value.items()
                ))
                
            elif isinstance(obj, ContainsRefs):
                fixed_obj = obj.__class__([get_ref(field) 
                                           for field in obj.value])
                
            else:
                return obj
            
            fixed_obj._made_from = obj
            return fixed_obj
        
        root = PythonicAdapter(Pass)._encode(root, context)
        
        i = 0
        self._objects = objects = [root]
        root._tmp_index = 1
        while i < len(objects):
            objects[i] = fix_fields(objects[i])
            i += 1
        
        for obj in orig_objects:
            obj._tmp_index = None
            # Strip indexes off objects in case we want to save again later
        
        return objects
    
    def _decode(self, objects, context):        
        def resolve_ref(obj, objects=objects):
            if isinstance(obj, Ref):
                # first entry is 1
                return objects[obj.index - 1]
            else:
                return obj
        
        # Reading the ObjTable backwards somehow makes more sense.
        for i in xrange(len(objects)-1, -1, -1):
            obj = objects[i]
            
            if isinstance(obj, UserObject):
                for field_name in obj.fields:
                    value = obj.fields[field_name]
                    value = resolve_ref(value)
                    obj.fields[field_name] = value
            
            elif isinstance(obj, Dictionary):
                obj.value = dict(
                    (resolve_ref(field), resolve_ref(value)) 
                    for (field, value) in obj.value.items()
                )
            
            elif isinstance(obj, dict):
                obj = dict(
                    (resolve_ref(field), resolve_ref(value)) 
                    for (field, value) in obj.items()
                )
            
            elif isinstance(obj, list):
                obj = [resolve_ref(field) for field in obj]
            
            elif isinstance(obj, Form):
                for field in obj.value:
                    value = getattr(obj, field)
                    value = resolve_ref(value)
                    setattr(obj, field, value)
            
            elif isinstance(obj, ContainsRefs):
                obj.value = [resolve_ref(field) for field in obj.value]
            
            objects[i] = obj
        
        for obj in objects:
            if isinstance(obj, UserObject) or isinstance(obj, Form):
                obj.built()
        
        root = objects[0]
        return root

_obj_table_entries = ObjectTableAdapter(Struct("object_table",
    Const(Bytes("header", 10), "ObjS\x01Stch\x01"),
    UBInt32("length"),
    Rename("objects", MetaRepeater(lambda ctx: ctx.length, _obj_table_entry)),
))

ObjTable = ObjectNetworkAdapter(_obj_table_entries)
ObjTable.__doc__ = """Construct for parsing a binary object table to pythonic 
    object(s).
    """ #Includes "ObjS\\x01Stch\\x01" header.

class InfoTableAdapter(Subconstruct):
    """Info ObjTable found in the project header.
    Adds the preceding info_size header (4 bytes).
    
    Parses to a Dictionary. Includes the following keys:
        thumbnail - image showing a small picture of the stage when the project 
                    was saved
        author - name of the user who saved or shared this project
        comment - author's comments about the project
        history - a string containing the project save/upload history
        scratch-version - the version of Scratch that saved the project
    """
    info_size = UBInt32("info_size")
    
    def _parse(self, stream, context):
        self.info_size._parse(stream, Container())
        objtable = self.subcon._parse(stream, context)
        return objtable
    
    def _build(self, obj, stream, context):
        bytes = self.subcon.build(obj)
        size = len(bytes)
        stream.write(self.info_size.build(size))
        stream.write(bytes)
        
InfoTable = InfoTableAdapter(ObjTable)



ScratchStageMorph = Stage
ScratchSpriteMorph = Sprite
ImageMedia = Image
SoundMedia = Sound

__all__ = [
    'ObjTable', '_obj_table_entry', '_obj_table_entries', 
    'UserObject', 'FixedObject', 'Field', 
    'ScratchStageMorph', 'ScratchSpriteMorph',
] + [cls.__name__ for cls in fixed_object_classes + user_object_classes]
