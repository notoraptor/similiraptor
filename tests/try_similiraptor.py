"""
ProfilingStart(Native C++, compare similar sequences)
89.22779352656278 %
94.65143587350101 %
ProfilingEnded(Native C++, compare similar sequences, 01s 275824µs)
ProfilingStart(Native C++, count similar pixels)
342.0 33.3984375 %
586.0 57.2265625 %
ProfilingEnded(Native C++, count similar pixels, 02s 496534µs)

ProfilingStart(Native C++, compare similar sequences)
95.89422487745098 %
98.08708639705883 %
ProfilingEnded(Native C++, compare similar sequences, 01s 085488µs)
ProfilingStart(Native C++, count similar pixels)
738.0 72.0703125 %
984.0 96.09375 %
ProfilingEnded(Native C++, count similar pixels, 02s 473749µs)
"""
import json
import os.path
import sys
import tkinter as tk
from ctypes import pointer

from PIL import ImageOps, ImageTk, ImageStat, Image

from similiraptor.core import (
    fn_compareSimilarSequences,
    fn_countSimilarPixels,
    image_to_native,
)
from tests.experimental_utilities import Display, norb2
from tests.profiling import Profiler
from tests.utilities import ImageUtils
from PIL import Image
from PIL import ImageEnhance
from tqdm import tqdm

W = 32
H = 32
S = (W, H)

PATHS = [
    ["ignored/image1.jpg", "ignored/image2.jpg"],
    ["dataset/images/477689490.jpg", "dataset/images/928741920.jpg"],
    ["dataset/images/1161808543.jpg", "dataset/images/1161808718.jpg"],
    ["dataset/images/1651265780.jpg", "dataset/images/771082710.jpg"],
    ["dataset/images/1635261604.jpg", "dataset/images/7e78d293.jpg"],
    ["dataset/images/627735190.jpg", "dataset/images/661978916.jpg"],
    ["dataset/images/498109366.jpg", "dataset/images/498109376.jpg"],
    ["dataset/images/1476360371.jpg", "dataset/images/1901182218.jpg"],
    ["black.jpg", "white.jpg"],
]


def main():
    path1, path2 = PATHS[-1]
    image1 = ImageUtils.open_rgb_image(path1)
    image2 = ImageUtils.open_rgb_image(path2)
    preparator = norb2
    dimg1 = preparator(image1)
    dimg2 = preparator(image2)
    Display.from_images(image1, dimg1, image2, dimg2)

    th1 = image1.resize(S)
    th2 = image2.resize(S)
    td1 = dimg1.resize(S)
    td2 = dimg2.resize(S)
    s1 = image_to_native(th1)
    s2 = image_to_native(th2)
    t1 = image_to_native(td1)
    t2 = image_to_native(td2)
    ss1 = pointer(s1)
    ss2 = pointer(s2)
    st1 = pointer(t1)
    st2 = pointer(t2)
    max_image_distance = 255 * 3 * W * H
    max_pixel_distance = 3 * 10
    batch = 20_000

    with Profiler("Native C++, compare similar sequences"):
        for _ in range(batch):
            c = fn_compareSimilarSequences(ss1, ss2, W, H, max_image_distance)
            d = fn_compareSimilarSequences(st1, st2, W, H, max_image_distance)
        print(c * 100, "%", file=sys.stderr)
        print(d * 100, "%", file=sys.stderr)

    with Profiler("Native C++, count similar pixels"):
        for _ in range(batch):
            e = fn_countSimilarPixels(ss1, ss2, W, H, max_pixel_distance)
            f = fn_countSimilarPixels(st1, st2, W, H, max_pixel_distance)
        print(e, e * 100 / (W * H), "%", file=sys.stderr)
        print(f, f * 100 / (W * H), "%", file=sys.stderr)


def main2():
    from image_similarity_measures.evaluate import evaluation
    from image_similarity_measures.quality_metrics import metric_functions
    import pprint

    all_metrics = sorted(metric_functions)
    good_metrics = [
        "fsim",  # similarity (> 0.5 ?)
        "rmse",  # distance (< 0.01 ?)
        "uiq",  # similarity (> 0.5 ?)
    ]

    black = Image.new("RGB", (300, 300), (0, 0, 0))
    white = Image.new("RGB", (300, 300), (255, 255, 255))
    path_black = "ignored/black.jpg"
    path_white = "ignored/white.jpg"
    black.save(path_black)
    white.save(path_white)
    res_black = evaluation(
        org_img_path=path_black, pred_img_path=path_black, metrics=all_metrics
    )
    res_white = evaluation(
        org_img_path=path_white, pred_img_path=path_white, metrics=all_metrics
    )
    res_base = evaluation(
        org_img_path=path_black, pred_img_path=path_white, metrics=all_metrics
    )

    path1, path2 = PATHS[0]
    path_b1, path_b2 = PATHS[1]
    res_good = evaluation(org_img_path=path1, pred_img_path=path2, metrics=all_metrics)
    res_bad = evaluation(
        org_img_path=path_b1, pred_img_path=path_b2, metrics=all_metrics
    )

    columns = ["METRIC", "Black", "White", "BvsW", "Good", "Bad"]
    rows = [res_black, res_white, res_base, res_good, res_bad]
    with open("ignored/res.csv", "w") as file:
        print(";".join(columns), file=file)
        for metric in all_metrics:
            print(f"{metric};" + ";".join(str(res[metric]) for res in rows), file=file)


def main3():
    from image_similarity_measures.evaluate import evaluation
    from image_similarity_measures.quality_metrics import metric_functions
    import numpy as np

    good_metrics = [
        "fsim",  # similarity (> 0.5 ?)
        "rmse",  # distance (< 0.01 ?)
        "uiq",  # similarity (> 0.5 ?)
    ]

    with open("dataset_similarities.json") as file:
        similarities = json.load(file)
    with open("ignored/measures.csv", "w") as file:
        print("FILE1;FILE2;" + ";".join(good_metrics), file=file)
        total = sum(len(group) - 1 for group in similarities)
        with tqdm(total=total, desc="measure") as pbar:
            for group in similarities:
                base, *others = group
                base_path = f"dataset/images/{base}"
                assert os.path.isfile(base_path)
                bimg = np.asarray(Image.open(base_path).resize((300, 300)))
                for other in others:
                    other_path = f"dataset/images/{other}"
                    assert os.path.isfile(other_path)
                    oimg = np.asarray(Image.open(other_path).resize((300, 300)))
                    res = {
                        metric: metric_functions[metric](org_img=bimg, pred_img=oimg)
                        for metric in good_metrics
                    }
                    print(
                        f"{base};{other};"
                        + ";".join(str(res[metric]) for metric in good_metrics),
                        file=file,
                    )
                    pbar.update(1)


if __name__ == "__main__":
    main3()
