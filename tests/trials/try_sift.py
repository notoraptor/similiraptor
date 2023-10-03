# import required libraries
import cv2
import matplotlib.pyplot as plt


def main():
    # read two input images as grayscale
    img1 = cv2.imread("../ignored/image1.jpg", 0)
    img2 = cv2.imread("../ignored/image2.jpg", 0)

    # Initiate SIFT detector
    sift = cv2.SIFT_create()

    # detect and compute the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # create BFMatcher object
    bf = cv2.BFMatcher()

    # Match descriptors.
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test
    good = []
    for m, n in matches:
        # print(m.distance, n.distance)
        if m.distance < 0.9 * n.distance:
            good.append([m])

    print(len(kp1), len(kp2), len(matches))
    print("Similarity/KP2", len(good) * 100 / len(kp2), "%")

    # Draw first 50 matches.
    out = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)
    plt.imshow(out), plt.show()


if __name__ == "__main__":
    main()
