from joblib import dump, load # to load ML
import numpy # to count labels and store in dict
import operator # to get most predicted label

# SAMPLE ARGUMENTS
beetle1_dict = {"50:F1:4A:CB:FE:EE": {"1": [97686, 92.75, -64.83, -10.33, -6, 79, 148], "2": [97686, 92.75, -64.83, -10.33, -19, 71, 154], "3": [97686, 92.77, -64.84, -10.34, -29, 64, 135], "4": [97686, 92.78, -64.84, -10.34, -34, 59, 127], "5": [97686, 92.79, -64.84, -10.36, -43, 60, 126], "6": [97686, 92.81, -64.84, -10.37, -41, 63, 134], "7": [97686, 92.82, -64.85, -10.38, -23, 51, 145], "8": [97686, 92.83, -64.85, -10.4, -10, 48, 146], "10": [97686, 93.06, -65.01, -10.52, -57, -31, 119], "12": [97686, 93.09, -64.98, -10.58, 20, 61, 171], "14": [97686, 94.14, -65.5, -10.32, 135, 87, 131], "15": [97686, 94.16, -65.56, -10.21, 149, 17, 55], "17": [97686, 94.11, -65.58, -9.92, 118, -41, 58], "18": [97686, 94.08, -65.6, -9.74, 71, -32, 109], "19": [97686, 102.82, -63.03, -9.67, -32, -243, -153], "20": [97686, 103.28, -63.25, -9.69, 152, -149, 280], "21": [97686, 103.72, -63.43, -9.69, -311, -96, 51], "22": [97686, 104.16, -63.5, -9.71, -157, -97, -119], "24": [97686, 105.18, -63.61, -9.55, -19, -137, -122], "25": [97686, 105.45, -63.74, -9.47, -6, -131, -82], "26": [97686, 113.42, -67.64, -7.21, 168, 104, 231], "27": [97686, 115.37, -66.95, -7.62, 198, 58, -218], "29": [97686, 118.25, -65.52, -9.03, 130, -113, -113], "30": [97686, 119.32, -72.76, 0.71, -269, 148, 212], "31": [97686, 119.6, -73.0, 0.33, -65, -81, 318], "32": [97686, 119.93, -73.17, -0.1, 126, -294, -211], "33": [97686, 120.72, -73.19, -1.5, -181, -287, 223], "34": [97686, 120.9, -73.05, -1.99, -62, 194, -294], "35": [97686, 111.14, -72.23, -7.67, 181, -12, -17], "36": [97686, 110.29, -72.51, -8.09, 0, -65, 258], "38": [97686, 110.38, -71.11, -9.12, -29, -2, -159], "40": [97686, 100.83, -75.1, -9.03, -153, 290, 307], "41": [97686, 100.07, -75.86, -8.56, -134, -257, 314], "42": [97686, 99.26, -76.42, -7.99, -143, -29, -149], "43": [97686, 95.47, -77.41, -5.16, 245, 106, -37], "44": [97686, 97.4, -75.67, -8.91, -272, 304, -65], "45": [97686, 97.42, -76.27, -8.71, -285, -324, 225], "46": [97686, 97.43, -76.88, -8.49, 308, 289, -222], "47": [97686, 97.36, -77.51, -8.22, 316, 213, -130], "49": [97686, 96.69, -80.28, -6.96, -208, 64, 213], "50": [97686, 96.37, -81.22, -6.48, -322, -76, -48], "51": [97686, 90.91, -69.11, -7.22, -242, 48, -164], "52": [97686, 90.63, -67.59, -8.17, -242, 52, -80], "54": [97686, 90.22, -63.5, -11.75, 190, -96, 237], "56": [97686, 90.29, -63.46, -12.52, 50, -29, -164], "57": [97686, 90.35, -63.53, -12.68, 298, -282, 292], "58": [97686, 67.14, -56.12, 21.7, 139, 35, 150], "60": [97686, 51.77, -44.48, 38.89, 218, 200, 184], "61": [97686, 48.17, -41.22, 42.87, -112, -224, -18], "62": [97686, 44.39, -37.83, 46.92, -208, -245, 223], "63": [97686, 40.31, -34.18, 51.09, -34, 197, -228], "64": [97686, -95.64, 49.83, -2.99, 305, 216, -88], "65": [97686, -98.98, 49.96, -6.35, -262, 94, 50], "67": [97686, -102.79, 49.44, -9.53, 319, 46, 30], "68": [97686, -104.33, 49.48, -10.43, 198, -32, -255], "69": [97686, -106.04, 49.4, -11.57, -319, -262, 197], "70": [97686, -107.92, 49.18, -12.9, 218, 226, -41], "73": [97686, -153.55, 21.17, 22.59, -324, -72, -186], "74": [97686, -151.43, 21.46, 16.91, -116, 26, -110], "75": [97686, -148.75, 21.68, 14.05, 285, 107, 179], "76": [97686, -145.45, 22.24, 11.37, 187, -187, -41], "77": [97686, -96.59, 52.97, -6.54, -19, -238, 133], "78": [97686, -96.5, 53.07, -6.76, -67, -160, 317], "79": [97686, -96.65, 53.12, -7.17, -36, -232, 207], "80": [97686, -97.18, 53.05, -7.85, 82, 270, 168], "81": [97686, -97.99, 52.94, -8.73, 322, 185, 225], "82": [97686, -98.9, 52.84, -9.69, 200, 140, -80], "83": [97686, -165.67, 26.77, 4.82, -170, -209, -208], "84": [97686, -168.25, 28.57, 8.26, 151, 322, 152], "86": [97686, -169.99, 32.11, 17.1, -120, 1, -192], "87": [97686, -167.85, 31.65, 18.74, -48, 75, -231], "88": [97686, -164.64, 30.55, 19.08, -193, 263, -105], "89": [97686, -161.2, 29.55, 18.21, -33, 157, 255], "92": [97686, -101.17, 52.14, -3.93, 63, -200, -192], "93": [97686, -115.88, 45.52, -17.56, 17, 59, 283], "94": [97686, -120.39, 42.62, -21.07, 234, 230, 124], "95": [97686, -123.89, 40.58, -23.04, 234, -314, 3], "96": [97686, -146.39, 24.22, 20.25, 101, -309, -271], "97": [97686, -144.34, 24.2, 17.55, 85, -253, 86], "98": [97686, -142.94, 24.27, 14.44, 159, 319, -81], "100": [97686, -129.2, 28.04, -0.74, 319, 53, 90], "101": [97686, -126.44, 30.42, -2.99, -137, 23, 319], "103": [97686, -128.61, 37.78, -28.11, 49, 187, 60], "104": [97686, -132.11, 36.33, -25.49, 178, -32, -248], "105": [97686, -133.51, 35.89, -23.32, -241, 76, -316]}}
beetle3_dict = {"78:DB:2F:BF:2C:E2": {"1": [159926, -74.57, -76.17, -12.86, -174, 189, -88], "2": [159926, -74.56, -76.16, -12.86, -184, 204, -18], "3": [159926, -74.56, -76.17, -12.86, -212, 175, 44], "4": [159926, -74.55, -76.18, -12.84, -263, 91, 58], "5": [159926, -74.56, -76.19, -12.82, -292, 39, 47], "6": [159926, -74.55, -76.2, -12.79, -304, 26, 22], "8": [159926, -74.37, -76.56, -12.06, -156, -312, 119], "10": [159926, -66.29, -72.92, -15.24, 99, -108, -231], "12": [159926, -64.5, -72.68, -15.55, 48, 266, -91], "18": [159926, 36.69, -81.45, -8.16, -110, -18, -43], "20": [159926, 66.2, -81.68, -7.95, -18, 320, 75], "21": [159926, 72.55, -81.88, -7.75, 117, 148, -326], "24": [159926, 99.98, -80.96, -9.02, 239, -281, -308], "25": [159926, 101.1, -80.67, -9.28, 301, 264, -214], "26": [159926, 81.67, -84.91, -4.38, -93, -296, -283], "27": [159926, 79.28, -84.78, -4.42, -244, -248, -6], "31": [159926, -77.59, -83.04, -6.17, -247, -269, 319], "33": [159926, -79.09, -83.33, -6.08, 243, -174, 60], "36": [159926, -91.62, -82.19, -1.16, -221, 281, 123], "37": [159926, -91.85, -82.28, -0.84, -207, 257, 135], "44": [159926, -92.52, -82.25, -1.25, 326, 273, 87], "46": [159926, 90.79, 73.03, 2.78, -82, 0, 287], "48": [159926, 82.78, 67.2, 2.69, -52, 183, -283], "50": [159926, 80.37, 67.27, 7.84, -228, -187, 34], "52": [159926, 152.66, 49.66, 32.76, -33, -106, 253], "54": [159926, 145.01, 53.77, 30.39, -301, 228, 321], "56": [159926, 100.22, 55.91, 25.67, -7, 214, 311], "57": [159926, 101.02, 56.19, 25.1, -117, 57, -314], "60": [159926, 111.18, 72.41, 15.72, -87, -100, -175], "61": [159926, 107.48, 74.9, 13.44, 158, -249, -159], "66": [171629, 85.29, 62.16, 17.67, -162, 110, -271], "67": [171629, 87.17, 63.09, 16.44, -31, -223, -144], "68": [171629, 89.01, 64.23, 15.11, -246, 309, -7], "69": [171629, 91.05, 65.05, 14.1, 233, 84, -316], "70": [171629, 93.77, 65.28, 13.93, -167, 273, -276], "71": [171629, 96.85, 65.48, 14.16, 104, -279, 204], "72": [171629, 100.03, 65.43, 14.79, -41, -64, 248], "73": [171629, 103.45, 64.84, 15.99, -45, -322, 20], "74": [171629, 107.03, 63.61, 17.52, 174, 81, -86], "75": [171629, 98.33, 76.49, 11.54, -51, 248, -14], "76": [171629, 94.7, 76.8, 9.74, 272, 149, 5], "77": [171629, 90.85, 76.49, 8.25, 134, -40, 49], "78": [171629, 86.73, 75.88, 7.02, -68, 213, -3], "79": [171629, 82.7, 75.31, 6.12, 270, 189, 190], "80": [171629, 79.51, 74.97, 5.85, -7, -303, 9], "81": [171629, 77.21, 74.64, 6.27, -284, 171, 210], "83": [171629, 116.64, 60.67, 25.53, -22, -32, -297], "85": [171629, 123.29, 55.3, 28.53, 193, 214, 0], "86": [171629, 126.54, 52.89, 29.5, 283, 166, 161], "87": [171629, 129.13, 51.06, 29.9, 213, 161, 56], "88": [171629, 131.28, 49.79, 29.79, -81, -176, 63], "89": [171629, 75.74, 77.37, 10.32, 263, 22, 272], "90": [171629, 77.21, 75.09, 13.4, -16, 308, 191], "91": [171629, 83.02, 72.13, 17.1, -114, 288, -289], "92": [171629, 85.88, 69.62, 19.92, 327, -233, -244], "93": [171629, 77.96, 67.74, 21.74, -269, 85, -206], "94": [171629, 60.78, 65.74, 23.35, -232, -2989, 159], "95": [171629, 62.47, 58.19, 28.99, -94, 231, -99], "97": [171629, 124.52, 54.46, 28.49, 322, 238, 276], "98": [171629, 123.53, 55.69, 28.03, -109, 139, 293], "99": [171629, 122.87, 56.52, 27.74, -224, -297, -87], "100": [171629, 122.17, 57.36, 27.45, -150, -195, -40], "101": [171629, 121.14, 58.5, 27.03, -266, 169, 228], "102": [171629, -5.74, 68.95, 18.24, 56, -23, -322], "103": [171629, 2.22, 66.78, 19.84, 285, -2, -51], "104": [171629, 12.18, 65.2, 20.82, -144, -49, -156], "105": [171629, 25.32, 64.04, 21.36, 67, -37, 171], "106": [171629, 40.15, 63.29, 21.57, 116, -201, -71], "108": [171629, 73.17, 64.74, 19.63, -9, -285, -10], "109": [171629, 79.59, 66.17, 18.48, 133, -263, -49], "110": [171629, 122.03, 56.33, 29.62, 301, 120, -56], "111": [171629, 120.36, 57.96, 29.04, -191, -229, 176], "112": [171629, 118.52, 59.88, 28.15, 253, 145, -52], "113": [171629, 112.97, 66.19, 23.61, 283, -160, -2], "114": [171629, 111.54, 67.7, 22.2, 309, 305, 105], "115": [171629, 110.56, 68.56, 21.34, -32, 24, 143], "117": [171629, 67.75, 59.88, 25.07, -282, -234, 229], "118": [171629, 78.92, 60.23, 24.66, 41, -192, 143], "119": [171629, 86.52, 60.88, 24.11, -318, 311, -204], "123": [171629, 112.3, 58.85, 27.03, 66, 231, -142], "124": [171629, 97.91, 72.14, 15.92, 229, -280, -104], "125": [171629, 91.35, 74.41, 12.65, 222, -140, -48], "126": [171629, 45.77, 75.44, 2.71, 260, 180, 249], "127": [171629, 33.47, 74.48, 3.21, 88, 42, 308], "128": [171629, 20.29, 74.1, 4.57, 39, -167, -5], "129": [171629, 3.08, 74.09, 5.98, -267, 40, 327], "130": [171629, 122.09, 53.06, 31.21, 203, 265, -190], "131": [171629, 127.29, 47.08, 31.77, 149, -111, 37], "132": [171629, 128.05, 46.07, 31.87, 50, 276, -203], "133": [171629, 128.65, 45.29, 32.05, -200, -158, -248], "134": [171629, 129.38, 44.64, 32.46, 14, 150, 282], "135": [171629, 129.94, 44.39, 33.16, -57, -305, 102], "137": [171629, -47.48, 77.13, 10.27, 100, 239, -129], "138": [171629, -52.45, 74.96, 13.2, -311, -293, 71], "139": [171629, -33.28, 65.5, 21.4, 276, 2, -28], "140": [171629, -18.62, 60.44, 24.92, -175, -16, -137], "143": [171629, 34.61, 52.33, 29.1, 311, 173, 147], "144": [171629, 127.44, 47.16, 34.82, -198, 215, -80], "145": [171629, 127.09, 47.46, 34.63, 247, -137, 217], "146": [171629, 127.04, 47.53, 34.49, -320, 91, -108], "147": [171629, 123.05, 52.42, 33.06, -215, -39, 296], "148": [171629, 122.15, 53.54, 32.75, 294, 18, -81], "149": [171629, -57.38, 70.06, 19.06, 35, -141, -21], "150": [171629, -52.64, 67.82, 21.01, -163, -1, -255], "151": [171629, -47.78, 66.08, 22.34, -225, 322, 172], "152": [171629, -43.31, 64.9, 23.14, 115, -147, 62], "153": [171629, -38.47, 64.09, 23.65, -222, -299, -118], "154": [171629, -31.4, 63.52, 23.95, -308, -2, -300], "155": [171629, -19.72, 63.2, 24.01, -118, -39, 4], "156": [171629, -1.02, 63.22, 23.75, -281, 82, 62], "158": [171629, 120.92, 51.49, 34.26, 191, 0, 62], "159": [171629, 120.22, 53.36, 34.21, 98, 198, -321], "160": [171629, 119.55, 54.87, 33.56, 208, -183, 24], "161": [171629, 119.08, 56.42, 32.69, -111, -278, -203], "162": [171629, 118.9, 57.82, 31.76, -161, 201, -206], "164": [171629, 84.09, 65.91, 22.36, -261, -42, 215], "165": [171629, 92.55, 65.99, 22.39, -86, -31, 110], "166": [171629, 97.92, 65.76, 22.69, 299, 210, -295], "167": [171629, 101.9, 65.85, 22.78, 47, -313, -8], "168": [171629, 104.79, 65.82, 23.0, -123, -315, 0], "169": [171629, 106.87, 65.22, 23.66, -81, -149, -147], "170": [171629, 116.76, 61.43, 28.46, 90, 32, 32], "171": [171629, 112.65, 69.71, 20.19, 175, -237, 51], "172": [171629, 110.53, 71.97, 17.93, -10, 145, -309], "173": [171629, 107.66, 74.63, 15.3, 297, 53, -230], "174": [171629, 103.7, 77.55, 12.43, 11, 1, 98], "175": [171629, 98.13, 80.54, 9.44, -59, -197, 17], "176": [171629, 96.05, 65.96, 21.79, 189, 284, 138], "177": [171629, 100.04, 64.92, 22.85, -170, 111, -189], "178": [171629, 107.52, 59.3, 26.93, 79, -67, -3], "179": [171629, 109.35, 56.89, 28.32, -209, -121, 102], "180": [171629, 110.93, 54.75, 29.54, -282, 241, -113], "181": [171629, 112.1, 52.99, 30.39, -297, -177, -288], "183": [171629, 84.92, 81.5, 8.35, 159, 219, 82], "184": [171629, -45.19, 83.29, 5.93, 215, -96, -235], "185": [171629, -61.31, 83.36, 5.48, 181, -115, -161], "186": [171629, -65.96, 83.0, 5.36, 14, 53, 64], "187": [171629, -68.16, 82.39, 5.46, 84, 304, 85]}}
beetle2_dict = {"1C:BA:8C:1D:30:22": {"1": [95396, -90.59, -78.72, 3.89, 15, 71, 226], "2": [95396, -90.59, -78.71, 3.9, 21, 47, 229], "3": [95396, -90.59, -78.71, 3.91, 26, 42, 244], "6": [95396, -90.57, -78.74, 3.93, -2, 138, 291], "13": [95396, -90.23, -78.74, 4.13, 131, 243, 174], "14": [95396, -90.22, -78.7, 4.16, 141, 283, 127], "18": [95396, -90.18, -78.23, 4.35, -306, -217, -62], "19": [95396, -90.19, -77.94, 4.47, -304, -135, -70], "21": [95396, -71.13, -73.87, -13.52, 70, -183, 317], "22": [95396, -70.75, -73.58, -14.06, -105, 31, 162], "23": [95396, -70.41, -73.35, -14.49, -266, 200, -5], "27": [95396, -67.81, -72.0, -16.2, 323, -318, -327], "30": [95396, 46.81, -56.28, -24.39, -247, 67, -20], "31": [95396, 50.4, -55.82, -24.12, 128, -40, 294], "32": [95396, 53.45, -55.28, -23.95, -153, -66, -101], "35": [95396, 61.08, -53.81, -24.16, -81, -99, 174], "36": [95396, 63.23, -53.58, -24.35, 308, 167, -194], "38": [95396, 74.48, -54.09, -27.31, -165, 283, 166], "44": [95396, 35.14, -58.44, -21.76, 66, 76, 121], "50": [95396, -35.92, -66.7, -16.19, 110, -294, -180], "51": [95396, -37.78, -67.03, -16.28, -155, -47, -54], "54": [95396, -44.22, -67.73, -16.13, 35, 149, -16], "55": [95396, -47.04, -68.07, -15.83, 225, 256, -84], "59": [95396, -52.51, -72.21, -9.12, 259, -250, -150], "63": [95396, -44.77, -69.67, -10.93, 4, -101, 70], "67": [95396, -69.45, -72.46, -17.51, -304, -205, 21], "69": [95396, -66.88, -72.01, -17.92, 209, 321, 56], "71": [95396, -64.19, -71.78, -18.05, 73, 319, 95], "72": [95396, -63.36, -71.81, -17.98, -121, -110, -26], "81": [95396, -49.19, -72.72, -4.31, -306, -168, 222], "86": [95396, -57.0, 32.52, 46.47, -55, -197, -24], "91": [95396, -111.0, 51.76, -22.38, 231, -112, -84], "92": [163, -204.36, 99.64, -136953.96, -110, 51, -2], "96": [95396, -108.37, 48.91, -19.87, 197, -57, 143], "97": [95396, -107.67, 48.76, -19.18, -182, -24, 238], "100": [95396, -114.52, 43.57, -3.34, -242, 223, -103], "101": [95396, -112.5, 45.71, 0.54, 314, 28, 305], "104": [8, 29.2, -105.0, -29752953.96, -97, 43, 1], "105": [95396, -94.75, 40.28, 16.54, 68, 94, 278], "106": [95396, -94.35, 38.3, 17.61, -173, -6, -155], "107": [95396, -94.77, 37.47, 18.18, 39, 196, 327], "108": [95396, -95.43, 37.62, 18.43, -280, -46, 78], "109": [95396, -113.99, 38.36, -28.81, -89, -96, -162], "112": [95396, -111.94, 41.64, -29.12, -320, -313, -5], "113": [95396, -111.97, 41.22, -28.89, 190, -67, 63], "114": [95396, -112.2, 40.85, -28.56, -211, -35, -303], "115": [95396, -112.7, 40.79, -28.29, -178, -253, -208], "116": [95396, -113.45, 40.67, -28.21, -189, 166, -229], "117": [95396, -114.6, 39.93, -28.53, 190, 254, 275], "118": [95396, -95.25, 37.44, 17.5, 73, -78, -38], "119": [95396, -96.09, 36.12, 16.32, -260, -212, 208], "120": [95396, -97.01, 34.98, 14.93, -311, -301, 206], "121": [95396, -97.81, 34.07, 13.67, -302, -325, -108], "124": [95396, -99.42, 32.83, 10.44, 23, -38, -232], "125": [95396, -100.07, 32.96, 8.69, -255, -196, 111], "126": [95396, -100.83, 33.16, 6.53, 180, 258, 209], "132": [95396, -123.03, 25.73, -44.84, -45, -140, -64], "133": [95396, -125.02, 22.6, -47.59, 127, -318, 104], "134": [95396, -126.78, 19.44, -49.35, 252, -294, -142], "135": [95396, -128.03, 17.21, -49.21, -184, -255, 294], "136": [95396, -128.7, 17.07, -47.08, 117, 243, 134], "137": [95396, -100.55, 43.16, -3.34, -165, 235, -101], "148": [95396, -115.01, 28.76, -32.23, -123, 144, -294], "151": [95396, -115.89, 32.95, -28.58, 261, 121, -175], "152": [95396, -116.26, 34.87, -26.45, 50, -301, -92]}}
ground_truth = [1,2,3]

# BEETLE ADDRESSES
beetle_1 = "50:F1:4A:CB:FE:EE"
beetle_2 = "1C:BA:8C:1D:30:22"
beetle_3 = "78:DB:2F:BF:2C:E2"

# returns a list of lists, each list containing a row of sensor data
def parse_data(dic_data, beetle):
    # collect hand data
    data = []
    for v in dic_data[beetle].values():
        ypr = []  # yaw, pitch, roll
        for i in range(1, 7):
            ypr.append(v[i])
        data.append(ypr)
    return (data)

def predict_beetle_dance(beetle_data, model):
    pred_arr = model.predict(beetle_data)
    unique, counts = numpy.unique(pred_arr, return_counts=True)
    pred_count = dict(zip(unique, counts))
    prediction = max(pred_count.items(), key=operator.itemgetter(1))[0]
    return prediction

# Program to find most frequent element in a list
def most_frequent_prediction(pred_list):
    return max(set(pred_list), key = pred_list.count)


def find_new_position(ground_truth, b1_move, b2_move, b3_move):
    # ground_truth = [3, 2, 1]
    # p1_movement = 'R'
    # p2_movement = 'S'
    # p3_movement = 'L'

    dic = {1: b1_move, 2: b2_move, 3: b3_move}

    p1_movement = dic[ground_truth[0]]
    p2_movement = dic[ground_truth[1]]
    p3_movement = dic[ground_truth[2]]

    if p1_movement == "R" and p2_movement == "S" and p3_movement == "L":
        # output = [3, 2, 1]
        output = [ground_truth[2], ground_truth[1], ground_truth[0]]
    elif p1_movement == "R" and p2_movement == "L" and p3_movement == "S":
        # output = [2, 1, 3]
        output = [ground_truth[1], ground_truth[0], ground_truth[2]]
    elif p1_movement == "R" and p2_movement == "L" and p3_movement == "L":
        # output = [2, 3, 1]
        output = [ground_truth[1], ground_truth[2], ground_truth[0]]
    elif p1_movement == "S" and p2_movement == "R" and p3_movement == "L":
        # output = [1, 3, 2]
        output = [ground_truth[0], ground_truth[2], ground_truth[1]]
    elif p1_movement == "S" and p2_movement == "L" and p3_movement == "S":
        # output = [2, 1, 3]
        output = [ground_truth[1], ground_truth[0], ground_truth[2]]
    else:
        # output = [1, 2, 3]
        output = ground_truth

    return (output)

# MAIN

# Get beetle data from dictionaries in arguments
beetle1_data = parse_data(beetle_1_dict, beetle_1)
beetle2_data = parse_data(beetle_2_dict, beetle_2)
beetle3_data = parse_data(beetle_3_dict, beetle_3)

# Load MLP NN model
mlp_dance = load('mlp_dance.joblib')

# Predict dance move of each beetle
beetle1_dance = predict_beetle_dance(beetle1_data, mlp_dance)
beetle2_dance = predict_beetle_dance(beetle2_data, mlp_dance)
beetle3_dance = predict_beetle_dance(beetle3_data, mlp_dance)

dance = (most_frequent_prediction(dance_predictions))
#print(dance)

# Load Movement ML
mlp_move = load('mlp_movement.joblib')

# Predict movement direction of each beetle
beetle1_move = predict_beetle(beetle1_data, mlp_move)
beetle2_move = predict_beetle(beetle1_data, mlp_move)
beetle3_move = predict_beetle(beetle1_data, mlp_move)

# Find new position
new_pos = find_new_position(ground_truth, beetle1_move, beetle2_move, beetle3_move)
#print(new_pos)


