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

def mse_lut(v):
    # input: [V_AB, V_AD, V_BC, V_CD, V_AC, V_BD]
    # output: [AD AB CD BC] (sum=1)

    # AB = np.array([0.283928571428571, 0.425, 0.530214285714286, 0.417285714285714, 0.557571428571429, 0.514285714285714])
    # BC = np.array([0.576615384615385, 0.910615384615385, 0.825846153846154, 0.485230769230769, 0.736230769230769, 0.839615384615385])
    # CD = np.array([0.338238095238095, 0.626380952380952, 0.798285714285714, 0.471095238095238, 0.582333333333333, 0.788333333333333])
    # AD = np.array([0.453526315789474, 0.694526315789474, 1.05936842105263, 0.600578947368421, 0.670894736842105, 1.08905263157895])


    AB = np.array([0.3935, 0.8155, 0.680275, 0.535575, 0.69945, 0.676225])
    BC = np.array([0.469475, 0.98365, 0.7295, 0.5296, 0.87585, 0.716475 ])
    CD = np.array([0.386225, 0.93265, 0.7363, 0.518525, 0.8448, 0.721925])
    AD = np.array([0.371925, 0.92035, 0.77965, 0.540925, 0.826775, 0.7696])

    refs = [CD, BC, AD, AB]

    # Compute MSE for each reference
    mses = [np.mean((v - ref) ** 2) for ref in refs]

    # Find index of minimum MSE
    min_idx = np.argmin(mses)

    # Create one-hot output
    out = np.zeros(4)
    out[min_idx] = 1

    return out


