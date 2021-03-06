import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
from scipy import ndimage
import matlab.engine
import collections

from sift import *
from surf import *

def rotateImage(img, deg, show = False):

    # shape1 = img.shape[0]
    # shape2 = img.shape[1]
    img2 = ndimage.rotate(img, deg)
    # img2 = cv2.resize(img2, (shape1, shape2))
    if show:
        img_rgb = img2[:, :, ::-1] #rgb (for plt)
        plt.imshow(img_rgb)
        plt.show()
    return img2

def rescaleImage(img, scaleFactor, show = False):

    shape1 = int(img.shape[0] * scaleFactor)
    shape2 = int(img.shape[1] * scaleFactor)
    img2 = cv2.resize(img, (shape2, shape1))
    # print(shape1, shape2, img2.shape)
    if show:
        img_rgb = img2[:, :, ::-1] #rgb (for plt)
        plt.imshow(img_rgb)
        plt.show()

    return img2


img1 = cv2.imread('./data1/obj1.JPG', cv2.IMREAD_COLOR)
kp1, dp1 = siftFeatures(img1)
kp1_s, dp1_s = surfFeatures('./data1/obj1.JPG')
# plotSift(img1, kp1)
# plotSift(img1, kp1_s)
gray = np.ones(img1.shape)*211/255
kp1 = np.array([[kp.pt[0], kp.pt[1]] for kp in kp1])
# kp1_s = np.array([[kp.pt[0], kp.pt[1]] for kp in kp1_s])

### ROTATION

x = []
y = []
y_s = []
for teta in np.arange(0, 360+15, 15):

    kp1_ = kp1.copy()
    kp1_s_ = kp1_s.copy()
    img2 = rotateImage(img1, teta)
    kp2, dp2 = siftFeatures(img2)
    cv2.imwrite('./data1/tmp.jpg', img2)
    kp2_s, dp2_s = surfFeatures('./data1/tmp.jpg')

    kp2 = np.array([[kp.pt[0], kp.pt[1]] for kp in kp2])
    # kp2_s = np.array([[kp.pt[0], kp.pt[1]] for kp in kp2_s])

    kp2 -= np.array([img2.shape[1]/2, img2.shape[0]/2]).reshape((1, -1))
    teta_r = teta*np.pi/180
    R = np.array([[np.cos(teta_r), -np.sin(teta_r)], [np.sin(teta_r), np.cos(teta_r)]])
    kp = R @ kp2.T + np.array([img1.shape[1]/2, img1.shape[0]/2]).T.reshape((-1, 1))

    kp2_s -= np.array([img2.shape[1]/2, img2.shape[0]/2]).reshape((1, -1))
    # teta_r = teta*np.pi/180
    R = np.array([[np.cos(teta_r), -np.sin(teta_r)], [np.sin(teta_r), np.cos(teta_r)]])
    kp_s = R @ kp2_s.T + np.array([img1.shape[1]/2, img1.shape[0]/2]).T.reshape((-1, 1))

    plotSift(img1, kp) # plotting rescaled kps in original pic
    plotSift(img1, kp_s) # plotting rescaled kps in original pic

    matched_idx = []
    not_matched_idx = []

    count = 0 # counting matches
    for i, point1 in enumerate(kp.T):
        best = (-1, distance.euclidean([0, 0], [img1.shape[1], img1.shape[0]])) # (index, distance)
        for j, point2 in enumerate(kp1_):

            if np.abs(point1[0] - point2[0]) <= 2 and np.abs(point1[1] - point2[1]) <= 2:
                # if best[0] != -1:
                    # print('a', end = ' ')
                if distance.euclidean(point1, point2) < best[1]:

                    count += (best[0] == -1)
                    best = (j, distance.euclidean(point1, point2))

        # print("")
        if best[0] != -1:
            np.delete(kp1_, best[0])
            matched_idx.append(i)
        else:
            not_matched_idx.append(i)

    aux1 = kp.T[matched_idx]
    aux2 = kp.T[not_matched_idx]
    plotSift_2kp(gray, aux1, aux2, c = 'orange')

    matched_idx = []
    not_matched_idx = []

    count_s = 0 # counting matches
    for i, point1 in enumerate(kp_s.T):
        best = (-1, distance.euclidean([0, 0], [img1.shape[1], img1.shape[0]])) # (index, distance)
        for j, point2 in enumerate(kp1_s_):

            if np.abs(point1[0] - point2[0]) <= 2 and np.abs(point1[1] - point2[1]) <= 2:
                # if best[0] != -1:
                    # print('a', end = ' ')
                if distance.euclidean(point1, point2) < best[1]:

                    count_s += (best[0] == -1)
                    best = (j, distance.euclidean(point1, point2))

        # print("")
        if best[0] != -1:
            np.delete(kp1_s_, best[0])
            matched_idx.append(i)
        else:
            not_matched_idx.append(i)

    aux1 = kp_s.T[matched_idx]
    aux2 = kp_s.T[not_matched_idx]
    plotSift_2kp(gray, aux1, aux2, c = 'orange')


    y.append(count / len(kp1))
    y_s.append(count_s / len(kp1_s))
    x.append(teta)

    print(teta, count / len(kp1), count_s / len(kp1_s))

plt.figure()
plt.plot(x, y)
plt.plot(x, y_s)
plt.ylim((0.6, 1))
plt.xlim((0, 360))
plt.xlabel('Rotation angle (degrees)')
plt.title('Repeatability against rotation')
plt.legend(['SIFT', 'SURF'])
# plt.show()
# out = gray1
# img_1 = cv2.drawKeypoints(gray1, keypoints_1, out)


### RESCALING

x = []
y = []
y_s = []
for scaleFactor in range(0, 8+1):

    kp1_ = kp1.copy()
    kp1_s_ = kp1_s.copy()
    img2 = rescaleImage(img1, 1.2**scaleFactor)
    kp2, dp2 = siftFeatures(img2)
    cv2.imwrite('./data1/tmp.jpg', img2)
    kp2_s, dp2_s = surfFeatures('./data1/tmp.jpg')

    kp2 = np.array([[kp.pt[0], kp.pt[1]] for kp in kp2])
    # kp2_s = np.array([[kp.pt[0], kp.pt[1]] for kp in kp2_s])

    kp = kp2 / 1.2**scaleFactor
    kp_s = kp2_s / 1.2**scaleFactor
    plotSift(img1, kp) # plotting rescaled kps in original pic
    plotSift(img1, kp_s) # plotting rescaled kps in original pic

    matched_idx = []
    not_matched_idx = []

    count = 0 # counting matches
    for i, point1 in enumerate(kp):
        best = (-1, distance.euclidean([0, 0], [img1.shape[1], img1.shape[0]])) # (index, distance)
        for j, point2 in enumerate(kp1_):

            if np.abs(point1[0] - point2[0]) <= 2 and np.abs(point1[1] - point2[1]) <= 2:
                # if best[0] != -1:
                    # print('a', end = ' ')
                if distance.euclidean(point1, point2) < best[1]:

                    count += (best[0] == -1)
                    best = (j, distance.euclidean(point1, point2))

        # print("")
        if best[0] != -1:
            np.delete(kp1_, best[0])
            matched_idx.append(i)
        else:
            not_matched_idx.append(i)

    aux1 = kp[matched_idx]
    aux2 = kp[not_matched_idx]
    plotSift_2kp(gray, aux1, aux2, c = 'orange')

    matched_idx = []
    not_matched_idx = []

    count_s = 0 # counting matches
    for i, point1 in enumerate(kp_s):
        best = (-1, distance.euclidean([0, 0], [img1.shape[1], img1.shape[0]])) # (index, distance)
        for j, point2 in enumerate(kp1_s_):

            if np.abs(point1[0] - point2[0]) <= 2 and np.abs(point1[1] - point2[1]) <= 2:
                # if best[0] != -1:
                    # print('a', end = ' ')
                if distance.euclidean(point1, point2) < best[1]:

                    count_s += (best[0] == -1)
                    best = (j, distance.euclidean(point1, point2))

        # print("")
        if best[0] != -1:
            np.delete(kp1_s_, best[0])
            matched_idx.append(i)
        else:
            not_matched_idx.append(i)

    aux1 = kp_s[matched_idx]
    aux2 = kp_s[not_matched_idx]
    plotSift_2kp(gray, aux1, aux2, c = 'orange')

    y.append(count / len(kp1))
    y_s.append(count_s / len(kp1_s))
    x.append(scaleFactor)

    print(scaleFactor, count / len(kp1), count_s / len(kp1_s))

plt.figure()
plt.plot(x, y)
plt.plot(x, y_s)
plt.ylim((0.4, 1))
plt.xlim((0, 8))
plt.xlabel('Scaling Factor (1.2**)')
plt.title('Repeatability against scaling')
plt.legend(['SIFT', 'SURF'])
plt.show()
# # out = gray1
# # img_1 = cv2.drawKeypoints(gray1, keypoints_1, out)
