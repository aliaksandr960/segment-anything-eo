import tempfile
import cv2
import numpy as np
import rasterio
from tqdm import tqdm


def chw_to_hwc(block):
    # Grab first 3 channels
    block = block[:3, ...]
    # CHW to HWC
    block = np.transpose(block, (1, 2, 0))
    return block


def hwc_to_hw(block, channel=0):
    
    # Grab first 3 channels
    block = block[..., channel].astype(np.uint8)
    return block

def calculate_sample_grid(raster_h, raster_w, sample_h, sample_w, bound):

    h, w = sample_h, sample_w
    blocks = []
    height = h + 2 * bound
    width = w + 2 * bound

    for y in range(- bound, raster_h, h):
        for x in range(- bound, raster_w, w):

            rigth_x_bound = max(bound,
                                x + width - raster_w)
            bottom_y_bound = max(bound,
                                y + height - raster_h)

            blocks.append({'x': x,
                           'y': y,
                           'height': height,
                           'width': width,
                           'bounds':
                               [[bound, bottom_y_bound], [bound, rigth_x_bound]],
                           })
    return blocks


def read_block(src, x, y, height, width, nodata=0, **kwargs):
    return src.read(window=((y, y + height), (x, x + width)), boundless=True, fill_value=nodata)


def write_block(dst, raster, y, x, height, width, bounds=None):
    if bounds:
        raster = raster[bounds[0][0]:raster.shape[0]-bounds[0][1], bounds[1][0]:raster.shape[1]-bounds[1][1]]
        x += bounds[1][0]
        y += bounds[0][0]
        width = width - bounds[1][1] - bounds[1][0]
        height = height - bounds[0][1] - bounds[0][0]
    dst.write(raster, 1, window=((y, y+height), (x, x+width)))


def tiff_to_tiff(src_fp, dst_fp, func,
                 data_to_rgb=chw_to_hwc,
                 sample_size=(512, 512),
                 sample_resize=None,
                 bound=128):

    with rasterio.open(src_fp) as src:
        profile = src.profile
        
        # Computer blocks
        rh, rw = profile['height'], profile['width']
        sh, sw = sample_size
        bound = bound
        
        resize_hw = sample_resize
        
        sample_grid = calculate_sample_grid(raster_h=rh, raster_w=rw, sample_h=sh, sample_w=sw, bound=bound)
        # set 1 channel uint8 output
        profile['count'] = 1
        profile['dtype'] = 'uint8'

        with rasterio.open(dst_fp, 'w', **profile) as dst:
            for b in tqdm(sample_grid):
                r = read_block(src, **b)
                
                uint8_rgb_in = data_to_rgb(r)
                orig_size = uint8_rgb_in.shape[:2]
                if resize_hw is not None:
                    uint8_rgb_in = cv2.resize(uint8_rgb_in, resize_hw, interpolation=cv2.INTER_LINEAR)
                
                # Do someting
                uin8_out = func(uint8_rgb_in)

                if resize_hw is not None:
                    uin8_out = cv2.resize(uin8_out, orig_size, interpolation=cv2.INTER_NEAREST)
                # Zero chennel, becouse 
                write_block(dst, uin8_out, **b)


def image_to_image(image, func,
                   sample_size=(384, 384),
                   sample_resize=None,
                   bound=128):
    
    with tempfile.NamedTemporaryFile() as src_tmpfile:
        s, b = cv2.imencode('.tif', image)
        src_tmpfile.write(b.tobytes())
        src_fp = src_tmpfile.name
        with tempfile.NamedTemporaryFile() as dst_tmpfile:
            dst_fp = dst_tmpfile.name
            tiff_to_tiff(src_fp, dst_fp, func,
                 data_to_rgb=chw_to_hwc,
                 sample_size=sample_size,
                 sample_resize=sample_resize,
                 bound=bound)
            
            result = cv2.imread(dst_fp)
    return result[..., 0]


def tiff_to_image(src_fp, func,
                  data_to_rgb=chw_to_hwc,
                  sample_size=(512, 512),
                  sample_resize=None,
                  bound=128):
    
    with tempfile.NamedTemporaryFile() as dst_tmpfile:
        dst_fp = dst_tmpfile.name
        tiff_to_tiff(src_fp, dst_fp, func,
                data_to_rgb=data_to_rgb,
                sample_size=sample_size,
                sample_resize=sample_resize,
                bound=bound)
        
        result = cv2.imread(dst_fp)
    return result[..., 0]