import json
from utils import create_new_aml

from classes import AMLElement

class AML_Dict(dict):
    def create_from_aml(self, aml_file, common_concept):
        pass

    def create_from_dict(self, dict):
        pass

    def convert_to_aml(self, common_concept) -> AMLElement:
        aml_element:AMLElement=create_new_aml() #Create new lxml element tree to write in
        config=self.derive_settings() #Derive config settings from current json
        aml_element.set_properties(self, aml_element, common_concept)
        
        return aml_element

        
