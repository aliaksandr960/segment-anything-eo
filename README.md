***I suggest you use https://github.com/opengeos/segment-geospatial instead of this repo. It was the first successful attempt to join SAM and EO data, but now there are much better documented and much better maintained options.***

![Automatic segmentation example](title_sameo.png?raw=true "Automatic segmentation example")

# Segment Anything EO tools
Earth observation tools for Meta AI Segment Anything

# Licensing

[Facebook Research Segment Anything](https://github.com/facebookresearch/segment-anything) &mdash; Apache-2.0 license 

[Gumblex tms2geotiff](https://github.com/gumblex/tms2geotiff) &mdash; BSD-2-Clause license

[aeronetlib](https://github.com/Geoalert/aeronetlib) &mdash; MIT licence



Other code &mdash; MIT license

***Segment Anything and tms2geotiff were copied to this repo 9 Apr 2022, you can update them to more recent versions if needed***

## This tools are developed to ease the processing of spatial data (GeoTIFF and TMS) with Meta AI Segment Anything models using sliding window algorithm for big files

### You can:
- download TMS data (including OpenAerialMap and Mapbox Maxar) as GeoTIFF files
- process GeoTIFF files with Meta AI Segment Anything models
- save predicted segments as GeoTIFF raster data and GPKG vector data

and a little bit more

### Usage:
- colab notebook https://colab.research.google.com/drive/1RC1V68tD1O-YissBq9nOvS2PHEjAsFkA?usp=share_link
- jupyter notebook in the repo https://github.com/aliaksandr960/segment-anything-eo/blob/main/basic_usage.ipynb

### Technical details:
- Using a sliding window algorithm to process large images
- In order to separate instances, every instance gets surrounded by 1px width spare space, so it is not the same as how original Segment Anything works

***Segment Anything was released less than a week ago, and these are the first experiments with it. I don't know how paramters affect perfomance &mdash; feel free to change everything.***
