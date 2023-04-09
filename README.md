# Segment Anything EO
Earth observation tools for Meta AI Segment Anything

## This tool is developed to easy process spatial data (GeoTIFF and TMS) with Meta AI Segment Anything models

### You can:
- download TMS data (including OpenAerialMap and Mapbox Maxar) as GeoTIFF files
- process GeoTIFF files with Meta AI Segment Anything models
- save predicted results as GeoTIFF raster data and GPKG vector data

and little a bit more


### Usage:
- colab notebook https://colab.research.google.com/drive/1RC1V68tD1O-YissBq9nOvS2PHEjAsFkA?usp=share_link
- jupyter notebook in repo https://github.com/aliaksandr960/segment-anything-eo/blob/main/basic_usage.ipynb

### Technical didalis:
- To process large images implemented a sliding window algorithm
- To separate instances, every instance surrounded by 1px width spare space

### Segment Anything was released less, than a week ago and there are first experiments with it. I not know how paramters affect perfomance - feel free to change everything.
