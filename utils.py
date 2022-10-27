from lxml import etree
import json
from classes import parser, AMLElement, CAEXFile
import yaml

def load_common_concept(path:str):
  with open(path) as f:
    common_concept = json.load(f)
  return common_concept

def load_aml_file(path:str):
  aml_file= etree.parse(path, parser)
  aml_file= aml_file.getroot()
  return aml_file  


def create_key_dictionary(common_concept:dict):
  key_dict = {}
  #Create Keys
  for object_element in common_concept:
    object_concept = common_concept[object_element]
    tag_list = object_concept["tags"] #Tags of the element
    attribute_list = object_concept["attributes"] #Tags of the element
    key_dict[object_element]= list(tag_list) + list(attribute_list) 
  return key_dict


#Create Normal AML-JSON File
def convert_aml_to_dict(aml_file: AMLElement, common_concept: dict, compressed=False, abbreviate=False, add_missing_id=False, delete_unused_classes=False):
    if compressed == False:
        json_dct= aml_file.to_json(common_concept)
        print("Successfully created normal AML dictionary")
    else: 
        json_dct= aml_file.global_to_json(common_concept)
        print("Successfully created compressed AML dictionary")
    return json_dct


def store_dict_as_json(dct:dict, json_output_name:str, indent=1):
    with open(json_output_name, "w", encoding="utf-8") as outfile:
        json.dump(dct, outfile, ensure_ascii=False, indent=indent)
    print("Successfully stored as JSON")


def store_dict_as_yaml(dct:dict, yaml_output_name:str):
    f = open(yaml_output_name, 'w+')
    yaml.dump(dct, f, allow_unicode=True)
    print("Created YAML file")

def create_new_aml() -> AMLElement:
    aml_element = CAEXFile()
    return aml_element