function [dp1,kp1] = surf(img_path)
img1_rgb = imread(img_path);
img1 = rgb2gray(img1_rgb);
kp1 = detectSURFFeatures(img1);
[a, b] = extractFeatures(img1, kp1.selectStrongest(300));
dp1= a;
kp1= b.Location;
