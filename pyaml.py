<<<<<<< HEAD
from  lxml import etree
from classes import CAEXFile
from utils import load_aml_file, load_common_concept, create_key_dictionary, convert_aml_to_dict, store_dict_as_json, store_dict_as_yaml

if __name__ == '__main__':
  common_concept:dict = load_common_concept("common_concept.json")
  aml_file = load_aml_file(r'./Examples/FLC.aml')

  #Create Dictionary
  json_dct = convert_aml_to_dict(aml_file, common_concept)
  #Create Normal AML-JSON File
  store_dict_as_json(json_dct, "output.json", indent=None)

  compressed_json_dct = convert_aml_to_dict(aml_file, common_concept, compressed=True)
  keys = create_key_dictionary(common_concept)
  compressed_json_dct["keys"]= keys 
  
  #Create Compressed AML-JSON File
  store_dict_as_json(compressed_json_dct, "output_global.json", indent=None)

  #Create YAML-File because we can
  store_dict_as_yaml(json_dct, "meta.yaml")
  store_dict_as_yaml(compressed_json_dct, "compressed_meta.yaml")

  #Create AML from JSON
  test_file = CAEXFile()
  test_file.create_from_json(common_concept, json_dct)
  doc = etree.ElementTree(test_file)
  print("Created element tree")
  outFile = open('output.xml', 'w')
  doc.write('output.xml', xml_declaration=False, encoding='utf-16') 
  print("Created aml")
