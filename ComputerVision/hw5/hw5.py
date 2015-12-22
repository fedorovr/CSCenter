import numpy as np
import cv2
import os


def hw5(cmp_foo):
    os.chdir(os.path.dirname(__file__) + "/datasets/Corel")
    list_dir = [filename for filename in os.listdir(os.getcwd()) if not filename.endswith(".txt")]
    results = []

    # params for cv2.calcHist()
    channels_hist = [0, 1, 2]    # H, S, V channels
    mask_hist = None
    bins_hist = [12, 12, 12]
    range_hist = [0, 256, 0, 256, 0, 256]

    for i in range(len(list_dir)):
        image = cv2.imread(list_dir[i], cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        hist = cv2.calcHist([image], channels_hist, mask_hist, bins_hist, range_hist)
        hist = cv2.normalize(hist).flatten()

        for j in range(i + 1, len(list_dir)):
            image_second = cv2.imread(list_dir[j], cv2.IMREAD_COLOR)
            image_second = cv2.cvtColor(image_second, cv2.COLOR_BGR2HSV)

            hist_second = cv2.calcHist([image_second],  channels_hist, mask_hist, bins_hist, range_hist)
            hist_second = cv2.normalize(hist_second).flatten()

            results.append((cmp_foo(hist, hist_second), list_dir[i], list_dir[j]))

    with open(cmp_foo.__name__ + ".txt", "w+") as f:
        for res in sorted(results):
            f.write(res[1] + " " + res[2] + " " + str(res[0]) + "\n")


def l2(x, y):
    return np.sum(np.power(np.fabs(np.subtract(x, y)), 2.)) ** 1./2.


def chi_square(x, y):
    return cv2.compareHist(x, y, cv2.cv.CV_COMP_CHISQR)

hw5(l2)
hw5(chi_square)
