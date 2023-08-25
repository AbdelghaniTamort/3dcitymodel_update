import geopandas as gpd
import shapely
import laspy

''' The following functions' objectives are : 

  - save_intersecting_polygons: creating 2 shapefiles, one containing instances of changed buildings and the other instances of unchanged ones
  - save_changed_unchanged_pc: for each of the building instances in the changed and unchanged shapefiles, a pointcloud is created using the clip operation 
'''

def save_intersecting_polygons(ahn4_no_new_no_lost_shp, ahn3_no_new_no_lost_shp, ahn4_changed_pc, changed, unchanged):
  
    # reading the pointcloud
    las_file = laspy.read(ahn4_changed_pc)
  
    # storing the values of the "original cloud index" scalar field into an attribute called "index"
    data = {'index': las_file.Original__cloud__index}
  
    # projecting the points onto the XY plane
    points_ahn4 = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(
        las_file.x, las_file.y), crs="EPSG:28992")
  
    # reading the shapefiles
    polygons = gpd.read_file(ahn4_no_new_no_lost_shp)
    polygons2 = gpd.read_file(ahn3_no_new_no_lost_shp)

    # Create spatial index on the points GeoDataFrame
    points_ahn4_sindex = points_ahn4.sindex

    # creating empty lists
    changed_list = []
    unchanged_list_temp = []
    unchanged_list = []
  
    # fixing the number of required points having the same index
    required_intersection_count = 100
  
    # Check for intersection and count points with the same attribute value
    for polygon in polygons.geometry:
        # for each polygon, check which points intersect
        candidate_points_index = list(
            points_ahn4_sindex.intersection(polygon.bounds))
        for idx in candidate_points_index:
            point = points_ahn4.geometry.iloc[idx]
            if point.intersects(polygon):
                # check if at least 100 points have the same attribute "index"
                # Access the "index" attribute and count occurrences of each value
                index_counts = points_ahn4['index'].value_counts()
                # Check if any value occurs at least 100 times
                at_least_100_occurrences = any(
                    index_counts >= required_intersection_count)
                if at_least_100_occurrences:
                    changed_list.append(polygon)
                    break

    # check for intersection between changed_list and polygons
    # if no intersection, add to unchanged_list_temp
    for poly in polygons.geometry:
        if poly not in changed_list:
            unchanged_list_temp.append(poly)
    # matching unchanged buildings from ahn4 with unchanged buildings from the model
    for poly in polygons2.geometry:
        for poly1 in unchanged_list_temp:
            if poly.intersects(poly1):
                if poly.intersection(poly1).area > 0.3*poly.area:
                    unchanged_list.append(poly)

    # converting the lists into geodataframes and attaching attributes
    changed_list = gpd.GeoDataFrame(geometry=changed_list, crs="EPSG:28992")
    changed_list = gpd.sjoin(changed_list, polygons,
                             how="inner", predicate="within")
    changed_list = changed_list.drop(columns=["index_right"])

    unchanged_list = gpd.GeoDataFrame(
        geometry=unchanged_list, crs="EPSG:28992")
    unchanged_list = gpd.sjoin(
        unchanged_list, polygons2, how="inner", predicate="within")
    unchanged_list = unchanged_list.drop(columns=["index_right"])

    return changed_list.to_file(changed), unchanged_list.to_file(unchanged)


save_intersecting_polygons('outputs/facets/AHN4_rest.shp', "outputs/facets/AHN3_rest.shp",
                           'outputs/pointcloud/changed_cc.laz', "outputs/facets/AHN4_changed.shp", "outputs/facets/AHN3_unchanged.shp")


def save_changed_unchanged_pc(changed_shp, unchanged_shp, ahn4_rest_pc, changed_pc, unchanged_pc):

    # read in the pointcloud
    las_file = laspy.read(ahn4_rest_pc)

    # read in the changed and unchanged polygons
    changed_poly = gpd.read_file(changed_shp)
    unchanged_poly = gpd.read_file(unchanged_shp)

    # create a GeoDataFrame from the x,y coordinates of the point clouds
    points = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        las_file.x, las_file.y), crs="EPSG:28992")

    # clip the point cloud to the polygon
    clipped_points_unchanged = points.clip(unchanged_poly)
    clipped_points_changed = points.clip(changed_poly)

    #  create a new laspy file objects
    changed = laspy.create(point_format=las_file.header.point_format,
                           file_version=las_file.header.version)
    unchanged = laspy.create(
        point_format=las_file.header.point_format, file_version=las_file.header.version)

    # setting the same scalar fields for the new las files
    # changed
    changed.x = clipped_points_changed.geometry.x.values
    changed.y = clipped_points_changed.geometry.y.values
    changed.z = las_file.z[clipped_points_changed.index]
    changed.intensity = las_file.intensity[clipped_points_changed.index]
    changed.classification = las_file.classification[clipped_points_changed.index]
    changed.gps_time = las_file.gps_time[clipped_points_changed.index]
    changed.user_data = las_file.user_data[clipped_points_changed.index]
    changed.return_number = las_file.return_number[clipped_points_changed.index]
    changed.number_of_returns = las_file.number_of_returns[clipped_points_changed.index]
    changed.edge_of_flight_line = las_file.edge_of_flight_line[clipped_points_changed.index]
    changed.red = las_file.red[clipped_points_changed.index]
    changed.green = las_file.green[clipped_points_changed.index]
    changed.blue = las_file.blue[clipped_points_changed.index]
    # unchanged
    unchanged.x = clipped_points_unchanged.geometry.x.values
    unchanged.y = clipped_points_unchanged.geometry.y.values
    unchanged.z = las_file.z[clipped_points_unchanged.index]
    unchanged.intensity = las_file.intensity[clipped_points_unchanged.index]
    unchanged.classification = las_file.classification[clipped_points_unchanged.index]
    unchanged.gps_time = las_file.gps_time[clipped_points_unchanged.index]
    unchanged.user_data = las_file.user_data[clipped_points_unchanged.index]
    unchanged.return_number = las_file.return_number[clipped_points_unchanged.index]
    unchanged.number_of_returns = las_file.number_of_returns[clipped_points_unchanged.index]
    unchanged.edge_of_flight_line = las_file.edge_of_flight_line[clipped_points_unchanged.index]
    unchanged.red = las_file.red[clipped_points_unchanged.index]
    unchanged.green = las_file.green[clipped_points_unchanged.index]
    unchanged.blue = las_file.blue[clipped_points_unchanged.index]

    return changed.write(changed_pc), unchanged.write(unchanged_pc)
