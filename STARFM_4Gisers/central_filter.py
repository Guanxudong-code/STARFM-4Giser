import numpy as np

def parseInputPixel(filename):
    images = []
    with open(filename) as f:
        temp = []
        temp = f.readlines()
    images = np.array(temp[5:])

    stripped_line = []
    for row in images:
        new_row = row.replace('    ', ' ')
        new_row = new_row.replace('   ', ' ')
        new_row = new_row.replace('  ', ' ')
        new_row = new_row.replace('\n', '')
        new_row = new_row.split(' ')
        if new_row[0] == '':
            new_row.pop(0)
        new_row = np.array(new_row)
        stripped_line.append(new_row)
    processed_img = np.array(stripped_line)
    return processed_img

def unsupervisedClassification(candidate_pixel, center_pixel, width, height):
    classified_pixel = np.zeros([height, width], dtype=float)
    for row in range(height - 2):
        for col in range(width - 2):
            threshold_pixel = center_pixel[row][col]

            min_pixel = 1000000
            max_pixel = 0
            for i in range(0, 3):
                for l in range(0, 3):
                    if int(candidate_pixel[row + i][col + l]) > max_pixel:
                        max_pixel = int(candidate_pixel[row + i][col + l])
                    if int(candidate_pixel[row + i][col + l]) < min_pixel:
                        min_pixel = int(candidate_pixel[row + i][col + l])

            threshold_point = (float(min_pixel) + float(max_pixel)) / 2.0
            for i in range(0, 3):
                for l in range(0, 3):
                    if float(candidate_pixel[row + i][col + l]) < threshold_point:
                        classified_pixel[row + i][col + l] = 0
                    else:
                        classified_pixel[row + i][col + l] = center_pixel[row][col]
    return classified_pixel

def getCentralPixel(images, width, height):
    center_pixel = np.empty([height, width], dtype=float)
    for row in range(height - 2):
        for col in range(width - 2):
            window_sum = 0
            for i in range(0, 3):
                for l in range(0, 3):
                    window_sum += int(images[row + i][col + l])
            new_pixel = float(window_sum) / 9.0
            center_pixel[row][col] = new_pixel
    return np.array(center_pixel)