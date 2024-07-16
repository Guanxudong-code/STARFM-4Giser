## Introduction

This code is a modification based on the original code by Hari Setiawan (https://github.com/harisw/STARFM_prediction). The modifications include adjustments for processing multi-band images, arbitrary sizes and various formats remote sensing images.

# Multi-band Image Processing with `compute.py`

This repository contains a script, `compute.py`, for processing multi-band images. The script reads multiple input images, computes differences and distances between pixels, and generates a prediction image for each band. The results are stacked and saved as a multi-band output image.

## Requirements

Ensure you have the following Python libraries installed:

- `numpy`
- `rasterio`
- `tqdm`

You can install these dependencies using pip:

```bash
pip install numpy rasterio tqdm