import re

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, RelationSummaryDto, Survey


class SrcDistName():
    def __init__(self, product_l3_src: ProductL3Src):
        self.product_l3_src = product_l3_src
        self.s3_src_tif = product_l3_src.product_tif_location
        self.s3_dest_tif = re.sub(
            ".tif", "_OV.tif", product_l3_src.product_tif_location)
        self.s3_hillshade_dest_tif = re.sub(
            ".tif", "_HS.tif", product_l3_src.product_tif_location)
