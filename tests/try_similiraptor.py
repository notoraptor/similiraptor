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
import sys
import tkinter as tk
from ctypes import pointer

from PIL import ImageOps, ImageTk, ImageStat

from similiraptor.core import (
    fn_compareSimilarSequences,
    fn_countSimilarPixels,
    image_to_native,
)
from tests.profiling import Profiler
from tests.utilities import ImageUtils
from PIL import Image
from PIL import ImageEnhance

W = 32
H = 32
S = (W, H)
EXPECTED = 128


PATHS = [
    ["ignored/image1.jpg", "ignored/image2.jpg"],
    ["dataset/images/477689490.jpg", "dataset/images/928741920.jpg"],
    ["dataset/images/1161808543.jpg", "dataset/images/1161808718.jpg"],
    ["dataset/images/1651265780.jpg", "dataset/images/771082710.jpg"],
    ["dataset/images/1635261604.jpg", "dataset/images/7e78d293.jpg"],
    ["dataset/images/627735190.jpg", "dataset/images/661978916.jpg"],
    ["dataset/images/498109366.jpg", "dataset/images/498109376.jpg"],
    ["dataset/images/1476360371.jpg", "dataset/images/1901182218.jpg"],
]


class Display:
    @staticmethod
    def from_path(path):
        root = tk.Tk()
        img = Image.open(path)
        tk_image = ImageTk.PhotoImage(img)
        label = tk.Label(master=root)
        label["image"] = tk_image
        label.pack(side="left")
        root.mainloop()

    @staticmethod
    def from_images(*images: Image):
        root = tk.Tk()
        tk_images = []
        for img in images:
            tk_image = ImageTk.PhotoImage(img)
            tk_images.append(tk_image)
            tk.Label(master=root, image=tk_image).pack(side="left")
        root.mainloop()


def _clip_color(value):
    return min(max(0, value), 255)


def normalize_brightness(image: Image.Image) -> Image.Image:
    w, h = image.size
    gray = sum(sum(p) for p in image.getdata()) / (3 * w * h)
    diff = EXPECTED - gray
    print(gray)
    if gray == 0:
        return Image.new("RGB", (w, h), (EXPECTED, EXPECTED, EXPECTED))
    out = Image.eval(image, lambda v: _clip_color(round(v + diff)))
    print("[", sum(sum(p) / 3 for p in out.getdata()) / (w * h), "]")
    return out


def norb(image: Image.Image) -> Image.Image:
    from PIL import ImageEnhance

    w, h = image.size
    gray = sum(ImageStat.Stat(image).mean) / 3
    if gray == 0:
        return Image.new("RGB", (w, h), (EXPECTED, EXPECTED, EXPECTED))
    enhancer = ImageEnhance.Brightness(image)
    factor = EXPECTED / gray
    print(factor)
    out = enhancer.enhance(factor)
    ngr = sum(ImageStat.Stat(out).mean) / 3
    print("From", gray, "to", ngr)
    return out


def norb2(image: Image.Image) -> Image.Image:
    w, h = image.size
    gray = sum(ImageStat.Stat(image).mean) / 3
    if round(gray) == 0:
        return Image.new("RGB", (w, h), (EXPECTED, EXPECTED, EXPECTED))
    return ImageEnhance.Brightness(image).enhance(EXPECTED / gray)


def _new_rgb_image(data, width, height):
    image = Image.new("RGB", (width, height))
    image.putdata(data)
    return image


def equalize_image(image: Image.Image) -> Image.Image:
    grays = sorted({int(sum(p) / 3) for p in image.getdata()})
    if len(grays) < 2:
        return Image.new("RGB", image.size, (0, 0, 0))
    best_distance = 255 / (len(grays) - 1)
    old_to_new_gray = {gray: round(i * best_distance) for i, gray in enumerate(grays)}
    output = []
    for pixel in image.getdata():
        old_gray = int(sum(pixel) / 3)
        distance = old_to_new_gray[old_gray] - old_gray
        output.append(
            (
                _clip_color(pixel[0] + distance),
                _clip_color(pixel[1] + distance),
                _clip_color(pixel[2] + distance),
            )
        )
    return _new_rgb_image(output, *image.size)


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


if __name__ == "__main__":
    main()
