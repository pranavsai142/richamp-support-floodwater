from datetime import datetime, timedelta
import argparse
import csv
import math

# Yr, Mo, Day, Hr, Min, Sec, Central P(mbar), Background P(mbar), Radius of Max Winds (km)
# 2023 9 1 12 0 0 982 1014 96.1887


# Track merge file
# ["basin","number","date","unknown1", "type", "hours", "latitude", "longitude", "wind", "pressure", "class", "unknown2", "unknown3", "34ktNE", "34ktSE", "34ktSW", "34ktNW", "background", "closure", "radius", "unknown8", "unknown11", "unknown12", "unknown13", "unknown14", "unknown15", "name"]

# AL, 08, 2021081500,   , BEST, 174, 394N,  710W,  65,  986, HU,  34, NEQ,   80,  110,   80,   50, 1012,  240,  25,  80,   0,   L,   0,    ,   0,   0,      HENRI, D, 12, NEQ,  150,  270,  120,   60, genesis-num, 021,
# AL, 08, 2021081500,   , BEST, 174, 394N,  710W,  65,  986, HU,  50, NEQ,   50,   70,    0,    0, 1012,  240,  25,  80,   0,   L,   0,    ,   0,   0,      HENRI, D, 12, NEQ,  150,  270,  120,   60, genesis-num, 021,
# AL, 08, 2021081500,   , BEST, 174, 394N,  710W,  65,  986, HU,  64, NEQ,    0,   30,    0,    0, 1012,  240,  25,  80,   0,   L,   0,    ,   0,   0,      HENRI, D, 12, NEQ,  150,  270,  120,   60, genesis-num, 021,
# AL, 08, 2021081500,   , BEST, 180, 407N,  713W,  55,  986, TS,  34, NEQ,   80,   90,   60,   50, 1012,  240,  25,  65,   0,   L,   0,    ,   0,   0,      HENRI, D, 12, NEQ,  150,  270,   90,   90, genesis-num, 021,
# AL, 08, 2021081500,   , BEST, 180, 407N,  713W,  55,  986, TS,  50, NEQ,   40,   50,    0,    0, 1012,  240,  25,  65,   0,   L,   0,    ,   0,   0,      HENRI, D, 12, NEQ,  150,  270,   90,   90, genesis-num, 021,
# AL, 08, 2021081500, 20, BEST, 183, 412N,  716W,  55,  987, TS,  34, NEQ,   50,   60,   40,   40, 1012,  240,  25,   0,   0,   L,   0,    ,   0,   0,      HENRI,  ,  0,    ,    0,    0,    0,    0, genesis-num, 021,
# AL, 08, 2021081500, 20, BEST, 183, 412N,  716W,  55,  987, TS,  50, NEQ,   40,   50,    0,    0, 1012,  240,  25,   0,   0,   L,   0,    ,   0,   0,      HENRI,  ,  0,    ,    0,    0,    0,    0, genesis-num, 021,
# AL, 08, 2021081500, 15, BEST, 184, 413N,  718W,  55,  988, TS,  34, NEQ,   50,   60,   40,   40, 1012,  240,  25,   0,   0,   L,   0,    ,   0,   0,      HENRI,  ,  0,    ,    0,    0,    0,    0, genesis-num, 021,
# AL, 08, 2021081500, 15, BEST, 184, 413N,  718W,  55,  988, TS,  50, NEQ,   40,   50,    0,    0, 1012,  240,  25,   0,   0,   L,   0,    ,   0,   0,      HENRI,  ,  0,    ,    0,    0,    0,    0, genesis-num, 021,
# AL, 08, 2021081500,   , BEST, 186, 415N,  720W,  40,  991, TS,  34, NEQ,   30,   40,   30,   20, 1012,  240,  25,  50,   0,   L,   0,    ,   0,   0,      HENRI, D,  0,    ,    0,    0,    0,    0, genesis-num, 021,
# AL, 08, 2021081500, 03, OFCL, 189, 416N,  724W,  35,  997, TS,  34, NEQ,    0,   30,    0,    0,    0,    0,   0,  50,   0,    ,   0, SRS, 290,   6,           ,  , 12, NEQ,    0,   90,   90,    0,
# AL, 08, 2021081500, 03, OFCL, 198, 420N,  735W,  30,    0, TD,  34, NEQ,    0,    0,    0,    0,    0,    0,   0,  40,   0,    ,   0, SRS, 295,   6,
# AL, 08, 2021081500, 03, OFCL, 210, 426N,  730W,  25,    0, TD,  34, NEQ,    0,    0,    0,    0,    0,    0,   0,  35,   0,    ,   0, SRS,  30,   4,
# AL, 08, 2021081500, 03, OFCL, 222, 430N,  704W,  25,    0, LO,  34, NEQ,    0,    0,    0,    0,    0,    0,   0,  35,   0,    ,   0, SRS,  75,  10,
# AL, 08, 2021081500, 03, OFCL, 234, 436N,  665W,  25,    0, LO,  34, NEQ,    0,    0,    0,    0,    0,    0,   0,  35,   0,    ,   0, SRS,  75,  15,

# Sample input data
# AL, 13, 2023090112,   , BEST,  96, 122N,  396W,  30, 1008, TD,   0,    ,    0,    0,    0,    0, 1012,  210, 120,  40,   0,   L,   0,    ,   0,   0,   THIRTEEN, M,  0,    ,    0,    0,    0,    0, genesis-num, 027, TRANSITIONED, alB52023 to al132023, DISSIPATED, al132023 to al952023, TRANSITIONED, alC52023 to al132023,
# AL, 13, 2023090112,   , BEST, 102, 129N,  411W,  35, 1006, TS,  34, NEQ,   60,    0,    0,   60, 1012,  210,  60,  45,   0,   L,   0,    ,   0,   0,        LEE, M, 12, NEQ,   60,    0,    0,    0, genesis-num, 027,

# Real sameple input
# AL, 13, 2023091400,   , BEST,   0, 276N,  677W,  90,  951,   ,  34, NEQ,  230,  230,  170,  180, 1013,     ,  50,     ,    ,    ,    ,    ,  0,   8,       LEE  ,   1,    3, 1, 1, 1, 1,     50.9,   48.6,   33.8,   38.9,    1.1744,   1.3343,   1.3270,   1.2797,   1.2961,  93.8157,  93.8157,  93.8157,  93.8157
# AL, 13, 2023091400,   , BEST,   0, 276N,  677W,  90,  951,   ,  50, NEQ,  140,  130,  100,  120, 1013,     ,  50,     ,    ,    ,    ,    ,  0,   8,       LEE  ,   1,    3, 1, 1, 1, 1,     42.2,   36.0,   29.2,   39.7,    1.1744,   1.3064,   1.2869,   1.2653,   1.2984,  93.8157,  93.8157,  93.8157,  93.8157
# AL, 13, 2023091400,   , BEST,   0, 276N,  677W,  90,  951,   ,  64, NEQ,  100,  100,   80,   80, 1013,     ,  50,     ,    ,    ,    ,    ,  0,   8,       LEE  ,   1,    3, 1, 1, 1, 1,     41.9,   39.1,   35.1,   38.4,    1.1744,   1.3056,   1.2967,   1.2840,   1.2945,  93.8157,  93.8157,  93.8157,  93.8157
# AL, 13, 2023091403,   , OFCL,   3, 280N,  677W,  90,  953,   ,  34, NEQ,  230,  230,  170,  180, 1013,     ,   0,     ,    ,    ,    ,    ,  0,   8,      LEE   ,   2,    3, 1, 1, 1, 1,     54.0,   51.7,   35.9,   41.6,    1.2136,   1.3911,   1.3833,   1.3306,   1.3495,  93.8157,  93.8157,  93.8157,  93.8157
# AL, 13, 2023091403,   , OFCL,   3, 280N,  677W,  90,  953,   ,  50, NEQ,  140,  130,  100,  120, 1013,     ,   0,     ,    ,    ,    ,    ,  0,   8,      LEE   ,   2,    3, 1, 1, 1, 1,     44.0,   37.8,   30.5,   41.3,    1.2136,   1.3578,   1.3369,   1.3129,   1.3485,  93.8157,  93.8157,  93.8157,  93.8157
# AL, 13, 2023091403,   , OFCL,   3, 280N,  677W,  90,  953,   ,  64, NEQ,  100,  100,   80,   80, 1013,     ,   0,     ,    ,    ,    ,    ,  0,   8,      LEE   ,   2,    3, 1, 1, 1, 1,     43.2,   40.4,   36.1,   39.4,    1.2136,   1.3550,   1.3458,   1.3315,   1.3423,  93.8157,  93.8157,  93.8157,  93.8157
# AL, 13, 2023091412,   , OFCL,  12, 299N,  679W,  90,  953,   ,  34, NEQ,  240,  240,  170,  190, 1013,     ,   0,     ,    ,    ,    ,    ,355,  13,      LEE   ,   3,    3, 1, 1, 1, 1,     57.0,   54.3,   36.8,   46.5,    1.1599,   1.3551,   1.3459,   1.2850,   1.3186,  91.7172,  91.7172,  91.7172,  91.7172
# AL, 13, 2023091412,   , OFCL,  12, 299N,  679W,  90,  953,   ,  50, NEQ,  140,  130,  100,  120, 1013,     ,   0,     ,    ,    ,    ,    ,355,  13,      LEE   ,   3,    3, 1, 1, 1, 1,     43.4,   36.9,   31.5,   43.3,    1.1599,   1.3079,   1.2855,   1.2669,   1.3076,  91.7172,  91.7172,  91.7172,  91.7172
# AL, 13, 2023091412,   , OFCL,  12, 299N,  679W,  90,  953,   ,  64, NEQ,  100,  100,   80,   80, 1013,     ,   0,     ,    ,    ,    ,    ,355,  13,      LEE   ,   3,    3, 1, 1, 1, 1,     42.9,   39.9,   38.3,   42.6,    1.1599,   1.3060,   1.2956,   1.2902,   1.3052,  91.7172,  91.7172,  91.7172,  91.7172
# AL, 13, 2023091500,   , OFCL,  24, 319N,  686W,  85,  956,   ,  34, NEQ,  250,  250,  170,  190, 1013,     ,   0,     ,    ,    ,    ,    ,343,  10,      LEE   ,   4,    3, 1, 1, 1, 1,     63.4,   62.2,   39.3,   48.0,    1.1019,   1.3342,   1.3296,   1.2446,   1.2766,  87.1305,  87.1305,  87.1305,  87.1305
# AL, 13, 2023091500,   , OFCL,  24, 319N,  686W,  85,  956,   ,  50, NEQ,  140,  130,  100,  120, 1013,     ,   0,     ,    ,    ,    ,    ,343,  10,      LEE   ,   4,    3, 1, 1, 1, 1,     45.7,   40.0,   34.5,   45.2,    1.1019,   1.2681,   1.2471,   1.2266,   1.2665,  87.1305,  87.1305,  87.1305,  87.1305
# AL, 13, 2023091500,   , OFCL,  24, 319N,  686W,  85,  956,   ,  64, NEQ,   90,   90,   70,   70, 1013,     ,   0,     ,    ,    ,    ,    ,343,  10,      LEE   ,   4,    3, 1, 1, 1, 1,     40.2,   38.9,   37.4,   39.3,    1.1019,   1.2477,   1.2431,   1.2376,   1.2445,  87.1305,  87.1305,  87.1305,  87.1305
# AL, 13, 2023091512,   , OFCL,  36, 350N,  680W,  80,  959,   ,  34, NEQ,  250,  250,  180,  230, 1013,     ,   0,     ,    ,    ,    ,    ,  9,  16,      LEE   ,   5,    3, 1, 1, 1, 1,     68.9,   61.3,   42.8,   74.5,    0.9666,   1.2345,   1.2047,   1.1312,   1.2570,  79.4315,  79.4315,  79.4315,  79.4315
# AL, 13, 2023091512,   , OFCL,  36, 350N,  680W,  80,  959,   ,  50, NEQ,  140,  130,  100,  120, 1013,     ,   0,     ,    ,    ,    ,    ,  9,  16,      LEE   ,   5,    3, 1, 1, 1, 1,     51.9,   40.1,   35.8,   57.1,    0.9666,   1.1675,   1.1206,   1.1039,   1.1879,  79.4315,  79.4315,  79.4315,  79.4315
# AL, 13, 2023091512,   , OFCL,  36, 350N,  680W,  80,  959,   ,  64, NEQ,   80,   80,   60,   60, 1013,     ,   0,     ,    ,    ,    ,    ,  9,  16,      LEE   ,   5,    3, 1, 1, 1, 1,     43.5,   35.1,   35.6,   60.0,    0.9666,   1.1342,   1.1012,   1.1030,   1.2014,  79.4315,  79.4315,  79.4315,  79.5044
# AL, 13, 2023091600,   , OFCL,  48, 379N,  676W,  75,  962,   ,  34, NEQ,  250,  250,  210,  230, 1013,     ,   0,     ,    ,    ,    ,    ,  6,  15,      LEE   ,   6,    3, 1, 1, 1, 1,     74.4,   66.5,   60.6,   82.0,    0.8956,   1.2066,   1.1731,   1.1478,   1.2384,  74.3036,  74.3036,  74.3036,  74.3036
# AL, 13, 2023091600,   , OFCL,  48, 379N,  676W,  75,  962,   ,  50, NEQ,  150,  130,  100,  130, 1013,     ,   0,     ,    ,    ,    ,    ,  6,  15,      LEE   ,   6,    3, 1, 1, 1, 1,     63.3,   44.3,   41.0,   72.7,    0.8956,   1.1593,   1.0789,   1.0648,   1.1991,  74.3036,  74.3036,  74.3036,  74.3036
# AL, 13, 2023091600,   , OFCL,  48, 379N,  676W,  75,  962,   ,  64, NEQ,   70,   70,   50,   50, 1013,     ,   0,     ,    ,    ,    ,    ,  6,  15,      LEE   ,   6,    3, 1, 1, 1, 1,     44.2,   34.6,   39.3,   50.0,    0.8956,   1.0783,   1.0376,   1.0577,   1.2270,  74.3036,  74.3036,  74.3036,  78.9018
# AL, 13, 2023091612,   , OFCL,  60, 409N,  681W,  65,  968,   ,  34, NEQ,  270,  250,  200,  250, 1013,     ,   0,     ,    ,    ,    ,    ,353,  15,      LEE   ,   7,    2, 1, 1, 1, 1,     95.0,   76.7,   72.1,  115.7,    0.7293,   1.1494,   1.0684,   1.0483,   1.2390,  62.9853,  62.9853,  62.9853,  62.9853
# AL, 13, 2023091612,   , OFCL,  60, 409N,  681W,  65,  968,   ,  50, NEQ,  150,  130,  110,  140, 1013,     ,   0,     ,    ,    ,    ,    ,353,  15,      LEE   ,   7,    2, 1, 1, 1, 1,     78.1,   56.8,   75.9,  139.6,    0.7293,   1.0749,   0.9797,   1.0650,   1.3130,  62.9853,  62.9853,  62.9853,  62.0339
# AL, 13, 2023091700,   , OFCL,  72, 442N,  680W,  60,  971,   ,  34, NEQ,  210,  240,  180,  160, 1013,     ,   0,     ,    ,    ,    ,    ,  1,  17,      LEE   ,   8,    2, 1, 1, 1, 1,     73.2,   78.2,   70.1,   77.3,    0.6379,   0.9806,   1.0037,   0.9662,   0.9994,  56.9072,  56.9072,  56.9072,  56.9072
# AL, 13, 2023091700,   , OFCL,  72, 442N,  680W,  60,  971,   ,  50, NEQ,  130,  130,  100,  130, 1013,     ,   0,     ,    ,    ,    ,    ,  1,  17,      LEE   ,   8,    2, 1, 1, 1, 1,     85.0,   66.6,   99.7,  130.0,    0.6379,   1.0347,   0.9497,   1.1992,   1.4388,  56.9072,  56.9072,  60.3430,  63.4082
# AL, 13, 2023091800,   , OFCL,  96, 512N,  627W,  40,  974,   ,  34, NEQ,    0,    0,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 27,  20,      LEE   ,   9,    1, 1, 1, 1, 1,     73.2,   78.2,   70.1,   77.3,    0.2389,   0.4316,   0.4316,   0.4316,   0.4316,  33.5586,  33.5586,  33.5586,  33.5586
# AL, 13, 2023091900,   , OFCL, 120, 571N,  513W,  35,  977,   ,  34, NEQ,    0,    0,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 49,  22,      LEE   ,  10,    1, 1, 1, 1, 1,     73.2,   78.2,   70.1,   77.3,    0.1690,   0.3255,   0.3255,   0.3255,   0.3255,  27.1172,  27.1172,  27.1172,  27.1172

# Fort.22 sample input from josh
# ["basin","number","date","unknown1", "type", "hours", "latitude", "longitude", "wind", "pressure", "class", "unknown2", "unknown3", "34ktNE", "34ktSE", "34ktSW", "34ktNW", "background", "closure", "radius", "unknown8", "unknown11", "unknown12", "unknown13", "unknown14", "unknown15", "name"]
# AL, 08, 2021082106,   , BEST,   0, 325N,  734W,  60,  993,   ,  34, NEQ,   90,  100,   50,   7a0, 1013,     ,  30,     ,    ,    ,    ,    , 16,  12,     HENRI  ,   1,    2, 1, 1, 1, 1,     43.6,   44.2,   21.7,   39.2,    1.5911,   1.9328,   1.9381,   1.7605,   1.8986,  58.4902,  58.4902,  58.4902,  58.4902
# AL, 08, 2021082106,   , BEST,   0, 325N,  734W,  60,  993,   ,  50, NEQ,   50,   50,    0,    0, 1013,     ,  30,     ,    ,    ,    ,    , 16,  12,     HENRI  ,   1,    2, 1, 1, 0, 0,     38.2,   31.0,    0.0,    0.0,    1.5911,   1.8900,   1.8337,   1.7419,   1.7012,  58.4902,  58.4902,  58.4902,  58.4902
# AL, 08, 2021082109,   , OFCL,   3, 331N,  732W,  60,  996,   ,  34, NEQ,   90,  100,   50,   70, 1013,     ,   0,     ,    ,    ,    ,    , 16,  12,    HENRI   ,   2,    2, 1, 1, 1, 1,     48.9,   50.5,   24.8,   42.9,    1.8719,   2.3283,   2.3431,   2.1023,   2.2722,  58.4902,  58.4902,  58.4902,  58.4902
# AL, 08, 2021082109,   , OFCL,   3, 331N,  732W,  60,  996,   ,  50, NEQ,   50,   50,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 16,  12,    HENRI   ,   2,    2, 1, 1, 0, 0,     39.7,   33.4,    0.0,    0.0,    1.8719,   2.2420,   2.1824,   2.0586,   2.0149,  58.4902,  58.4902,  58.4902,  58.4902
# AL, 08, 2021082118,   , OFCL,  12, 356N,  723W,  70,  978,   ,  34, NEQ,  100,  110,   90,   50, 1013,     ,   0,     ,    ,    ,    ,    , 17,  17,    HENRI   ,   3,    3, 1, 1, 1, 1,     31.7,   30.8,   28.1,   16.9,    1.2178,   1.3973,   1.3920,   1.3766,   1.3126,  67.6926,  67.6926,  67.6926,  67.6926
# AL, 08, 2021082118,   , OFCL,  12, 356N,  723W,  70,  978,   ,  50, NEQ,   50,   50,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 17,  17,    HENRI   ,   3,    3, 1, 1, 0, 0,     24.9,   19.7,    0.0,    0.0,    1.2178,   1.3582,   1.3285,   1.2839,   1.3235,  67.6926,  67.6926,  67.6926,  67.6926
# AL, 08, 2021082118,   , OFCL,  12, 356N,  723W,  70,  978,   ,  64, NEQ,   20,   25,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 17,  17,    HENRI   ,   3,    3, 1, 1, 0, 0,     20.0,   15.7,    0.0,    0.0,    1.2178,   1.3146,   1.3055,   1.2529,   1.2529,  67.2734,  67.6926,  67.6926,  67.6926
# AL, 08, 2021082206,   , OFCL,  24, 388N,  720W,  70,  978,   ,  34, NEQ,  110,  130,   90,   50, 1013,     ,   0,     ,    ,    ,    ,    ,  4,  16,    HENRI   ,   4,    3, 1, 1, 1, 1,     36.2,   41.5,   30.3,   16.7,    1.2358,   1.4585,   1.4919,   1.4217,   1.3377,  68.1904,  68.1904,  68.1904,  68.1904
# AL, 08, 2021082206,   , OFCL,  24, 388N,  720W,  70,  978,   ,  50, NEQ,   50,   60,   20,   20, 1013,     ,   0,     ,    ,    ,    ,    ,  4,  16,    HENRI   ,   4,    3, 1, 1, 1, 1,     23.8,   25.4,   10.0,   13.7,    1.2358,   1.3811,   1.3914,   1.2961,   1.3190,  68.1904,  68.1904,  68.1904,  68.1904
# AL, 08, 2021082206,   , OFCL,  24, 388N,  720W,  70,  978,   ,  64, NEQ,   20,   25,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    ,  4,  16,    HENRI   ,   4,    3, 1, 1, 0, 0,     16.0,   16.0,    0.0,    0.0,    1.2358,   1.3333,   1.3331,   1.2744,   1.2744,  68.1904,  68.1904,  68.1904,  68.1904
# AL, 08, 2021082218,   , OFCL,  36, 409N,  727W,  60,  984,   ,  34, NEQ,   90,  120,   80,   60, 1013,     ,   0,     ,    ,    ,    ,    ,346,  11,    HENRI   ,   5,    2, 1, 1, 1, 1,     30.9,   44.9,   32.9,   24.1,    1.1233,   1.3333,   1.4300,   1.3467,   1.2862,  59.1787,  59.1787,  59.1787,  59.1787
# AL, 08, 2021082218,   , OFCL,  36, 409N,  727W,  60,  984,   ,  50, NEQ,   50,   60,   30,   20, 1013,     ,   0,     ,    ,    ,    ,    ,346,  11,    HENRI   ,   5,    2, 1, 1, 1, 1,     29.4,   34.1,   30.0,   20.0,    1.1233,   1.3226,   1.3553,   1.4032,   1.2967,  59.1787,  59.1787,  61.0226,  60.1418
# AL, 08, 2021082306,   , OFCL,  48, 421N,  736W,  35, 1000,   ,  34, NEQ,   40,   80,   30,   30, 1013,     ,   0,     ,    ,    ,    ,    ,331,   7,    HENRI   ,   6,    1, 1, 1, 1, 1,     40.0,   79.9,   30.0,   30.0,    0.7917,   1.1244,   1.6315,   1.6430,   1.4526,  32.6299,  34.9991,  42.7683,  39.8732
# AL, 08, 2021082318,   , OFCL,  60, 428N,  733W,  25, 1000,   ,  34, NEQ,    0,    0,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 18,   4,    HENRI   ,   7,    1, 1, 1, 1, 1,     40.0,   79.9,   30.0,   30.0,    0.4119,   0.7254,   0.7254,   0.7254,   0.7254,  23.9921,  23.9921,  23.9921,  23.9921
# AL, 08, 2021082406,   , OFCL,  72, 433N,  715W,  25, 1000,   ,  34, NEQ,    0,    0,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 69,   7,    HENRI   ,   8,    1, 1, 1, 1, 1,     40.0,   79.9,   30.0,   30.0,    0.3487,   0.6567,   0.6567,   0.6567,   0.6567,  22.0742,  22.0742,  22.0742,  22.0742
# AL, 08, 2021082506,   , OFCL,  96, 445N,  625W,  25, 1000,   ,  34, NEQ,    0,    0,    0,    0, 1013,     ,   0,     ,    ,    ,    ,    , 80,  17,    HENRI   ,   9,    1, 1, 1, 1, 1,     40.0,   79.9,   30.0,   30.0,    0.2325,   0.5110,   0.5110,   0.5110,   0.5110,  18.0278,  18.0278,  18.0278,  18.0278


# Wind_Inp.txt sample only dynamic fields are 3 and 5th fields. Date and delta hours. Rest are hardcoded
# richamp 
# 3 
# 2023 09 01 12 00 00 
# 1.0 
# 426 
# -101.0 -49.0 
# 4.0  51. 
# 12. 

# track.richamp sample (size of each field must stay same. adding padding zeros. EX: 090)
# First field "NHC A13 URIPWMIN " hardcoded except for 13, storm numbers
# Date, hour+minute, latitude, longitude with padding "0" if len(string) == 4
# heading (calculated from delta of track position. current position to next position. last heading is copied from second to last heading)
# low pressure, high pressure, radius of closure (radius of max winds * 20), padded with 0, should be 4 characters,
#  max wind speed meters/sec, 2 char int, radius of max wind 3 char
# NHC A13 URIPWMIN   20230901 1200 95N 0135W 270 1011 1014 0406 10 020 -999 -999 -999 -999 D -999 -999 -999 -999


# Original line, low pressure printed twice
# NHC A13 URIPWMIN   20230901 1200 95N 0135W 270 1011 1011 1014 0406 10 020 -999 -999 -999 -999 D -999 -999 -999 -999

def vectorDirection(x,y):
    degrees = math.degrees(math.atan2(x,y))
    if(degrees < 0):
        return degrees + 360
    return degrees
    
def findHeading(previousLatitude, latitude, deltaLongitude):
    latitude = math.radians(latitude)
    previousLatitude = math.radians(previousLatitude)
    deltaLongitude = math.radians(deltaLongitude)
    x = math.cos(latitude) * math.sin(deltaLongitude)
    y = math.cos(previousLatitude) * math.sin(latitude)
    y = y - (math.sin(previousLatitude) * math.cos(latitude) * math.cos(deltaLongitude))
    return vectorDirection(x, y)
    
def convertLongitude(longitudeString):
    longitude = float(longitudeString[0:-1])/10
    if (longitudeString[-1] == "W"):
        longitude = longitude * -1.0
    return longitude

def convertLatitude(latitudeString):
    latitude = float(latitudeString[0:-1])/10
    if (latitudeString[-1] == "S"):
        latitude = latitude * -1.0
    return latitude

def calculateRadiusOfMaxWind(latitudeString, pressure, background):
    pressure = float(pressure)
    background = float(background)
    latitude = convertLatitude(latitudeString)
    deltaPressure = background - pressure
#         % if not specified - calculated %Rmax = exp(2.636 - ((0.00005086 * (dP ^ 2)) + 0.0394899 * latitude)) 
    radiusOfMaxWind = (0.00005086 * (deltaPressure**2))
    radiusOfMaxWind = 2.636 - radiusOfMaxWind + 0.0394899 * latitude
    radiusOfMaxWind = math.exp(radiusOfMaxWind)
    return radiusOfMaxWind
    

def main():
    p = argparse.ArgumentParser(description="Make a request to generate parametric wind input")
    p.add_argument(
        "--track", help="NHC Track file. In floodwater this file is nhc_merge*.track", type=str
    )
    args = p.parse_args()
    args.epsg = 4326
    trackDict = {}
    stormName = ""
    stormType = ""
    stormNumber = ""
    trackDict["date"] = []
    trackDict["pressure"] = []
    trackDict["background"] = []
    trackDict["latitude"] = []
    trackDict["longitude"] = []
    trackDict["radius"] = []
    trackDict["wind"] = []
#     data[3]
    trackTimes = []
    trackDeltaHours = []
    trackHeadings = []
#     data[5]
    latitudeStrings = []
    longitudeStrings = []
    centralPressures = []
    backgroundPressures = []
    radiusMaxWinds = []
    radiusClosures = []
    maxWindSpeeds = []
    stormSpans = []
    largeStormSpans = []
    
    dataDict = None
    lineCount = sum(1 for line in open(args.track))
    with open(args.track) as trackFile:
        dataDict = csv.DictReader(trackFile, fieldnames=["basin","number","date","unknown1", "type", "hours", "latitude", "longitude", "wind", "pressure", "class", "unknown2", "unknown3", "34ktNE", "34ktSE", "34ktSW", "34ktNW", "background", "closure", "radius", "unknown8", "unknown11", "unknown12", "unknown13", "unknown14", "unknown15", "name"])
        print(dataDict)
        previousLatitude = None
        previousLongitude = None
        for index, row in enumerate(dataDict):
            dateStr = row["date"].strip()
            hoursStr = row["hours"].strip()
            year = int(dateStr[0:4])
            month = int(dateStr[4:6])
            day = int(dateStr[6:8])
            hour = int(dateStr[8:10])
            hours = int(hoursStr)
#             print("date hours", row["date"], row["hours"])
            
            time = datetime(year=year, month=month, day=day, hour=hour) + timedelta(hours=hours)
            if(time not in trackTimes):
                stormNumber = row["number"].strip()
                trackTimes.append(time)
                trackDeltaHours.append(hours)
                centralPressures.append(int(row["pressure"].strip()))
                backgroundPressure = int(row["background"].strip())
                if(backgroundPressure == 0):
                    backgroundPressure = 1014
                backgroundPressures.append(backgroundPressure)
                radiusOfMaxWind = float(row["radius"].strip())
#                 print("radiusOfMaWind", radiusOfMaxWind)
#                 Calculate both radius of max wind and closure radius, instead of relying on track values
                if(radiusOfMaxWind == 0 or True):
                    radiusOfMaxWind = calculateRadiusOfMaxWind(row["latitude"], row["pressure"], row["background"])
#                 print(radiusOfMaxWind)
#                 closureRadius = float(row["closure"].strip())
                if(True):
#                     print("setting Closure radius")
#                   closure radius is max wind times 20
                    closureRadius = radiusOfMaxWind * 20
                radiusOfMaxWind = round(radiusOfMaxWind, 4)
                radiusMaxWinds.append(radiusOfMaxWind)
                radiusClosures.append(closureRadius)
#                 Convert to m/s
                maxWindSpeed = float(row["wind"].strip()) * 0.514444
#                 print("MaxWindSpeed", maxWindSpeed)
                maxWindSpeeds.append(maxWindSpeed)
#                 Convert to KM, from nautical miles
                windNE = float(row["34ktNE"].strip()) * 1.852
                if(windNE == 0):
                    windNE = -999
                print("34ktNE", windNE)
                windSE = float(row["34ktSE"].strip()) * 1.852
                if(windSE == 0):
                    windSE = -999
                print("34ktSE", windSE)
                windNW = float(row["34ktNW"].strip()) * 1.852
                if(windNW == 0):
                    windNW = -999
                print("34ktNW", windNW)
                windSW = float(row["34ktSW"].strip()) * 1.852
                if(windSW == 0):
                    windSW = -999
                print("34ktSW", windSW)
                stormSpans.append((windNE, windSE, windNW, windSW))
                if(index > 0):
                    largeStormSpans.append((windNE, windSE, windNW, windSW))
                latitudeStrings.append(row["latitude"].strip())
                longitudeStrings.append(row["longitude"].strip())
#                 print(row["latitude"])
                latitude = convertLatitude(row["latitude"])
                longitude = convertLongitude(row["longitude"])
                
#                 heading = int(row["heading?"].strip())
#                 print("headingString", heading)
                if(not previousLatitude and not previousLongitude):
                    previousLatitude = latitude
                    previousLongitude = longitude
#                 Use only calculated heading
                else:     
                    deltaLatitude = latitude - previousLatitude
                    deltaLongitude = longitude - previousLongitude
                    heading = findHeading(previousLatitude, latitude, deltaLongitude)
                    print("calculated", heading)
                    trackHeadings.append(heading)
#                 if(heading == 0 and (previousLatitude != latitude or previousLongitude != longitude)):     
#                     deltaLatitude = latitude - previousLatitude
#                     deltaLongitude = longitude - previousLongitude
#                     heading = findHeading(previousLatitude, latitude, deltaLongitude)
#                     print("calculated", heading)
#                 if(heading != 0):
#                     print(heading)
#                     trackHeadings.append(heading)
                    
                print(latitude, longitude)
        trackHeadings.append(trackHeadings[-1])
        largeStormSpans.append((-999, -999, -999, -999))
        print(len(largeStormSpans))
        print(len(stormSpans))
#                 print("closureRadius", closureRadius)
#                 print(float(row["wind"]) * 0.514444)
#                 print("radiusOfMaxWind", round(radiusOfMaxWind, 4))
                
    with open("TrackRMW.txt", "w") as f:
        f.write("Yr, Mo, Day, Hr, Min, Sec, Central P(mbar), Background P(mbar), Radius of Max Winds (km)\n")
        for index, trackTime in enumerate(trackTimes):
            f.write(str(trackTime.year) + " " + str(trackTime.month) + " " + str(trackTime.day) + " " + str(trackTime.hour) + " " + str(trackTime.minute) + " " + str(trackTime.second) + " " + str(centralPressures[index]) + " " + str(backgroundPressures[index]) + " " + str(radiusMaxWinds[index]) + "\n")
        f.close()

    with open("Wind_Inp.txt", "w") as f:
        f.write("richamp\n")
        f.write("3\n")
        minTrackTime = min(trackTimes)
        f.write(str(minTrackTime.year).zfill(4) + " " + str(minTrackTime.month).zfill(2) + " " + str(minTrackTime.day).zfill(2) + " " + str(minTrackTime.hour).zfill(2) + " " + str(minTrackTime.minute).zfill(2) + " " + str(minTrackTime.second).zfill(2) + "\n")
        f.write("1.0\n")
        f.write(str(max(trackDeltaHours)) + "\n")
        f.write("-101.0 -49.0\n")
        f.write("4.0  51.\n")
        f.write("12.\n")
        f.close()

    with open("track.richamp", "w") as f:
        for index, trackTime in enumerate(trackTimes):
            stormAndDateString = "NHC A" + stormNumber + " URIPWMIN  " + str(trackTime.year).zfill(4) + " " + str(trackTime.month).zfill(2) + " " + str(trackTime.day).zfill(2) + " " + str(trackTime.hour).zfill(2) + " " + str(trackTime.minute).zfill(2)
            bearingString = latitudeStrings[index].zfill(3) + " " + longitudeStrings[index].zfill(5) + " " + str(round(trackHeadings[index])).zfill(3)
            pressureAndRadiusString = str(centralPressures[index]).zfill(4) + " " + str(backgroundPressures[index]).zfill(4) + " " + str(round(radiusClosures[index])).zfill(4) + " " + str(round(maxWindSpeeds[index])).zfill(2) + " " + str(round(radiusMaxWinds[index])).zfill(3)
            print("writing tack")
            print(len(stormSpans))
            stormSpanString = str(round(stormSpans[index][0])).zfill(4) + " " + str(round(stormSpans[index][1])).zfill(4) + " " + str(round(stormSpans[index][2])).zfill(4) + " " + str(round(stormSpans[index][3])).zfill(4)
            largeStormSpanString = str(round(largeStormSpans[index][0])).zfill(4) + " " + str(round(largeStormSpans[index][1])).zfill(4) + " " + str(round(largeStormSpans[index][2])).zfill(4) + " " + str(round(largeStormSpans[index][3])).zfill(4)

            f.write(stormAndDateString + " " + bearingString + " " + pressureAndRadiusString + " " + stormSpanString + " D " + largeStormSpanString + "\n")
        f.close()

    
if __name__ == "__main__":
    main()
