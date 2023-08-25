import geopandas as gpd
import laspy

''' this function is used to clip a pointcloud using the polygons within a shapefile. In other words, the newly generated pointcloud only contains points lay within each polygon in the shapefile when projected to the XY plane'''


def crop_pc_using_footprints(pc, footprints, pc_output):

    # read in the las file using laspy
    las_file = laspy.read(pc)

    # create a GeoDataFrame from the x,y coordinates of the point cloud
    points = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        las_file.x, las_file.y), crs="EPSG:28992")

    # convert a shapefile into a geodataframes
    polygon = gpd.read_file(footprints)

    # clip the point cloud to the polygon
    clipped_points = points.clip(polygon)

    # create a new laspy file object
    new_las = laspy.create(point_format=las_file.header.point_format,
                           file_version=las_file.header.version)

    # set the x, y, and z values of the new las file
    new_las.x = clipped_points.geometry.x.values
    new_las.y = clipped_points.geometry.y.values
    new_las.z = las_file.z[clipped_points.index]
    new_las.point_source_id = las_file.point_source_id[clipped_points.index]
    new_las.intensity = las_file.intensity[clipped_points.index]
    new_las.classification = las_file.classification[clipped_points.index]
    new_las.gps_time = las_file.gps_time[clipped_points.index]
    new_las.user_data = las_file.user_data[clipped_points.index]
    new_las.return_number = las_file.return_number[clipped_points.index]
    new_las.number_of_returns = las_file.number_of_returns[clipped_points.index]
    new_las.edge_of_flight_line = las_file.edge_of_flight_line[clipped_points.index]
    new_las.red = las_file.red[clipped_points.index]
    new_las.green = las_file.green[clipped_points.index]
    new_las.blue = las_file.blue[clipped_points.index]

    return new_las.write(pc_output)
