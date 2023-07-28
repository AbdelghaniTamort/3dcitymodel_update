import geopandas as gpd
import shapely
import laspy


def save_intersecting_polygons(ahn4_shp, ahn3_shp, ahn4_pc, ahn3_pc, ahn3_tempo, ahn4_tempo,  new, lost, ahn3_rest, ahn4_rest):

    # reading the shapefiles
    shapefile1 = gpd.read_file(ahn4_shp)
    shapefile2 = gpd.read_file(ahn3_shp)
    # setting the crs
    shapefile1.crs = "EPSG:28992"
    shapefile2.crs = "EPSG:28992"

    # read the pointclouds using laspy
    las_file1 = laspy.read(ahn3_pc)
    las_file2 = laspy.read(ahn4_pc)

    # create a GeoDataFrame from the x,y coordinates of the point clouds
    points_ahn3 = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        las_file1.x, las_file1.y), crs="EPSG:28992")
    points_ahn4 = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        las_file2.x, las_file2.y), crs="EPSG:28992")

    # creating empty lists temporary , new and lost polygons
    temp_polygons = []
    ahn3_temp = []
    ahn4_temp = []
    temp_polygons1 = []
    new_polygons = []
    lost_polygons = []
    rest_ahn3_polygons = []
    rest_ahn4_polygons = []

    # creating a spatial index for the ahn3 and ahn4 point clouds
    points_ahn3_sindex = points_ahn3.sindex
    points_ahn4_sindex = points_ahn4.sindex

    # Define a buffer distance to select nearby points
    buffer_distance = 1

    # creating a new list with the polygons from AHN3 that with at least a point from AHN3 point cloud

    for polygon in shapefile2.geometry:
        # Create a buffer around the polygon to find nearby points efficiently.
        polygon_buffered_ahn3 = polygon.buffer(buffer_distance)
    # Use the spatial index to find candidate points within the buffer.
        candidate_points_idx_ahn3 = list(
            points_ahn3_sindex.intersection(polygon_buffered_ahn3.bounds))
    # Check for actual intersection for each candidate point.
        for idx in candidate_points_idx_ahn3:
            point = points_ahn3.geometry.iloc[idx]
            if point.intersects(polygon):
                ahn3_temp.append(polygon)
                # Stop checking once an intersection is found for the polygon.
                break

    # creating a new list with the polygons from AHN4 that with at least a point from AHN4 point cloud
    for poly in shapefile1.geometry:
        # Create a buffer around the polygon to find nearby points efficiently.
        polygon_buffered_ahn4 = poly.buffer(buffer_distance)
        # Use the spatial index to find candidate points within the buffer.
        candidate_points_idx_ahn4 = list(
            points_ahn4_sindex.intersection(polygon_buffered_ahn4.bounds))
        # Check for actual intersection for each candidate point.
        for idx in candidate_points_idx_ahn4:
            point = points_ahn4.geometry.iloc[idx]
            if point.intersects(poly):
                ahn4_temp.append(poly)
                # Stop checking once an intersection is found for the polygon.
                break

    # adding polygons from AHN4 that intersect with AHN3 to a temporary list (temp_polygons)
    for poly in ahn4_temp:
        for poly1 in ahn3_temp:
            if shapely.intersects(poly, poly1):
                temp_polygons.append(poly)

    # adding polygons from AHN3 that intersect with AHN4 to a temporary list (temp_polygons1)
    for poly in ahn3_temp:
        for poly1 in ahn4_temp:
            if shapely.intersects(poly, poly1):
                temp_polygons1.append(poly)

    # adding polygons from AHN4 that do not intersect with AHN3 to a new list (new_polygons)
    for poly in ahn4_temp:
        if poly not in temp_polygons:
            new_polygons.append(poly)
        else:
            rest_ahn4_polygons.append(poly)

    # adding polygons from AHN3 that do not intersect with AHN4 to a new list (lost_polygons)
    for poly in ahn3_temp:
        if poly not in temp_polygons1:
            lost_polygons.append(poly)
        else:
            rest_ahn3_polygons.append(poly)

    # converting the lists to geodataframes and joining them with the original shapefiles to add the attributes

    ahn3_temp = gpd.GeoDataFrame(geometry=ahn3_temp, crs="EPSG:28992")
    ahn4_temp = gpd.GeoDataFrame(geometry=ahn4_temp, crs="EPSG:28992")
    ahn3_temp = gpd.sjoin(ahn3_temp, shapefile2,
                          how="inner", predicate="within")
    ahn4_temp = gpd.sjoin(ahn4_temp, shapefile1,
                          how="inner", predicate="within")
    ahn3_temp = ahn3_temp.drop(columns=["index_right"])
    ahn4_temp = ahn4_temp.drop(columns=["index_right"])

    new_polygons = gpd.GeoDataFrame(
        geometry=new_polygons, crs="EPSG:28992")
    new_polygons = gpd.sjoin(
        new_polygons, shapefile1, how="inner", predicate="within")
    new_polygons = new_polygons.drop(columns=["index_right"])

    lost_polygons = gpd.GeoDataFrame(geometry=lost_polygons, crs="EPSG:28992")
    lost_polygons = gpd.sjoin(
        lost_polygons, shapefile2, how="inner", predicate="within")
    lost_polygons = lost_polygons.drop(columns=["index_right"])

    rest_ahn3_polygons = gpd.GeoDataFrame(
        geometry=rest_ahn3_polygons, crs="EPSG:28992")
    rest_ahn3_polygons = gpd.sjoin(
        rest_ahn3_polygons, shapefile2, how="inner", predicate="within")
    rest_ahn3_polygons = rest_ahn3_polygons.drop(columns=["index_right"])

    rest_ahn4_polygons = gpd.GeoDataFrame(
        geometry=rest_ahn4_polygons, crs="EPSG:28992")
    rest_ahn4_polygons = gpd.sjoin(
        rest_ahn4_polygons, shapefile1, how="inner", predicate="within")
    rest_ahn4_polygons = rest_ahn4_polygons.drop(columns=["index_right"])

    return new_polygons.to_file(new), lost_polygons.to_file(lost), rest_ahn3_polygons.to_file(ahn3_rest), rest_ahn4_polygons.to_file(ahn4_rest), ahn3_temp.to_file(ahn3_tempo), ahn4_temp.to_file(ahn4_tempo)


def save_ahn4_ahn3_pc_without_new_and_lost(ahn3_rest, ahn4_rest, ahn3_pc, ahn4_pc, ahn3_filtered, ahn4_filtered):

    # reading the shapefiles
    shapefile1 = gpd.read_file(ahn3_rest)
    shapefile2 = gpd.read_file(ahn4_rest)

    # setting the crs
    shapefile1.crs = "EPSG:28992"
    shapefile2.crs = "EPSG:28992"

    # read the pointclouds using laspy
    las_file1 = laspy.read(ahn3_pc)
    las_file2 = laspy.read(ahn4_pc)

    # create a GeoDataFrame from the x,y coordinates of the point clouds
    points_ahn3 = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        las_file1.x, las_file1.y), crs="EPSG:28992")
    points_ahn4 = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        las_file2.x, las_file2.y), crs="EPSG:28992")

    # clip the point cloud to the polygon
    clipped_points_ahn3 = points_ahn3.clip(shapefile1)
    clipped_points_ahn4 = points_ahn4.clip(shapefile2)

    # create a new laspy file objects
    ahn3_changed = laspy.create(point_format=las_file1.header.point_format,
                                file_version=las_file1.header.version)
    ahn4_changed = laspy.create(
        point_format=las_file2.header.point_format, file_version=las_file2.header.version)

    # setting the same scalar fields for the new las files
    # for ahn3
    ahn3_changed.x = clipped_points_ahn3.geometry.x.values
    ahn3_changed.y = clipped_points_ahn3.geometry.y.values
    ahn3_changed.z = las_file1.z[clipped_points_ahn3.index]
    ahn3_changed.intensity = las_file1.intensity[clipped_points_ahn3.index]
    ahn3_changed.classification = las_file1.classification[clipped_points_ahn3.index]
    ahn3_changed.gps_time = las_file1.gps_time[clipped_points_ahn3.index]
    ahn3_changed.user_data = las_file1.user_data[clipped_points_ahn3.index]
    ahn3_changed.return_number = las_file1.return_number[clipped_points_ahn3.index]
    ahn3_changed.number_of_returns = las_file1.number_of_returns[clipped_points_ahn3.index]
    ahn3_changed.edge_of_flight_line = las_file1.edge_of_flight_line[clipped_points_ahn3.index]
    ahn3_changed.red = las_file1.red[clipped_points_ahn3.index]
    ahn3_changed.green = las_file1.green[clipped_points_ahn3.index]
    ahn3_changed.blue = las_file1.blue[clipped_points_ahn3.index]
    # for ahn4
    ahn4_changed.x = clipped_points_ahn4.geometry.x.values
    ahn4_changed.y = clipped_points_ahn4.geometry.y.values
    ahn4_changed.z = las_file2.z[clipped_points_ahn4.index]
    ahn4_changed.intensity = las_file2.intensity[clipped_points_ahn4.index]
    ahn4_changed.classification = las_file2.classification[clipped_points_ahn4.index]
    ahn4_changed.gps_time = las_file2.gps_time[clipped_points_ahn4.index]
    ahn4_changed.user_data = las_file2.user_data[clipped_points_ahn4.index]
    ahn4_changed.return_number = las_file2.return_number[clipped_points_ahn4.index]
    ahn4_changed.number_of_returns = las_file2.number_of_returns[clipped_points_ahn4.index]
    ahn4_changed.edge_of_flight_line = las_file2.edge_of_flight_line[clipped_points_ahn4.index]
    ahn4_changed.red = las_file2.red[clipped_points_ahn4.index]
    ahn4_changed.green = las_file2.green[clipped_points_ahn4.index]
    ahn4_changed.blue = las_file2.blue[clipped_points_ahn4.index]

    return ahn3_changed.write(ahn3_filtered), ahn4_changed.write(ahn4_filtered)


save_intersecting_polygons("inputs/footprints/ahn4.shp", "inputs/footprints/model.shp", "inputs/pointcloud/AHN4_buildings_clip.laz", "inputs/pointcloud/AHN3_buildings_clip.laz", "outputs/facets/ahn3_temp.shp", "outputs/facets/ahn4_temp.shp",
                           "outputs/facets/new.shp", "outputs/facets/lost.shp", "outputs/facets/ahn3_rest.shp", "outputs/facets/ahn4_rest.shp")
save_ahn4_ahn3_pc_without_new_and_lost("outputs/facets/ahn3_rest.shp", "outputs/facets/ahn4_rest.shp", "inputs/pointcloud/AHN3_buildings_clip.laz",
                                    "inputs/pointcloud/AHN4_buildings_clip.laz", "outputs/pointcloud/ahn3_no_new_no_lost.laz", "outputs/pointcloud/ahn4_no_new_no_lost.laz")
