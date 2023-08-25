import json
from copy import deepcopy

''' The following function is used to add the change_type attribute to the input changed or new CityJson model
'''

def change_update(model, change_type, prefix, updated_model):

    # Read the CityJSON file
    with open(model) as file:
        cityjson_data = json.load(file)

    # Create a new CityJSON object
    new_cityjson_data = deepcopy(cityjson_data)

    # add the 'change_type' attribute to the CityObjects
    for (key, value) in cityjson_data['CityObjects'].items():
        # New attributes dictionary
        new_attributes = {'change_type': change_type}
        new_attributes.update(value['attributes'])  # Add existing attributes
        new_cityjson_data['CityObjects'][key]['attributes'] = new_attributes

    for key in list(cityjson_data['CityObjects'].keys()):
        modified_key = prefix + key
        new_cityjson_data['CityObjects'][modified_key] = new_cityjson_data['CityObjects'].pop(
            key)

    for key, value in new_cityjson_data['CityObjects'].items():
        if "children" in value:
            children = value['children']
            updated_list = [prefix + element for element in children]
            value['children'] = updated_list
        if "parents" in value:
            if value['parents'] is not None:
                parents = value['parents']
                updated_list = [prefix + element for element in parents]
                value['parents'] = updated_list

    # Save the new CityJSON file
    with open(updated_model, 'w') as file:
        json.dump(new_cityjson_data, file)
