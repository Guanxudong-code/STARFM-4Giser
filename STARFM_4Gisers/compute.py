import numpy as np
import rasterio
from math import sqrt
from tqdm import tqdm
import central_filter
import time
import os

noise_const = 0.005

Lkpixel = os.path.join("testdata", "L71093084_08420011124_HRF_modtran_surf_ref_agd66.bil")
Mkpixel = os.path.join("testdata", "MOD09GA_A2001329.sur_refl.int")
M0pixel = os.path.join("testdata", "MOD09GA_A2002012.sur_refl.int")

def read_image_with_rasterio(file_path):
    with rasterio.open(file_path) as src:
        data = src.read()  # 读取所有波段
        width = src.width
        height = src.height
        bands = src.count
        return data, width, height, bands  # 返回所有波段的数据，以及图像的宽度、高度和波段数

def computeDiff(first_img, second_img, width, height):
    diff_pixel = np.zeros([height, width], dtype=np.float64)
    for row in range(height):
        for col in range(width):
            diff_pixel[row][col] = abs(float(first_img[row][col]) - float(second_img[row][col]))
    return diff_pixel

def computeDistance(candidate_pixel, central_pixel, width, height):
    dist_pixel = np.zeros([height, width], dtype=np.float64)
    bar = tqdm(total=height)
    print("Computing distance/n")
    for row in range(height - 2):
        for col in range(width - 2):
            threshold_pixel = central_pixel[row][col]
            for i in range(0, 3):
                for l in range(0, 3):
                    pos_y = row + i
                    pos_x = col + l
                    if pos_x == 1 and pos_y == 1:
                        continue
                    elif float(candidate_pixel[pos_y][pos_x]) == central_pixel[row][col]:
                        dist_pixel[pos_y][pos_x] = sqrt((col - pos_x) ** 2 + (row - pos_y) ** 2)
        bar.update(1)
    bar.close()
    return dist_pixel

def computeCombinedWeight(spec_diff, temp_diff, dist_pixel, width, height):
    combined_pixel = np.ones([height, width], dtype=np.float64)
    for row in range(height):
        for col in range(width):
            combined_pixel[row][col] = spec_diff[row][col] * temp_diff[row][col] * dist_pixel[row][col]
    combined_sum = np.sum(combined_pixel)
    weight_pixel = np.ones([height, width], dtype=np.float64)
    print(combined_sum)
    for row in range(height):
        for col in range(width):
            if combined_pixel[row][col] != 0:
                weight_pixel[row][col] = (1 / combined_pixel[row][col]) / (1 / combined_sum)
    return weight_pixel

def refinePixel(candidate_pixel, pixel_diff, width, height):
    pixel_max = pixel_diff.max()
    refined_pixel = np.ones([height, width], dtype=np.float64)
    for row in range(height):
        for col in range(width):
            if candidate_pixel[row][col] > (pixel_max + noise_const):
                refined_pixel[row][col] = 0
            else:
                refined_pixel[row][col] = candidate_pixel[row][col]
    return refined_pixel

def generatePrediction(Lk, Mk, M0, weight, width, height):
    pixel_result = np.empty([height, width], dtype=np.float64)
    print('Computing Prediction pixel')
    bar = tqdm(total=height)
    for row in range(height):
        for col in range(width):
            pixel_result[row][col] = weight[row][col] * (float(M0[row][col]) + float(Lk[row][col]) - float(Mk[row][col]))
        bar.update(1)
    bar.close()
    return pixel_result

def write_image_with_rasterio(output_path, data, reference_path):
    with rasterio.open(reference_path) as src:
        meta = src.meta.copy()  # 复制源图像的元数据

    # 更新元数据以反映新图像的数据类型和图层数
    meta.update(
        dtype=np.float64,  # 使用 float64 类型
        count=data.shape[0]  # 根据数据的波段数更新 count
    )

    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(data)

if __name__ == '__main__':
    start_time = time.time()
    Lkimg, width, height, bands = read_image_with_rasterio(Lkpixel)
    Mkimg, _, _, _ = read_image_with_rasterio(Mkpixel)
    M0img, _, _, _ = read_image_with_rasterio(M0pixel)

    all_band_results = []

    for band in range(bands):
        central_pixel = central_filter.getCentralPixel(Lkimg[band], width, height)
        classified_pixel = central_filter.unsupervisedClassification(Lkimg[band], central_pixel, width, height)
        spec_diff = computeDiff(Lkimg[band], Mkimg[band], width, height)
        temporal_diff = computeDiff(Mkimg[band], M0img[band], width, height)
        dist_pixel = computeDistance(classified_pixel, central_pixel, width, height)

        spec_candidate = spec_diff
        temporal_candidate = temporal_diff

        weight_pixel = computeCombinedWeight(spec_candidate, temporal_candidate, dist_pixel, width, height)
        pixel_result = generatePrediction(Lkimg[band], Mkimg[band], M0img[band], weight_pixel, width, height)

        all_band_results.append(pixel_result)

    # 将所有波段结果堆叠
    all_band_results = np.stack(all_band_results)

    output_path = os.path.join("testdata/temp", "STARFM_PREDICTION.tif")
    write_image_with_rasterio(output_path, all_band_results, Lkpixel)
    end_time = time.time()
    print((f"Execution time: {end_time - start_time} seconds"))
