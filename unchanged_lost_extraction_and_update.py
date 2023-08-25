import geopandas as gpd
import json
from copy import deepcopy

''' the following functions have as objectives: 

- extract_unchanged_from_model: extracting only the unchanged (or lost) buildings from the existing model using a matching between CityObjects names in the model and building indentifier attribute in the shapefile extracted from the model 

- change_update: adding the change_type as an attribute 
'''

def extract_unchanged_from_model(fp_unchanged, model, output_model):
    # read the CityJSON file
    with open(model) as file:
        cityjson_data = json.load(file)

    # Read the shapefile containing footprints
    footprints = gpd.read_file(fp_unchanged)

    # Get the attributes from the shapefile that correspond to the buildings' identifiers
    building_ids = footprints['uid']
    building_ids = list(building_ids)

    children_ids = footprints['children']
    children_ids = list(children_ids)
    children_ids = [item[2:-2] for item in children_ids]
    children_ids = [item.split("', '") for item in children_ids]
    children_ids1 = []

    for elem in children_ids:
        if isinstance(elem, list) and len(elem) > 1:
            children_ids1.extend([sub_elem] for sub_elem in elem)
        else:
            children_ids1.append(elem)
    children_ids1 = [item[0] for item in children_ids1]

    # Create a new CityJSON object
    new_cityjson_data = deepcopy(cityjson_data)

    # Remove buildings based on matching with the foorprints' identifiers in the disappeared_buildings.shp file
    for (key, value) in cityjson_data['CityObjects'].items():
        if key not in children_ids1 and key not in building_ids:
            new_cityjson_data['CityObjects'].pop(key)

    # Save the new CityJSON file
    with open(output_model, 'w') as file:
        json.dump(new_cityjson_data, file)


def change_update(model, change_type, updated_model):

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

    # Save the new CityJSON file
    with open(updated_model, 'w') as file:
        json.dump(new_cityjson_data, file)
