import numpy as np

# Collection of different classifiers (static functions only, trained elsewhere!)
# input: [V_AB, V_AD, V_BC, V_CD, V_AC, V_BD]
# output: [AD AB CD BC] (sum=1)


# Simpliest method, only uses 4 voltages
def second_highest(v):

    # Find 2nd highest voltage (AB, AD, etc.)
    index = np.argsort(v[:4])[-2]

    # 2nd highest voltage defines location of OHR
    match index:
        case 0:
            return np.array([0, 0, 0, 1])
        case 1:
            return np.array([0, 0, 1, 0])
        case 2:
            return np.array([0, 1, 0, 0])
        case 3:
            return np.array([1, 0, 0, 0])


# Original method, uses all voltages (incomplete)
def absolute_conditionals(v):

    if v[4] > v[5]:
        # Either BC or CD
        if 0:
            pass

    else:
        if 0:
            pass
    # Either AD or AB


# Allows softmax to generate actual probability distribution
# Same logic as absolute conditional
def numeric_conditionals(v):
    alpha = 1
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
