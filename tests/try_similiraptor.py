import sys
from ctypes import pointer

from similiraptor.core import fn_compareSimilarSequences, image_to_native
from tests.profiling import Profiler
from tests.dataset_provider import Dataset


import tkinter as tk

from PIL import Image, ImageTk, ImageOps


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


def main():
    assert fn_compareSimilarSequences

    w = 32
    h = 32
    s = (w, h)
    image1 = Image.new("RGB", s, color=(245, 245, 0))
    image2 = Image.new("RGB", s, color=(255, 255, 0))
    Display.from_images(image1, image2)
    s1 = image_to_native(image1)
    s2 = image_to_native(image2)
    ss1 = pointer(s1)
    ss2 = pointer(s2)

    mds = round(3 * 10)
    batch = 20_000
    with Profiler("Native C++"):
        for _ in range(batch):
            c = fn_compareSimilarSequences(ss1, ss2, w, h, mds)
    print(c, file=sys.stderr)


SQRT_3 = 3**0.5


def image_h_dists(image: Image.Image) -> Image.Image:
    w, h = image.size
    data = list(image.getdata())
    avg_gray = sum(sum(p) for p in data) / (3 * len(data))
    output = []
    for i, (r1, g1, b1) in enumerate(data):
        x, y = i % w, i // w
        x_n = min(w - 1, x + 1)
        y_n = min(h - 1, y + 1)
        rh, gh, bh = data[y * w + x_n]
        rv, gv, bv = data[y_n * w + x]
        ch = int((((rh - r1) ** 2 + (gh - g1) ** 2 + (bh - b1) ** 2) ** 0.5) / SQRT_3)
        cv = int((((rv - r1) ** 2 + (gv - g1) ** 2 + (bv - b1) ** 2) ** 0.5) / SQRT_3)
        output.append(
            (255 - ch, 255 - cv, 255 - int(abs(avg_gray - (r1 + g1 + b1) / 3)))
        )
    # assert len(output) == w * h, (len(output), w, h, w * h)
    nimg = Image.new("RGB", (w, h))
    nimg.putdata(output)
    return nimg


EXPECTED = 128


def _clip_color(value):
    return min(max(0, value), 255)


def normalize_brightness(image: Image.Image) -> Image.Image:
    w, h = image.size
    gray = sum(sum(p) / 3 for p in image.getdata()) / (w * h)
    diff = EXPECTED - gray
    print(gray)
    if gray == 0:
        return Image.new("RGB", (w, h), (EXPECTED, EXPECTED, EXPECTED))
    out = Image.eval(image, lambda v: _clip_color(round(v + diff)))
    print("[", sum(sum(p) / 3 for p in out.getdata()) / (w * h), "]")
    return out


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
    return Dataset.new_rgb_image(output, *image.size)


def near(v, l, s=0.3):
    return l * (1 - s) <= v <= l * (1 + s)


def compare_pixel(p1, p2, dgray):
    r1, g1, b1 = p1
    r2, g2, b2 = p2
    drg = (r1 - g1) * (r2 - g2)
    dgb = (g1 - b1) * (g2 - b2)
    # return (drg >= 0 and dgb >= 0 and abs((r1 + g1 + b1 - r2 - g2 - b2) / 3 - dgray) <= 8)
    if (
        drg >= 0
        and dgb >= 0
        and near(abs(r1 - r2), dgray)
        and near(abs(g1 - g2), dgray)
        and near(abs(b1 - b2), dgray)
    ):
        print(p1, p2, dgray, dgray * (1 - 0.3), dgray * (1 + 0.3), file=sys.stderr)
        return True
    return False


def compare_images(img1: Image.Image, img2: Image.Image):
    assert img1.size == img2.size
    w, h = img1.size
    data1 = list(img1.getdata())
    data2 = list(img2.getdata())
    gray1 = sum(sum(p) for p in data1) / (3 * w * h)
    gray2 = sum(sum(p) for p in data2) / (3 * w * h)
    dgray = abs(gray1 - gray2)
    total = 0
    r = 2
    for x in range(0, w):
        for y in range(0, h):
            p = data1[x + y * w]
            total += any(
                compare_pixel(p, data2[i + j * w], dgray)
                for i in range(max(0, x - r), min(x + r + 1, w))
                for j in range(max(0, y - r), min(y + r + 1, h))
            )
    return total


def main_specific():
    w = 32
    h = 32
    s = (w, h)
    path1 = "ignored/image1.jpg"
    path2 = "ignored/image2.jpg"
    path11 = "C:/data/git/similiraptor/tests/dataset/images/477689490.jpg"
    path12 = "C:/data/git/similiraptor/tests/dataset/images/928741920.jpg"
    path21 = "C:/data/git/similiraptor/tests/dataset/images/1161808543.jpg"
    path22 = "C:/data/git/similiraptor/tests/dataset/images/1161808718.jpg"
    path31 = "C:/data/git/similiraptor/tests/dataset/images/1651265780.jpg"
    path32 = "C:/data/git/similiraptor/tests/dataset/images/771082710.jpg"
    image1 = Dataset.open_rgb_image(path1)
    image2 = Dataset.open_rgb_image(path2)
    dimg1 = ImageOps.equalize(image1)
    dimg2 = ImageOps.equalize(image2)
    Display.from_images(image1, dimg1, image2, dimg2)

    th1 = image1.resize(s)
    th2 = image2.resize(s)
    td1 = dimg1.resize(s)
    td2 = dimg2.resize(s)
    s1 = image_to_native(th1)
    s2 = image_to_native(th2)
    t1 = image_to_native(td1)
    t2 = image_to_native(td2)
    ss1 = pointer(s1)
    ss2 = pointer(s2)
    st1 = pointer(t1)
    st2 = pointer(t2)
    mds = 255 * 3 * w * h
    # mds = round(3 * 10)
    batch = 20_000

    # pc = compare_images(th1, th2)
    # pd = compare_images(td1, td2)
    # print("Python:", pc, pc * 100 / (w * h), "%", file=sys.stderr)
    # print("Python:", pd, pd * 100 / (w * h), "%", file=sys.stderr)
    # return

    with Profiler("Native C++"):
        for _ in range(batch):
            c = fn_compareSimilarSequences(ss1, ss2, w, h, mds)
            d = fn_compareSimilarSequences(st1, st2, w, h, mds)
    print(c, c * 100 / (w * h), "%", file=sys.stderr)
    print(d, d * 100 / (w * h), "%", file=sys.stderr)


if __name__ == "__main__":
    main_specific()
