from venv import create
from lxml import etree
import random
import uuid
import json
import yaml


class MyLookup(etree.CustomElementClassLookup):
  def lookup(self, node_type, document, namespace, name):
    if name == 'InternalElement':
      return InternalElement  
    if name == 'RoleClass':
      return RoleClass
    if name == 'RoleClassLib':
      return RoleClassLib
    if name == 'ExternalInterface':
      return ExternalInterface
    if name == 'Attribute':
      return Attribute
    if name == 'InterfaceClassLib':
      return InterfaceClassLib
    if name == 'InterfaceClass':
      return InterfaceClass
    if name == 'SystemUnitClassLib':
      return SystemUnitClassLib
    if name == 'SystemUnitClass':
      return SystemUnitClass
    if name == 'InstanceHierarchy':
      return InstanceHierarchy
    if name == 'MappingObject':
      return MappingObject
    if name == 'AttributeNameMapping':
      return AttributeNameMapping
    if name == 'InterfaceNameMapping':
      return InterfaceNameMapping
    if name == 'RoleRequirement':
      return RoleRequirement
    if name == "CAEXFile":
      return CAEXFile
    else:
      return AMLElement  # pass on to (default) fallback
parser = etree.XMLParser()
parser.set_element_class_lookup(MyLookup())

class AMLElement(etree.ElementBase):
  def _init(self): 
    #if self.get("ID")  == None and "ID" in common_concept[self.tag]:
    #  self.set("ID", str(uuid.uuid4()))
    pass

  def to_json(self, common_concept):
    aml_dict={} #Initial Dictionary that is getting filled witdh .aml data
    object_concept=common_concept[self.tag]  # Concept snippet of the element
    tag_list = object_concept["tags"] #Tags of the element
    attribute_list = object_concept["attributes"] #Tags of the element
    child_list = object_concept["children"]  #Children of the element


    #Step 1: Append tags
    for tag in tag_list:
      if self.get(tag) is not None and self.get(tag) != "" and self.get(tag) != "null":
        aml_dict[tag]= self.get(tag)

    #Step 2: Append Attributes
    for attribute in attribute_list:
      if self.find(attribute) is not None:
        #Exception Handling for weird RequiredValues in Constraints
        if len(self.findall(attribute))>1: 
          aml_dict[attribute]=[]
          for attribute_element in self.findall(attribute):
              aml_dict[attribute].append(attribute_element.text)
        #Normal case:
        else:
          aml_dict[attribute]= self.find(attribute).text


    #Step 3: Append Children
    for child in child_list:
      actual_children_list = self.findall(child) #As there can be multiple children with the same tag we need to find them all
      child_is_multivalued = common_concept[child]["multi"]
      if child_is_multivalued and actual_children_list: #if child is multivalued and actual children of that type exist:
        aml_dict[child] = []
        for kid in actual_children_list:
          aml_dict[child].append(kid.to_json(common_concept))
      elif actual_children_list: #if single valued and actual children of that type exist:
        aml_dict[child] = actual_children_list[0].to_json(common_concept) #use only existing element in list as kid
    
    return aml_dict

  def global_to_json(self, common_concept):

    # Step 0: Initialize root element and iterate from here
    aml_dict={} #Initial Dictionary that is getting filled with .aml data
    object_concept=common_concept[self.tag]  # Concept snippet of the element
    tag_list = object_concept["tags"] #Tags of the element
    attribute_list = object_concept["attributes"] #Tags of the element
    child_list = object_concept["children"]  #Children of the element

    #Step 0.1: Set up key reference
    key_list =list(tag_list)+list(attribute_list)
    value_list=[]

    #Step 1: Append tags and attributes
    for key in key_list:
      if key in tag_list:
        if self.get(key) is not None and self.get(key) != "null":
          value_list.append(self.get(key))
        else:
          value_list.append("")
      if key in attribute_list:
        if self.find(key) is not None and self.find(key) != "null":
          value_list.append(self.find(key).text)
        else:
          value_list.append("")
    aml_dict["values"]=value_list

    #Step 2: Append Children
    for child in child_list:
      abbreviated_child = common_concept[child]["abbreviation"]
      actual_children_list = self.findall(child) #As there can be multiple children with the same tag we need to find them all
      child_is_multivalued = common_concept[child]["multi"]
      if child_is_multivalued and actual_children_list: #if child is multivalued and actual children of that type exist:
        aml_dict[abbreviated_child] = []
        for kid in actual_children_list:
          aml_dict[abbreviated_child].append(kid.global_to_json(common_concept))
      elif actual_children_list: #if single valued and actual children of that type exist:
        aml_dict[abbreviated_child] = actual_children_list[0].global_to_json(common_concept) #use only existing element in list as kid

    return aml_dict



  def set_dict_properties(self, common_concept, json_dict):
    #Step 0.1: Initialize concepts
    object_concept=common_concept[self.tag]  
    tag_list = object_concept["tags"]
    attribute_list = object_concept["attributes"]
    child_list = object_concept["children"]

    #Augment dict from local() so that only needed values are included
    for key, value in json_dict.items():
      if value is None or value == "" or value == "None":
        json_dict.pop(key)

    #Put arguments from local into the appropriate category -> either tag or attribute of lxml with corresponding tag
    for key, value in json_dict.items():
      # Step 1: Key-Tags as Tags
      if key in tag_list:
        self.set(key, value)
      # Step 2: Key-Attribute as Attributes
      elif key in attribute_list:
        #Exception Handling for Constraints
        if not isinstance(value, list): # Normal case: items are just strings/integers, no lists
          attribute_child=etree.Element(key)
          attribute_child.text=str(value)
          self.append(attribute_child) 
        else: # Weird constraint case: List of items that we need back in single form
          for value_item in value:
            attribute_child=etree.Element(key)
            attribute_child.text=str(value_item)
            self.append(attribute_child) 
      # Step 3: Key-Attribute as Attributes 
      elif key in child_list:
        if type(value) == list:
          value_list = value # renaming for clarification as the value is actually a list of values 
          for item_dict in value_list:
              child = parser.makeelement(key)
              child.set_dict_properties(common_concept, item_dict)    
              self.append(child)
        elif type(value) == dict:
          item_dict = value # renaming for clarification 
          child = parser.makeelement(key)
          child.set_dict_properties(common_concept, item_dict)    
          self.append(child)

  #ToDO Finish factory method
  def addElement(self, key, **dict): # generic Adder
    pass

## Object Classes

class CAEXFile(AMLElement):
  def _init(self):
    #ToDo: Setup Writerheader and AdditionalInformation
    pass

  def create_from_json(self, common_concept:dict, dct:dict):
    self.set_dict_properties(common_concept, dct)
#### RoleClassLib and RoleClass

class RoleClassLib(AMLElement):
  def _init(self):
    super(RoleClassLib, self)._init()

class RoleClass(AMLElement):
  def _init(self):
    super(RoleClass, self)._init()

#### Internal Element:
class InternalElement(AMLElement):
  def _init(self):
    super(InternalElement, self)._init()
    #self.set("ChangeMode", "Change")

#### External Interface

class ExternalInterface(AMLElement):
  def _init(self):
    super(ExternalInterface, self)._init()

#### Internal Link

class InternalLink(AMLElement):
  def _init(self):
    super(InternalLink, self)._init()

#### Supported Role Class

class SupportedRoleClass(AMLElement):
  def _init(self):
    super(SupportedRoleClass, self)._init()

#### SUC Lib & SUC

class SystemUnitClassLib(AMLElement):
  def _init(self):
    super(SystemUnitClassLib, self)._init()

class SystemUnitClass(AMLElement):
  def _init(self):
    super(SystemUnitClass, self)._init()

#### Interface Class Lib & Interface Class

class InterfaceClassLib(AMLElement):
  def _init(self):
    super(InterfaceClassLib, self)._init()

class InterfaceClass(AMLElement):
  def _init(self):
    super(InterfaceClass, self)._init()

#### Instance Hierarchy

class InstanceHierarchy(AMLElement):
  def _init(self):
    super(InstanceHierarchy, self)._init()

#### Attribute

class Attribute(AMLElement):
  def _init(self):
    super(Attribute, self)._init()

####MappingObject


class MappingObject(AMLElement):
  def _init(self):
    super(MappingObject, self)._init()

####AttributeNameMapping

class AttributeNameMapping(AMLElement):
  def _init(self):
    super(AttributeNameMapping, self)._init()

####InterfaceNameMapping

class InterfaceNameMapping(AMLElement):
  def _init(self):
    super(InterfaceNameMapping, self)._init()

####RoleRequirement

class RoleRequirement(AMLElement):
  def _init(self):
    super(RoleRequirement, self)._init()


#nesting = None
#nesting = "local"
nesting = "global"

abbreviate=True

def load_common_concept(path):
  with open(path) as f:
    common_concept = json.load(f)
  return common_concept


def load_aml_file(path):
  aml_file= etree.parse(path, parser)
  aml_file= aml_file.getroot()
  return aml_file  

class AML_Dict(dict):
  def create_from_aml(self, aml_file, common_concept):
    pass

  def create_from_dict(self, dict):
    pass

  def store_as_json(self, output_path):
    with open(output_path, "w", encoding="utf-8") as outfile:
      json.dump(json_dct, outfile, ensure_ascii=False)
  

def create_key_dictionary():
  key_dict = {}
  #Create Keys
  for object_element in common_concept:
    object_concept = common_concept[object_element]
    tag_list = object_concept["tags"] #Tags of the element
    attribute_list = object_concept["attributes"] #Tags of the element
    key_dict[object_element]= list(tag_list) + list(attribute_list) 
  return key_dict


if __name__ == '__main__':
  common_concept = load_common_concept("config.json")
  aml_file = load_aml_file(r'./Examples/Testanlage.aml')

  #Create Normal AML-JSON File
  json_dct= aml_file.to_json(common_concept)
  with open("output.json", "w", encoding="utf-8") as outfile:
      json.dump(json_dct, outfile, ensure_ascii=False, indent=1)
  print("Created normal file")

  
  #Create Compressed AML-JSON File
  compressed_json_dct= aml_file.global_to_json(common_concept)
  keys = create_key_dictionary()
  compressed_json_dct["keys"]= keys 
  with open("output_global.json", "w", encoding="utf-8") as outfile:
    json.dump(compressed_json_dct, outfile, ensure_ascii=False)
  print("Created compressed file")

  #Create YAML-File because we can
  f = open('meta.yaml', 'w+')
  yaml.dump(json_dct, f, allow_unicode=True)
  print("Created normal file")
  f = open('compressed_meta.yaml', 'w+')
  yaml.dump(compressed_json_dct, f, allow_unicode=True)
  print("Created compressed file")

  #Create AML from JSON
  test_file = CAEXFile()
  test_file.create_from_json(common_concept, json_dct)
  doc = etree.ElementTree(test_file)
  print("Created element tree")
  outFile = open('output.xml', 'w')
  doc.write('output.xml', xml_declaration=False, encoding='utf-16') 
  print("Created aml")

  with open("config.json") as f:
      common_concept = json.load(f)
  aml_file= etree.parse(r'./Examples/Testbed.aml', parser)
  aml_file= aml_file.getroot()  
  json_dct= aml_file.to_json(common_concept)
  with open("Testbed.json", "w", encoding="utf-8") as outfile:
      json.dump(json_dct, outfile, ensure_ascii=False)
  compressed_json_dct= aml_file.global_to_json(common_concept)
  #with open("keys.json") as f:
  #  keys = json.load(f)
  #compressed_json_dct["keys"]= keys 
  #Step 3: Append Key-Dictionary
  f = open('meta.yaml', 'w+')
  yaml.dump(json_dct, f, allow_unicode=True)
  f = open('compressed_meta.yaml', 'w+')
  yaml.dump(compressed_json_dct, f, allow_unicode=True)

  with open("Testbed_global.json", "w", encoding="utf-8") as outfile:
      json.dump(json_dct, outfile, ensure_ascii=False, indent=1)
  test_file = CAEXFile()
  test_file.create_from_json(common_concept, json_dct)

  doc = etree.ElementTree(test_file)
  outFile = open('Testbed.xml', 'w')
  doc.write('Testbed.xml', xml_declaration=False, encoding='utf-16') 

