import numpy as np
import cv2
import sliding_window
import polygonization
from tms2geotiff.tms2geotiff import draw_tile
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator


# Availble sam_kwargs:

# points_per_side: Optional[int] = 32,
# points_per_batch: int = 64,
# pred_iou_thresh: float = 0.88,
# stability_score_thresh: float = 0.95,
# stability_score_offset: float = 1.0,
# box_nms_thresh: float = 0.7,
# crop_n_layers: int = 0,
# crop_nms_thresh: float = 0.7,
# crop_overlap_ratio: float = 512 / 1500,
# crop_n_points_downscale_factor: int = 1,
# point_grids: Optional[List[np.ndarray]] = None,
# min_mask_region_area: int = 0,
# output_mode: str = "binary_mask",

class SamEO:
    def __init__(self, checkpoint="sam_vit_h_4b8939.pth",
                 model_type='vit_h',
                 device='cpu',
                 erosion_kernel=(3, 3),
                 mask_multiplier=255,
                 sam_kwargs=None):
        
        self.checkpoint = checkpoint
        self.model_type = model_type
        self.device = device
        self.sam_kwargs = sam_kwargs
        self.reinit_sam()
        
        self.erosion_kernel = erosion_kernel
        if self.erosion_kernel is not None:
            self.erosion_kernel = np.ones(erosion_kernel, np.uint8)
            
        self.mask_multiplier = mask_multiplier 
            
    def reinit_sam(self):
        self.sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint)
        self.sam.to(device=self.device)
        
        sam_kwargs = self.sam_kwargs if self.sam_kwargs is not None else {}
        self.mask_generator = SamAutomaticMaskGenerator(self.sam, **sam_kwargs)
    
    def __call__(self, image):
        h, w, c = image.shape
        
        resulting_mask = np.zeros((h, w), dtype=np.uint8)
        resulting_borders = np.zeros((h, w), dtype=np.uint8)

        masks = self.mask_generator.generate(image)
        for m in masks:
            mask = (m['segmentation'] > 0).astype(np.uint8)
            resulting_mask += mask

            if self.erosion_kernel is not None:
                mask_erode = cv2.erode(mask, self.erosion_kernel, iterations=1)
                mask_erode = (mask_erode > 0).astype(np.uint8)
                edge_mask = mask - mask_erode
                resulting_borders += edge_mask
        
        resulting_mask = (resulting_mask > 0).astype(np.uint8)
        resulting_borders = (resulting_borders > 0).astype(np.uint8)
        resulting_mask_with_borders = resulting_mask - resulting_borders
        return resulting_mask_with_borders *self.mask_multiplier
    
    def tiff_to_tiff(self, in_path, out_path):
        return sliding_window.tiff_to_tiff(in_path, out_path, self)
    
    def image_to_image(self, image):
        return sliding_window.image_to_image(image, self)

    def download_tms_as_tiff(self, source, pt1, pt2, zoom, dist):
        image = draw_tile(source, pt1[0], pt1[1], pt2[0], pt2[1],
                          zoom, dist)
        return image

    def tiff_to_gpkg(self, tiff_path, gpkg_path, simplify_tolerance=None):
        polygonization.tiff_to_gpkg(tiff_path, gpkg_path, simplify_tolerance)