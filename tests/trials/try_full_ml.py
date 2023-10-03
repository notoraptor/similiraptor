"""
https://medium.com/analytics-vidhya/image-similarity-model-6b89a22e2f1a

https://github.com/ChaitanyaNarva/image-similarity-model
"""

# For commands
import os
import time
from tqdm.notebook import tqdm
import warnings

warnings.filterwarnings("ignore")
# For array manipulation
import numpy as np
import pandas as pd
import pandas.util.testing as tm

# For visualization
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import cv2
import imageio as io
from pylab import *
from sklearn.manifold import TSNE

# For model performance
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.externals import joblib

# For model training
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
import tensorflow as tf
from sklearn.neighbors import KNeighborsClassifier
from tensorflow.keras.models import Sequential
from keras.applications.vgg16 import preprocess_input
from tensorflow.keras.layers import Conv2D, Activation, MaxPooling2D, UpSampling2D
from tensorflow.keras.optimizers import Adam, Adagrad, RMSprop
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import backend as K
from keras.models import load_model
from keras.preprocessing import image

file_path = os.listdir("../dataset")
print(len(file_path))
