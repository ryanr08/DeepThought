import os
import datetime
import sys

import IPython
import IPython.display
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False


def main():
    csv_path = "../../datasets/LTC-USD.csv"#__file__[:__file__.rindex('/')] + "/../../datasets/LTC-USD.csv"

    df = pd.read_csv(csv_path).iloc[: , 1:]

    print(df.head())

    print(df.describe().transpose())

    lstm_model = tf.keras.models.Sequential([
        # Shape [batch, time, features] => [batch, time, lstm_units]
        tf.keras.layers.LSTM(32, return_sequences=True),
        # Shape => [batch, time, features]
        tf.keras.layers.Dense(units=1)
    ])

if __name__ == "__main__":
    main() 
