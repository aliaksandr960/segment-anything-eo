#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import argparse
import itertools
import concurrent.futures

import pyproj
import numpy as np
import scipy.ndimage
from PIL import Image
from osgeo import gdal

gdal.UseExceptions()


def num2deg(xtile, ytile, zoom):
    n = 2 ** zoom
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ytile / n))))
    lon = xtile / n * 360 - 180
    return (lat, lon)


def deg2num(lat, lon, zoom):
    lat_r = math.radians(lat)
    n = 2 ** zoom
    xtile = ((lon + 180) / 360 * n)
    ytile = ((1 - math.log(math.tan(lat_r) + 1/math.cos(lat_r)) / math.pi) / 2 * n)
    return (xtile, ytile)


def transform_tile(imgdata, invmatrix, crs,
    corner_x, corner_y, size, zoom, dirname, outname):
    projrev = pyproj.Transformer.from_crs("EPSG:4326", crs)
    newimgdata = np.zeros((imgdata.shape[0], size, size), dtype=float)
    def transform(out_coords):
        # px -> [corner_xy + 0, corner_xy + 1] -> 4326 -> projrev -> img
        tile_x = corner_x + (out_coords[1] / size)
        tile_y = corner_y + (out_coords[0] / size)
        lat, lon = num2deg(tile_x, tile_y, zoom)
        local_xy = projrev.transform(lat, lon)
        img_xy = invmatrix.dot(np.array(local_xy + (1,)))[:2]
        return tuple(reversed(img_xy))

    for b, band in enumerate(imgdata):
        newband = scipy.ndimage.geometric_transform(
            band.astype(float), transform, (size, size), float,
            mode='constant', cval=(255 if b < 3 else 0))
        newimgdata[b] = np.clip(newband, 0, 255)

    newim = Image.fromarray(np.rollaxis(newimgdata, 0, 3).astype('uint8'))
    outpath = os.path.join(dirname, outname.format(x=corner_x, y=corner_y, z=zoom))
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    newim.save(outpath)


def split_tile(imgfile, dirname, outname, zoom, size, proj=None, threads=None):
    # img --aff--> local --proj--> 4326 -> tile xyz (corners)
    # -> 4326 --proj--> 3857 --> tile
    img = gdal.Open(imgfile)
    crs = proj or img.GetProjection() or "EPSG:3857"
    projfwd = pyproj.Transformer.from_crs(crs, "EPSG:4326")
    # x' = a*x + b*y + c
    # y' = d*x + e*y + f
    try:
        tfwfile = os.path.splitext(imgfile)[0] + '.tfw'
        with open(tfwfile, 'r', encoding='utf-8') as f:
            content = tuple(map(float, f.read().strip().split()))
            imgmatrix = np.array((
                (content[0], content[2], content[4]),
                (content[1], content[3], content[5]),
                (0, 0, 1)
            ))
    except Exception:
        geotrans = img.GetGeoTransform()
        # (c, a, b, f, d, e)
        imgmatrix = np.array((
            (geotrans[1], geotrans[2], geotrans[0]),
            (geotrans[4], geotrans[5], geotrans[3]),
            (0, 0, 1)
        ))
    invmatrix = np.linalg.inv(imgmatrix)
    local_corners = imgmatrix.dot(np.array((
        (0, 0, 1),
        (img.RasterXSize, 0, 1),
        (0, img.RasterYSize, 1),
        (img.RasterXSize, img.RasterYSize, 1),
    )).T)[:2].T
    latlon_corners = np.array(tuple(
        projfwd.transform(*row) for row in local_corners))
    min_lat, min_lon = np.amin(latlon_corners, axis=0)
    max_lat, max_lon = np.amax(latlon_corners, axis=0)
    tile_x0, tile_y0 = deg2num(min_lat, min_lon, zoom)
    tile_x1, tile_y1 = deg2num(max_lat, max_lon, zoom)
    if tile_x0 > tile_x1:
        tile_x0, tile_x1 = tile_x1, tile_x0
    if tile_y0 > tile_y1:
        tile_y0, tile_y1 = tile_y1, tile_y0
    corners = tuple(itertools.product(
        range(math.floor(tile_x0), math.ceil(tile_x1)),
        range(math.floor(tile_y0), math.ceil(tile_y1))))
    totalnum = len(corners)
    imgdata = img.ReadAsArray()

    worker_num = threads or os.cpu_count()
    with concurrent.futures.ProcessPoolExecutor(max_workers=worker_num) as exc:
        futures = []
        for corner_x, corner_y in corners:
            futures.append(exc.submit(
                transform_tile, imgdata, invmatrix, crs,
                corner_x, corner_y, size, zoom, dirname, outname))
        for k, future in enumerate(futures):
            future.result()
            print('Image %d/%d' % (k, totalnum))


def main():
    parser = argparse.ArgumentParser(
        description="Split a big GeoTIFF image to TMS tiles.",
        epilog="-z is required")
    parser.add_argument("-z", "--zoom", help="zoom level(s), eg. 15 or 14-17")
    parser.add_argument("-n", "--name", default='{z}_{x}_{y}.png', help="image file name format, default {z}_{x}_{y}.png")
    parser.add_argument("-s", "--size", type=int, default=256,
        help="image size in px, default 256px")
    parser.add_argument("-p", "--proj", help="set projection id")
    parser.add_argument("-t", "--threads", type=int, help="set thread number")
    parser.add_argument("inputfile", help="input GeoTIFF file")
    parser.add_argument("outputdir", help="output directory")
    args = parser.parse_args()
    if not hasattr(args, 'zoom'):
        parser.print_help()
        return 1
    zooms = args.zoom.split('-')
    try:
        if len(zooms) == 1:
            zoomrange = (int(zooms[0]),)
        elif len(zooms) == 2:
            zoomrange = range(int(zooms[0]), int(zooms[1])+1)
        else:
            raise ValueError
    except (TypeError, ValueError):
        parser.print_help()
        return 1

    for zoom in zoomrange:
        split_tile(
            args.inputfile, args.outputdir, args.name,
            zoom, args.size, args.proj, args.threads
        )
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
