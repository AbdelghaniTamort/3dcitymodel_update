import geopandas as gpd
import shapely


def save_intersecting_polygons(ahn4, ahn3,  new, lost):

    # reading the shapefiles
    shapefile1 = gpd.read_file(ahn4)
    shapefile2 = gpd.read_file(ahn3)
    # setting the crs
    shapefile1.crs = "EPSG:28992"
    shapefile2.crs = "EPSG:28992"

    # creating empty lists temporary , new and lost polygons
    temp_polygons = []
    temp_polygons1 = []
    new_polygons = []
    lost_polygons = []

    # adding polygons from AHN4 that intersect with AHN3 to a temporary list (temp_polygons)
    for poly in shapefile1.geometry:
        for poly1 in shapefile2.geometry:
            if shapely.intersects(poly, poly1):
                temp_polygons.append(poly)

    # adding polygons from AHN3 that intersect with AHN4 to a temporary list (temp_polygons1)
    for poly in shapefile1.geometry:
        for poly1 in shapefile2.geometry:
            if shapely.intersects(poly, poly1):
                temp_polygons1.append(poly1)

    # adding polygons from AHN4 that do not intersect with AHN3 to a new list (new_polygons)
    for poly in shapefile1.geometry:
        if poly not in temp_polygons:
            new_polygons.append(poly)

    # adding polygons from AHN3 that do not intersect with AHN4 to a new list (lost_polygons)
    for poly in shapefile2.geometry:
        if poly not in temp_polygons1:
            lost_polygons.append(poly)

    # converting the lists to geodataframes and joining them with the original shapefiles to add the attributes
    new_polygons = gpd.GeoDataFrame(
        geometry=new_polygons, crs="EPSG:28992")
    new_polygons = gpd.sjoin(
        new_polygons, shapefile1, how="inner", predicate="within")
    new_polygons = new_polygons.drop(columns=["index_right"])

    lost_polygons = gpd.GeoDataFrame(geometry=lost_polygons, crs="EPSG:28992")
    lost_polygons = gpd.sjoin(
        lost_polygons, shapefile2, how="inner", predicate="within")
    lost_polygons = lost_polygons.drop(columns=["index_right"])

    return new_polygons.to_file(new), lost_polygons.to_file(lost)


save_intersecting_polygons("inputs/footprints/ahn4.shp", "inputs/footprints/model.shp",
                           "outputs/facets/new.shp", "outputs/facets/lost.shp")
