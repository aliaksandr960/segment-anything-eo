import shapely
import geopandas as gpd
import rasterio
from rasterio import features


def tiff_to_shapes(tiff_path, simplify_tolerance=None):
    with rasterio.open(tiff_path) as src:
        band=src.read()

        mask = band!= 0
        shapes = features.shapes(band, mask=mask, transform=src.transform)
    result = [shapely.geometry.shape(shape) for shape, _ in shapes]
    if simplify_tolerance is not None:
        result = [shape.simplify(tolerance=simplify_tolerance) for shape in result]
    return result


def tiff_to_gpkg(tiff_path, gpkg_path, simplify_tolerance=None):
    with rasterio.open(tiff_path) as src:
        band=src.read()

        mask = band!= 0
        shapes = features.shapes(band, mask=mask, transform=src.transform)

    fc = [{"geometry": shapely.geometry.shape(shape), "properties": {"value": value}} for shape, value in shapes]
    if simplify_tolerance is not None:
        for i in fc:
            i["geometry"] = i["geometry"].simplify(tolerance=simplify_tolerance)

    gdf = gpd.GeoDataFrame.from_features(fc)
    gdf.set_crs(epsg=src.crs.to_epsg(), inplace=True)
    gdf.to_file(gpkg_path, driver='GPKG')