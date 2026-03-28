import numpy as np

# Collection of different classifiers (static functions only, trained elsewhere!)

# Simpliest method, only uses 4 voltages
def second_highest(v):

    # Find 2nd highest voltage (AB, AD, etc.)
    index = np.argsort(v[:4])[-2]

    # 2nd highest voltage defines location of OHR
    match index:
        case 0:
            v_raw = np.array([0, 0, 0, 1])
        case 1:
            v_raw = np.array([0, 0, 1, 0])
        case 2:
            v_raw = np.array([0, 1, 0, 0])
        case 3:
            v_raw = np.array([1, 0, 0, 0])

    return v_raw


# Original method, uses all voltages
def absolute_conditionals(v):
    pass


# Allows softmax to generate actual probability distribution
def numeric_conditionals(v):
    alpha=1
    pass


# Allows for linear bias to account for voltage offsets
# Most accurate
# https://en.wikipedia.org/wiki/Discriminative_model
def linear_classifier(v):
    # For linear classifier, learned from data
    W1 = None
    B1 = None

    W2 = None
    B2 = None

    pass
