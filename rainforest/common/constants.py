#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set of constants regarding MeteoSwiss radars and QPE

"""

import os
import pandas as pd
import numpy as np
import shapefile
from pathlib import Path
import glob
import datetime
from scipy.stats import mode

current_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = Path(current_folder, 'data')


###############
# PHYSIC
###############

KE = 1.25 # value of KE used by MeteoSwiss
LAPSE_RATE = 0.7 # avg lapse rate in the atmosphere
THRESHOLD_SOLID = 2 # Below 2 °C is considerd to be solid precipitation

###############
# STATIONS
###############

METSTATIONS = pd.read_csv(str(Path(data_folder, 'data_stations.csv')), 
                           sep=';', encoding='latin-1')

###############
# RADARS
###############


RADARS = pd.read_csv(str(Path(data_folder, 'data_radars.csv')),
                           sep=';', encoding='latin-1')

ELEVATIONS = [-0.2, 0.4, 1.0, 1.6, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 
               9.5, 11.0, 13.0, 16.0, 20.0, 25.0, 30.0, 35.0, 40.0]

RADIAL_RESOLUTION = {'L':500, 'H': 83.3}

NGATES = {}
NGATES['H'] = [2952,
 2520,
 2952,
 1944,
 2196,
 1944,
 1752,
 1944,
 1680,
 1452,
 1332,
 1200,
 1044,
 900,
 744,
 600,
 492,
 408,
 360,
 324]

NGATES['L'] = [int(n/6) for n in NGATES['H']]

CART_GRID_SIZE = 1000

NSAMPLES = [33.3, 38.9,33.3,37.5,33.3,37.5,27.8,37.5,27.8,33.3,33.3,
            33.3,41.7,41.7,41.7,41.7,41.7,41.7,41.7,41.7 ]
NYQUIST_VEL = [8.3,9.6,8.3,12.4,11,12.4,13.8,12.4,13.8,16.5,16.5,16.5,
               20.6,20.6,20.6,20.6,20.6,20.6,20.6,20.6]


###############
# QPE
###############

VPR_REF_HEIGHTS = {'A':1500,'D':2000,'L':2000,'P':1500,'W':1500}
VPR_REF_RADAR = {'A':'A','P':'A','L':'L','W':'A','D':'D'}

A_QPE = 250
B_QPE = 1.5

MAX_VPR_CORRECTION_DB = 4.77

NBINS_Y = 710
NBINS_X = 640

LOCAL_BIAS =  np.fromfile(str(Path(data_folder, 'lbias_qpegrid.dat')),
                         dtype = np.float32).reshape(NBINS_Y,NBINS_X)
GLOBAL_BIAS = {'A':3.5, 'D': 2., 'L':4., 'P':2., 'W':1.5}
Y_QPE = np.linspace(255, 965, NBINS_Y + 1)
X_QPE = np.linspace(480, -160,  NBINS_X + 1)
Z_QPE = np.load(str(Path(data_folder ,'z_qpegrid.npy')))

try: # when sphinx imports this module it crashes here because it considers numpy as mock module
    Y_QPE_CENTERS = 0.5 * (Y_QPE[0:-1] + Y_QPE[1:])
except:
    Y_QPE_CENTERS = [1]

try: # when sphinx imports this module it crashes here because it considers numpy as mock module
    X_QPE_CENTERS = 0.5 * (X_QPE[0:-1] + X_QPE[1:])
except:
    X_QPE_CENTERS = [1]

MASK_NAN = np.load(str(Path(data_folder, 'mask_nan.npy')))
        
SCALE_RGB = np.array([[0,255,255,255,0.000000],
[1,255,254,254,0.000000],
[2,255,253,253,0.000104],
[3,255,252,252,0.000112],
[4,255,251,251,0.000121],
[5,255,250,250,0.000131],
[6,255,249,249,0.000141],
[7,255,248,248,0.000153],
[8,255,247,247,0.000165],
[9,255,246,246,0.000178],
[10,255,245,245,0.000192],
[11,255,244,244,0.000207],
[12,255,243,243,0.000224],
[13,255,242,242,0.000242],
[14,255,241,241,0.000261],
[15,255,240,240,0.000282],
[16,255,239,239,0.000304],
[17,255,238,238,0.000329],
[18,255,237,237,0.000355],
[19,255,236,236,0.000383],
[20,255,235,235,0.000414],
[21,255,234,234,0.000447],
[22,255,233,233,0.000483],
[23,255,232,232,0.000521],
[24,255,231,231,0.000563],
[25,255,230,230,0.000607],
[26,255,229,229,0.000656],
[27,255,228,228,0.000708],
[28,255,227,227,0.000765],
[29,255,226,226,0.000826],
[30,255,225,225,0.000892],
[31,255,224,224,0.000963],
[32,255,223,223,0.001040],
[33,255,222,222,0.001123],
[34,255,221,221,0.001212],
[35,255,220,220,0.001309],
[36,255,219,219,0.001413],
[37,255,218,218,0.001526],
[38,255,217,217,0.001648],
[39,255,216,216,0.001779],
[40,255,215,215,0.001921],
[41,255,214,214,0.002074],
[42,255,213,213,0.002240],
[43,255,212,212,0.002418],
[44,255,211,211,0.002611],
[45,255,210,210,0.002820],
[46,255,209,209,0.003045],
[47,255,208,208,0.003288],
[48,255,207,207,0.003550],
[49,255,206,206,0.003833],
[50,255,205,205,0.004139],
[51,255,204,204,0.004469],
[52,255,203,203,0.004825],
[53,255,202,202,0.005210],
[54,255,201,201,0.005626],
[55,255,200,200,0.006075],
[56,255,199,199,0.006560],
[57,255,198,198,0.007083],
[58,255,197,197,0.007648],
[59,255,196,196,0.008258],
[60,255,195,195,0.008917],
[61,255,194,194,0.009628],
[62,255,193,193,0.010396],
[63,255,192,192,0.011226],
[64,255,191,191,0.012121],
[65,255,190,190,0.013088],
[66,255,189,189,0.014132],
[67,255,188,188,0.015260],
[68,255,187,187,0.016477],
[69,255,186,186,0.017791],
[70,255,185,185,0.019211],
[71,255,184,184,0.020743],
[72,255,183,183,0.022398],
[73,255,182,182,0.024185],
[74,255,181,181,0.026114],
[75,255,180,180,0.028197],
[76,255,179,179,0.030447],
[77,255,178,178,0.032876],
[78,255,177,177,0.035498],
[79,255,176,176,0.038330],
[80,255,175,175,0.041388],
[81,255,174,174,0.044690],
[82,255,173,173,0.048255],
[83,255,172,172,0.052105],
[84,255,171,171,0.056261],
[85,255,170,170,0.060749],
[86,255,169,169,0.065596],
[87,255,168,168,0.070829],
[88,255,167,167,0.076479],
[89,255,166,166,0.082580],
[90,255,165,165,0.089168],
[91,255,164,164,0.096281],
[92,255,163,163,0.103962],
[93,255,162,162,0.112256],
[94,255,161,161,0.121211],
[95,255,160,160,0.130881],
[96,255,159,159,0.141322],
[97,255,158,158,0.152596],
[98,255,157,157,0.164769],
[99,255,156,156,0.177913],
[100,255,155,155,0.192106],
[101,255,154,154,0.207432],
[102,255,153,153,0.223980],
[103,255,152,152,0.241848],
[104,255,151,151,0.261141],
[105,255,150,150,0.281974],
[106,255,149,149,0.304468],
[107,255,148,148,0.328757],
[108,255,147,147,0.354984],
[109,255,146,146,0.383303],
[110,255,145,145,0.413881],
[111,255,144,144,0.446898],
[112,255,143,143,0.482550],
[113,255,142,142,0.521045],
[114,255,141,141,0.562612],
[115,255,140,140,0.607494],
[116,255,139,139,0.655957],
[117,255,138,138,0.708286],
[118,255,137,137,0.764790],
[119,255,136,136,0.825801],
[120,255,135,135,0.891679],
[121,255,134,134,0.962813],
[122,255,133,133,1.039622],
[123,255,132,132,1.122558],
[124,255,131,131,1.212110],
[125,255,130,130,1.308806],
[126,255,129,129,1.413216],
[127,255,128,128,1.525956],
[128,255,127,127,1.647689],
[129,255,126,126,1.779134],
[130,255,125,125,1.921064],
[131,255,124,124,2.074317],
[132,255,123,123,2.239797],
[133,255,122,122,2.418477],
[134,255,121,121,2.611411],
[135,255,120,120,2.819737],
[136,255,119,119,3.044682],
[137,255,118,118,3.287573],
[138,255,117,117,3.549839],
[139,255,116,116,3.833028],
[140,255,115,115,4.138808],
[141,255,114,114,4.468982],
[142,255,113,113,4.825497],
[143,255,112,112,5.210451],
[144,255,111,111,5.626115],
[145,255,110,110,6.074939],
[146,255,109,109,6.559568],
[147,255,108,108,7.082860],
[148,255,107,107,7.647896],
[149,255,106,106,8.258007],
[150,255,105,105,8.916791],
[151,255,104,104,9.628128],
[152,255,103,103,10.396218],
[153,255,102,102,11.225572],
[154,255,101,101,12.121097],
[155,255,100,100,13.088065],
[156,255,99,99,14.132160],
[157,255,98,98,15.259560],
[158,255,97,97,16.476887],
[159,255,96,96,17.791338],
[160,255,95,95,19.210651],
[161,255,94,94,20.743175],
[162,255,93,93,22.397971],
[163,255,92,92,24.184763],
[164,255,91,91,26.114113],
[165,255,90,90,28.197381],
[166,255,89,89,30.446818],
[167,255,88,88,32.875726],
[168,255,87,87,35.498376],
[169,255,86,86,38.330278],
[170,255,85,85,41.388094],
[171,255,84,84,44.689817],
[172,255,83,83,48.254967],
[173,255,82,82,52.104491],
[174,255,81,81,56.261153],
[175,255,80,80,60.749410],
[176,255,79,79,65.595678],
[177,255,78,78,70.828606],
[178,255,77,77,76.478937],
[179,255,76,76,82.580077],
[180,255,75,75,89.167946],
[181,255,74,74,96.281289],
[182,255,73,73,103.96217],
[183,255,72,72,112.255728],
[184,255,71,71,121.210981],
[185,255,70,70,130.880638],
[186,255,69,69,141.321598],
[187,255,68,68,152.595603],
[188,255,67,67,164.768867],
[189,255,66,66,177.913384],
[190,255,65,65,192.106508],
[191,255,64,64,207.431746],
[192,255,63,63,223.979719],
[193,255,62,62,241.847629],
[194,255,61,61,261.141125],
[195,255,60,60,281.973799],
[196,255,59,59,304.468164],
[197,255,58,58, 328.757250],
[198,255,57,57,354.98377],
[199,255,56,56,383.302783],
[200,255,55,55,413.880943],
[201,255,54,54,446.898157],
[202,255,53,53,482.549681],
[203,255,52,52,521.044914],
[204,255,51,51,562.611534],
[205,255,50,50,607.49411],
[206,255,49,49,655.956794],
[207,255,48,48,708.286032],
[208,255,47,47,764.789335],
[209,255,46,46,825.800785],
[210,255,45,45,891.679424],
[211,255,44,44,962.812889],
[212,255,43,43,1039.62179],
[213,255,42,42,1122.557226],
[214,255,41,41,1212.109784],
[215,255,40,40,1308.806375],
[216,255,39,39,1413.215993],
[217,255,38,38,1525.956075],
[218,255,37,37,1647.688792],
[219,255,36,36,1779.133917],
[220,255,35,35,1921.065102],
[221,255,34,34,2074.317475],
[222,255,33,33,2239.797151],
[223,255,32,32,2418.476217],
[224,255,31,31,2611.411413],
[225,255,30,30,2819.738084],
[226,255,29,29,3044.681598],
[227,255,28,28,3287.572759],
[228,255,27,27,3549.837666],
[229,255,26,26,3833.027705],
[230,255,25,25,4138.809371],
[231,255,24,24,4468.98139],
[232,255,23,23,4825.493097],
[233,255,22,22,5210.449288],
[234,255,21,21,5626.115241],
[235,255,20,20,6074.941151],
[236,255,19,19,6559.572634],
[237,255,18,18,7082.855026],
[238,255,17,17,7647.893647],
[239,255,16,16,8258.008123],
[240,255,15,15,8916.794405],
[241,255,14,14,9628.136288],
[242,255,13,13,396.209982],
[243,255,12,12,1225.572892],
[244,255,11,11,2121.098186],
[245,255,10,10,3088.063782],
[246,255,9,9,4132.171067],
[247,255,8,8,5259.549869],
[248,255,7,7,6476.887099],
[249,255,6,6,7791.338812],
[250,255,5,5,9210.651359],
[251,255,4,4,-99],
[252,255,3,3,-99],
[253,255,2,2,-99],
[254,255,1,1,-99],
[255,0,0,0,-99]])

SCALE_CPC = np.array([0.000000e+00,0.000000e+00,7.177341e-02,1.095694e-01,1.486983e-01,
1.892071e-01,2.311444e-01,2.745606e-01,3.195080e-01,3.660402e-01,
4.142135e-01,4.640857e-01,5.157166e-01,5.691682e-01,6.245048e-01,
6.817929e-01,7.411011e-01,8.025010e-01,8.660660e-01,9.318726e-01,
1.000000e+00,1.070530e+00,1.143547e+00,1.219139e+00,1.297397e+00,
1.378414e+00,1.462289e+00,1.549121e+00,1.639016e+00,1.732080e+00,
1.828427e+00,1.928171e+00,2.031433e+00,2.138336e+00,2.249010e+00,
2.363586e+00,2.482202e+00,2.605002e+00,2.732132e+00,2.863745e+00,
3.000000e+00,3.141060e+00,3.287094e+00,3.438278e+00,3.594793e+00,
3.756828e+00,3.924578e+00,4.098242e+00,4.278032e+00,4.464161e+00,
4.656854e+00,4.856343e+00,5.062866e+00,5.276673e+00,5.498019e+00,
5.727171e+00,5.964405e+00,6.210004e+00,6.464264e+00,6.727490e+00,
7.000000e+00,7.282120e+00,7.574187e+00,7.876555e+00,8.189587e+00,
8.513657e+00,8.849155e+00,9.196485e+00,9.556064e+00,9.928322e+00,
1.031371e+01,1.071269e+01,1.112573e+01,1.155335e+01,1.199604e+01,
1.245434e+01,1.292881e+01,1.342001e+01,1.392853e+01,1.445498e+01,
1.500000e+01,1.556424e+01,1.614837e+01,1.675311e+01,1.737917e+01,
1.802731e+01,1.869831e+01,1.939297e+01,2.011213e+01,2.085664e+01,
2.162742e+01,2.242537e+01,2.325146e+01,2.410669e+01,2.499208e+01,
2.590869e+01,2.685762e+01,2.784002e+01,2.885706e+01,2.990996e+01,
3.100000e+01,3.212848e+01,3.329675e+01,3.450622e+01,3.575835e+01,
3.705463e+01,3.839662e+01,3.978594e+01,4.122425e+01,4.271329e+01,
4.425483e+01,4.585074e+01,4.750293e+01,4.921338e+01,5.098415e+01,
5.281737e+01,5.471524e+01,5.668003e+01,5.871411e+01,6.081992e+01,
6.300000e+01,6.525696e+01,6.759350e+01,7.001244e+01,7.251669e+01,
7.510925e+01,7.779324e+01,8.057188e+01,8.344851e+01,8.642657e+01,
8.950967e+01,9.270148e+01,9.600586e+01,9.942677e+01,1.029683e+02,
1.066347e+02,1.104305e+02,1.143601e+02,1.184282e+02,1.226398e+02,
1.270000e+02,1.315139e+02,1.361870e+02,1.410249e+02,1.460334e+02,
1.512185e+02,1.565865e+02,1.621438e+02,1.678970e+02,1.738531e+02,
1.800193e+02,1.864030e+02,1.930117e+02,1.998535e+02,2.069366e+02,
2.142695e+02,2.218609e+02,2.297201e+02,2.378564e+02,2.462797e+02,
2.550000e+02,2.640278e+02,2.733740e+02,2.830498e+02,2.930668e+02,
3.034370e+02,3.141730e+02,3.252875e+02,3.367940e+02,3.487063e+02,
3.610387e+02,3.738059e+02,3.870234e+02,4.007071e+02,4.148732e+02,
4.295390e+02,4.447219e+02,4.604402e+02,4.767129e+02,4.935594e+02,
5.110000e+02,5.290557e+02,5.477480e+02,5.670995e+02,5.871335e+02,
6.078740e+02,6.293459e+02,6.515750e+02,6.745881e+02,6.984126e+02,
7.230773e+02,7.486119e+02,7.750469e+02,8.024141e+02,8.307465e+02,
8.600779e+02,8.904438e+02,9.218805e+02,9.544258e+02,9.881188e+02,
1.023000e+03,1.059111e+03,1.096496e+03,1.135199e+03,1.175267e+03,
1.216748e+03,1.259692e+03,1.304150e+03,1.350176e+03,1.397825e+03,
1.447155e+03,1.498224e+03,1.551094e+03,1.605828e+03,1.662493e+03,
1.721156e+03,1.781888e+03,1.844761e+03,1.909852e+03,1.977238e+03,
2.047000e+03,2.119223e+03,2.193992e+03,2.271398e+03,2.351534e+03,
2.434496e+03,2.520384e+03,2.609300e+03,2.701352e+03,2.796650e+03,
2.895309e+03,2.997448e+03,3.103188e+03,3.212656e+03,3.325986e+03,
3.443312e+03,3.564775e+03,3.690522e+03,3.820703e+03,3.955475e+03,
4.095000e+03,4.239445e+03,4.388984e+03,4.543796e+03,4.704068e+03,
4.869992e+03,5.041768e+03,5.219600e+03,5.403705e+03,5.594301e+03,
5.79e+03    ,0           ,0           ,0           ,0  ,       0])


SCALE_CPC_OLD = np.array([0,0.000000e+00,3.526497e-02,7.177341e-02,1.095694e-01,1.486983e-01,
1.892071e-01,2.311444e-01,2.745606e-01,3.195080e-01,3.660402e-01,
4.142135e-01,4.640857e-01,5.157166e-01,5.691682e-01,6.245048e-01,
6.817929e-01,7.411011e-01,8.025010e-01,8.660660e-01,9.318726e-01,
1.000000e+00,1.070530e+00,1.143547e+00,1.219139e+00,1.297397e+00,
1.378414e+00,1.462289e+00,1.549121e+00,1.639016e+00,1.732080e+00,
1.828427e+00,1.928171e+00,2.031433e+00,2.138336e+00,2.249010e+00,
2.363586e+00,2.482202e+00,2.605002e+00,2.732132e+00,2.863745e+00,
3.000000e+00,3.141060e+00,3.287094e+00,3.438278e+00,3.594793e+00,
3.756828e+00,3.924578e+00,4.098242e+00,4.278032e+00,4.464161e+00,
4.656854e+00,4.856343e+00,5.062866e+00,5.276673e+00,5.498019e+00,
5.727171e+00,5.964405e+00,6.210004e+00,6.464264e+00,6.727490e+00,
7.000000e+00,7.282120e+00,7.574187e+00,7.876555e+00,8.189587e+00,
8.513657e+00,8.849155e+00,9.196485e+00,9.556064e+00,9.928322e+00,
1.031371e+01,1.071269e+01,1.112573e+01,1.155335e+01,1.199604e+01,
1.245434e+01,1.292881e+01,1.342001e+01,1.392853e+01,1.445498e+01,
1.500000e+01,1.556424e+01,1.614837e+01,1.675311e+01,1.737917e+01,
1.802731e+01,1.869831e+01,1.939297e+01,2.011213e+01,2.085664e+01,
2.162742e+01,2.242537e+01,2.325146e+01,2.410669e+01,2.499208e+01,
2.590869e+01,2.685762e+01,2.784002e+01,2.885706e+01,2.990996e+01,
3.100000e+01,3.212848e+01,3.329675e+01,3.450622e+01,3.575835e+01,
3.705463e+01,3.839662e+01,3.978594e+01,4.122425e+01,4.271329e+01,
4.425483e+01,4.585074e+01,4.750293e+01,4.921338e+01,5.098415e+01,
5.281737e+01,5.471524e+01,5.668003e+01,5.871411e+01,6.081992e+01,
6.300000e+01,6.525696e+01,6.759350e+01,7.001244e+01,7.251669e+01,
7.510925e+01,7.779324e+01,8.057188e+01,8.344851e+01,8.642657e+01,
8.950967e+01,9.270148e+01,9.600586e+01,9.942677e+01,1.029683e+02,
1.066347e+02,1.104305e+02,1.143601e+02,1.184282e+02,1.226398e+02,
1.270000e+02,1.315139e+02,1.361870e+02,1.410249e+02,1.460334e+02,
1.512185e+02,1.565865e+02,1.621438e+02,1.678970e+02,1.738531e+02,
1.800193e+02,1.864030e+02,1.930117e+02,1.998535e+02,2.069366e+02,
2.142695e+02,2.218609e+02,2.297201e+02,2.378564e+02,2.462797e+02,
2.550000e+02,2.640278e+02,2.733740e+02,2.830498e+02,2.930668e+02,
3.034370e+02,3.141730e+02,3.252875e+02,3.367940e+02,3.487063e+02,
3.610387e+02,3.738059e+02,3.870234e+02,4.007071e+02,4.148732e+02,
4.295390e+02,4.447219e+02,4.604402e+02,4.767129e+02,4.935594e+02,
5.110000e+02,5.290557e+02,5.477480e+02,5.670995e+02,5.871335e+02,
6.078740e+02,6.293459e+02,6.515750e+02,6.745881e+02,6.984126e+02,
7.230773e+02,7.486119e+02,7.750469e+02,8.024141e+02,8.307465e+02,
8.600779e+02,8.904438e+02,9.218805e+02,9.544258e+02,9.881188e+02,
1.023000e+03,1.059111e+03,1.096496e+03,1.135199e+03,1.175267e+03,
1.216748e+03,1.259692e+03,1.304150e+03,1.350176e+03,1.397825e+03,
1.447155e+03,1.498224e+03,1.551094e+03,1.605828e+03,1.662493e+03,
1.721156e+03,1.781888e+03,1.844761e+03,1.909852e+03,1.977238e+03,
2.047000e+03,2.119223e+03,2.193992e+03,2.271398e+03,2.351534e+03,
2.434496e+03,2.520384e+03,2.609300e+03,2.701352e+03,2.796650e+03,
2.895309e+03,2.997448e+03,3.103188e+03,3.212656e+03,3.325986e+03,
3.443312e+03,3.564775e+03,3.690522e+03,3.820703e+03,3.955475e+03,
4.095000e+03,4.239445e+03,4.388984e+03,4.543796e+03,4.704068e+03,
4.869992e+03,5.041768e+03,5.219600e+03,5.403705e+03,5.594301e+03,
0           ,0           ,0           ,0                      ,0])

###############
# Graphics
###############

path_shp = Path(current_folder, 'data','swiss_border_shp', 'Border_CH.shp')
BORDER_SHP = shapefile.Reader(str(path_shp))


###############
# Data retrieval
###############
FOLDER_DATABASE = '/store/msrad/radar/radar_database/'
FOLDER_RADAR = '/store/msrad/radar/swiss/data/'
FOLDER_CPCCV = '/store/msrad/radar/cpc_validation/'
COSMO1_START = datetime.datetime(2015,10,1)
FOLDER_RADAR = '/store/msrad/radar/swiss/data/'
FOLDER_COSMO1 = '/store/s83/owm/COSMO-1/'
FOLDER_COSMO1_T = '/store/s83/owm/COSMO-1/ORDERS/MDR/'
FOLDER_COSMO2_T = '/store/msrad/cosmo/cosmo2/data/'
FILTER_COMMAND = '~owm/bin/fxfilter'
CONVERT_COMMAND = '~owm/bin/fxconvert'
OFFSET_CCS4 = [297,-100]
FILES_COSMO1_T = sorted(glob.glob(FOLDER_COSMO1_T + '*.nc'))
TIMES_COSMO1_T = np.array([datetime.datetime.strptime(f[-13:-3],'%Y%m%d%H')
     for f in FILES_COSMO1_T])


###############
# Radar processing
###############

PYART_NAMES_MAPPING = {'reflectivity':'ZH',
                       'differential_reflectivity':'ZDR',
                       'uncorrected_differential_phase':'PSIDP',
                       'spectrum_width':'SW',
                       'velocity':'RVEL',
                       'reflectivity_vv':'ZV',
                       'uncorrected_cross_correlation_ratio':'RHOHV'}

NOISE_100 = 5 # Noise level at 100 km

MIN_RZC_VALID = 0.04  # everything below will be put to zero

def MODE(x):
    if not np.any(np.isfinite(x)):
        return np.nan
    else:
        return mode(x).mode

PYART_NAMES_MAPPING = {'reflectivity':'ZH',
                       'differential_reflectivity':'ZDR',
                       'uncorrected_differential_phase':'PSIDP',
                       'spectrum_width':'SW',
                       'velocity':'RVEL',
                       'reflectivity_vv':'ZV',
                       'uncorrected_cross_correlation_ratio':'RHOHV'}
NUM_RADAR_PER_GAUGE = 2 # 2 5-min radar scans per 10-min gauge accumulation


AVG_BY_VAR = {'ZH': 1 , 'ZH_VISIB' : 1, 'ZV': 1, 'ZV_VISIB' : 1, 'ZDR': 1, 
              'ZV_CORR': 1, 'ZH_CORR':1 , 'ZDR_CORR':1,
              'NH': 1, 'NV': 1, 'TCOUNT':2}


AVG_METHODS = {}
AVG_METHODS[0] = lambda x, axis: np.nanmean(x, axis = axis)
AVG_METHODS[1] = lambda x, axis: 10 * np.log10(np.nanmean(10**(0.1 * x), axis = axis))
AVG_METHODS[2] = lambda x, axis: np.nansum(x, axis = axis)


WARNING_RAM = 512 # megabytes
SLURM_HEADER_R = '''#!/bin/sh
#SBATCH -N 1     # nodes requested
#SBATCH -c 1      # cores requested
#SBATCH -t 06:0:00  # time requested in hour:minute:second
'''


SLURM_HEADER_PY = '''#!/bin/sh
#SBATCH -N 1     # nodes requested
#SBATCH -c 1      # cores requested
#SBATCH --mem-per-cpu 64g # memory in mbytes  
#SBATCH -t 23:59:59  # time requested in hour:minute:second
'''

# Default (not indicated) is np.float32
COL_TYPES = {'TIMESTAMP':np.int32, 
         'RADAR':str,
         'SWEEP':np.dtype(np.int8),
         'NX':np.dtype(np.int8),
         'NY':np.dtype(np.int8),         
         'STATION':str,
         'HYDRO':np.int8,
         'VISIB':np.int8,
         'TCOUNT':np.int8}    


HYDRO_CENTROIDS = {}
HYDRO_CENTROIDS['A'] = [[13.5829, 0.4063, 0.0497, 0.9868, 1330.3],  # AG
         [02.8453, 0.2457, 0.0000, 0.9798, 0653.8],  # CR
         [07.6597, 0.2180, 0.0019, 0.9799, -1426.5],  # LR
         [31.6815, 0.3926, 0.0828, 0.9978, 0535.3],  # RP
         [39.4703, 1.0734, 0.4919, 0.9876, -1036.3],  # RN
         [04.8267, -0.5690, 0.0000, 0.9691, 0869.8],  # VI
         [30.8613, 0.9819, 0.1998, 0.9845, -0066.1],  # WS
         [52.3969, 2.1094, 2.4675, 0.9730, -1550.2],  # MH
         [50.6186, -0.0649, 0.0946, 0.9904, 1179.9]]  # IH/HDG
HYDRO_CENTROIDS['L'] = [[13.8231, 0.2514, 0.0644, 0.9861, 1380.6],  # AG
         [03.0239, 0.1971, 0.0000, 0.9661, 1464.1],  # CR
         [04.9447, 0.1142, 0.0000, 0.9787, -0974.7],  # LR
         [34.2450, 0.5540, 0.1459, 0.9937, 0945.3],  # RP
         [40.9432, 1.0110, 0.5141, 0.9928, -0993.5],  # RN
         [03.5202, -0.3498, 0.0000, 0.9746, 0843.2],  # VI
         [32.5287, 0.9751, 0.2640, 0.9804, -0055.5],  # WS
         [52.6547, 2.7054, 2.5101, 0.9765, -1114.6],  # MH
         [46.4998, 0.1978, 0.6431, 0.9845, 1010.1]]  # IH/HDG
HYDRO_CENTROIDS['D'] = [[12.567, 0.18934, 0.041193, 0.97693, 1328.1],  # AG
         [3.2115, 0.13379, 0.0000, 0.96918, 1406.3],  # CR
         [10.669, 0.18119, 0.0000, 0.97337, -1171.9],  # LR
         [34.941, 0.13301, 0.090056, 0.9979, 898.44],  # RP
         [39.653, 1.1432, 0.35013, 0.98501, -859.38],  # RN
         [2.8874, -0.46363, 0.0000, 0.95653, 1015.6],  # VI
         [34.122, 0.87987, 0.2281, 0.98003, -234.37],  # WS
         [53.134, 2.0888, 2.0055, 0.96927, -1054.7],  # MH
         [46.715, 0.030477, 0.16994, 0.9969, 976.56]]  # IH/HDG
HYDRO_CENTROIDS['P'] =  [[13.9882, 0.2470, 0.0690, 0.9939, 1418.1],  # AG
         [00.9834, 0.4830, 0.0043, 0.9834, 0950.6],  # CR
         [05.3962, 0.2689, 0.0000, 0.9831, -0479.5],  # LR
         [35.3411, 0.1502, 0.0940, 0.9974, 0920.9],  # RP
         [35.0114, 0.9681, 0.1106, 0.9785, -0374.0],  # RN
         [02.5897, -0.3879, 0.0282, 0.9876, 0985.5],  # VI
         [32.2914, 0.7789, 0.1443, 0.9075, -0153.5],  # WS
         [53.2413, 1.8723, 0.3857, 0.9454, -0470.8],  # MH
         [44.7896, 0.0015, 0.1349, 0.9968, 1116.7]]  # IH/HDG
HYDRO_CENTROIDS['W'] = [[16.7650, 0.3754, 0.0442, 0.9866, 1409.0],  # AG
         [01.4418, 0.3786, 0.0000, 0.9490, 1415.8],  # CR
         [16.0987, 0.3238, 0.0000, 0.9871, -0818.7],  # LR
         [36.5465, 0.2041, 0.0731, 0.9952, 0745.4],  # RP
         [43.4011, 0.6658, 0.3241, 0.9894, -0778.5],  # RN
         [00.9077, -0.4793, 0.0000, 0.9502, 1488.6],  # VI
         [36.8091, 0.7266, 0.1284, 0.9924, -0071.1],  # WS
         [53.8402, 0.8922, 0.5306, 0.9890, -1017.6],  # MH
         [45.9686, 0.0845, 0.0963, 0.9940, 0867.4]]  # IH/HDG



