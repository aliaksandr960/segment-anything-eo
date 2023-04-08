# tms2geotiff
Download tiles from [Tile Map Server](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames) (online maps) and make a large GeoTIFF image.

Dependencies: GDAL, Pillow, numpy, requests/httpx

    usage: tms2geotiff.py [-h] [-s URL] [-f LAT,LON] [-t LAT,LON] [-z ZOOM] output

    Merge TMS tiles to a big GeoTIFF image.

    positional arguments:
      output                output file

    optional arguments:
      -h, --help            show this help message and exit
      -s URL, --source URL  TMS server url (default is OpenStreetMap:
                            https://tile.openstreetmap.org/{z}/{x}/{y}.png)
      -f LAT,LON, --from LAT,LON
                            one corner
      -t LAT,LON, --to LAT,LON
                            the other corner
      -z ZOOM, --zoom ZOOM  zoom level

    The -f, -t, -z arguments are required

For example,

    python3 tms2geotiff.py -s https://tile.openstreetmap.org/{z}/{x}/{y}.png -f 45.699,127 -t 30,148.492 -z 6 output.tiff

downloads a map of Japan.

If the coordinates are negative, use `--from=-12.34,56.78 --to=-13.45,57.89`


# tmssplit
Split a large GeoTIFF image into tiles for a Tile Map Server.

Dependencies: GDAL, Pillow, numpy, scipy, pyproj

    usage: tmssplit.py [-h] [-z ZOOM] [-n NAME] [-s SIZE] [-p PROJ] [-t THREADS]
                       inputfile outputdir

    Split a big GeoTIFF image to TMS tiles.

    positional arguments:
      inputfile             input GeoTIFF file
      outputdir             output directory

    optional arguments:
      -h, --help            show this help message and exit
      -z ZOOM, --zoom ZOOM  zoom level(s), eg. 15 or 14-17
      -n NAME, --name NAME  image file name format, default {z}_{x}_{y}.png
      -s SIZE, --size SIZE  image size in px, default 256px
      -p PROJ, --proj PROJ  set projection id
      -t THREADS, --threads THREADS
                            set thread number

    -z is required

