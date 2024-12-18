import tkinter as tk

from PIL import Image, ImageEnhance, ImageStat, ImageTk

EXPECTED = 128


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
