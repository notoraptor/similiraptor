import sys

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from PIL import Image
from scipy.spatial import distance

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


def main_ml():
    # 2023/10/02
    # https://towardsdatascience.com/image-similarity-with-deep-learning-c17d83068f59

    model_url = "https://tfhub.dev/tensorflow/efficientnet/lite0/feature-vector/2"

    IMAGE_SHAPE = (224, 224)

    layer = hub.KerasLayer(model_url)
    model = tf.keras.Sequential([layer])

    def extract(image):
        file = image.convert("L").resize(IMAGE_SHAPE)
        # display(file)

        file = np.stack((file,) * 3, axis=-1)

        file = np.array(file) / 255.0

        embedding = model.predict(file[np.newaxis, ...])
        # print(embedding)
        vgg16_feature_np = np.array(embedding)
        flattended_feature = vgg16_feature_np.flatten()

        # print(len(flattended_feature))
        # print(flattended_feature)
        # print('-----------')
        return flattended_feature

    cat1 = extract(Image.open("ignored/image1.jpg"))
    cat2 = extract(Image.open("ignored/image2.jpg"))
    black = extract(Image.new("RGB", IMAGE_SHAPE, (0, 0, 0)))
    white = extract(Image.new("RGB", IMAGE_SHAPE, (255, 255, 255)))

    metric = "cosine"

    dc = distance.cdist([cat1], [cat1], metric)[0]
    print(dc)
    print("the distance between cat1 and cat1 is {}".format(dc))

    dc = distance.cdist([cat1], [cat2], metric)[0]
    print(dc)
    print("the distance between cat1 and cat2 is {}".format(dc))

    dc = distance.cdist([black], [white], metric)[0]
    print(dc)
    print("the distance between black and white is {}".format(dc))
