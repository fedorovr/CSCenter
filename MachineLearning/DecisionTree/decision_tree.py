import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import random
from sklearn.metrics import roc_auc_score
from collections import Counter

popular_features = Counter() # feature to count of usage it in intermediate nodes
max_depth = 10
min_leaf_size = 7


class Node:
    # Node may be leaf(feature_idx=feature_value=left=right=None) or not leaf(probability=None)
    def __init__(self, probability=None, feature_idx=None, feature_value=None, left=None, right=None):
        self.probability = probability
        self.feature_idx = feature_idx
        self.feature_value = feature_value
        self.left = left
        self.right = right

    def predict(self, target_object):
        if (self.probability is not None): # we are in a leaf
            return self.probability
        elif (target_object[self.feature_idx] <= self.feature_value):
            return self.left.predict(target_object)
        else:
            return self.right.predict(target_object)


def cv(X, y, n_folds=5):
    fold_size = int(X.shape[0] / n_folds)
    dataset = np.concatenate((X, y), axis=1)
    random_permutation = np.random.permutation(dataset)
    X_permutation, y_permutation = random_permutation[:, :-1], random_permutation[:, -1]
    for fold_idx in range(n_folds):
        fold_start_idx = fold_idx * fold_size
        fold_end_idx = (fold_idx + 1) * fold_size 
        yield(X_permutation[list(range(0, fold_start_idx)) + list(range(fold_end_idx, dataset.shape[0]))],
              y_permutation[list(range(0, fold_start_idx)) + list(range(fold_end_idx, dataset.shape[0]))],
              X_permutation[range(fold_start_idx, fold_end_idx)],
              y_permutation[range(fold_start_idx, fold_end_idx)])


def plot_hist(X, y):
    for idx in range(75, X.shape[1]):
        plot_hist_flat(X[:, idx], idx)
    plot_hist_flat(y, 'y')


def plot_hist_flat(arr, label):
    plt.hist(arr, bins='sqrt')
    plt.title(label)
    plt.show()


def get_data():
    learn_df = pd.read_csv('learn.csv')
    labels = learn_df[['label']]
    learn_df.drop(['label', 'id'], axis=1, inplace=True)
    learn_shape = learn_df.shape

    test_df = pd.read_csv('test.csv')
    ids = test_df[['id']]
    test_df.drop('id', axis=1, inplace=True)
    
    all_data = learn_df.append(test_df)
    all_data = pd.get_dummies(all_data, columns=['f_16', 'f_22', 'f_30', 'f_37'])
    learn_df = all_data[:learn_shape[0]]
    test_df = all_data[learn_shape[0]:]   

    X_learn = learn_df.as_matrix()
    y_learn = labels.as_matrix()
    X_test = test_df.as_matrix()
    ids = ids.as_matrix()

    # plot_hist(X_learn, y_learn)

    return X_learn, y_learn, X_test, ids


# Split with Gini impurity 
def get_node(X, y, depth=1):
    global popular_features
    global max_depth
    global min_leaf_size
    if ((depth >= max_depth) or (X.shape[0] <= min_leaf_size) or (np.sum(y) == 0) or (np.sum(y) == X.shape[0])): # return leaf node
        return Node(probability=np.sum(y) / X.shape[0])
    best_split_value, best_split_feature, best_split_object = float('+inf'), -1, -1
    for feature_idx in range(X.shape[1]):
        values = np.append(X[:, feature_idx].reshape(y.shape), y, axis=1)
        sorted_values = values[values[:, 0].argsort()]
        p0_l, p1_l = 0.0, 0.0       # 0 and 1 probability in left node
        p0_r, p1_r = (values.shape[0] - np.sum(y)) / values.shape[0], np.sum(y) / values.shape[0]
        split_value = p0_r + p1_r - (p0_r * p0_r) - (p1_r * p1_r) 
        if (split_value < best_split_value):
            best_split_value, best_split_feature, best_split_object = split_value, feature_idx, 0
        for object_idx in range(sorted_values.shape[0] - 1):
            p0_l, p1_l, p0_r, p1_r, current_split_value = update_probabilities(p0_l, p1_l, p0_r, p1_r, object_idx, sorted_values[object_idx, 1], values.shape[0])
            # print('for object idx=', object_idx, ', split value is: ', current_split_value)
            if (sorted_values[object_idx, 0] != sorted_values[object_idx + 1, 0] and current_split_value < best_split_value):
                best_split_value, best_split_feature, best_split_object = current_split_value, feature_idx, object_idx
    # print('found best split(val, feature, object)=', best_split_value, best_split_feature, best_split_object)
    if (best_split_object == 0):   # No split, return leaf node
        return Node(probability=np.sum(y) / X.shape[0])
    else:                          # Perform split and return intermediate node
        data = np.append(X, y, axis=1)
        sorted_data = data[data[:, best_split_feature].argsort()]
        left_part = sorted_data[:(best_split_object + 1)]
        right_part = sorted_data[(best_split_object + 1):]
        popular_features[best_split_feature] += 1
        return Node(feature_idx=best_split_feature,
                    feature_value=sorted_data[(best_split_object+1), best_split_feature],
                    left=get_node(left_part[:, :-1],   left_part[:, -1].reshape((left_part.shape[0], 1)), depth + 1),  # divide X and y
                    right=get_node(right_part[:, :-1], right_part[:, -1].reshape((right_part.shape[0], 1)), depth + 1)) # divide X and y


def update_probabilities(p0_l, p1_l, p0_r, p1_r, object_idx, object_value, objects_count):
    left_divider = object_idx + 1
    p0_l *= object_idx / left_divider
    p1_l *= object_idx / left_divider
    p0_l += int(object_value == 0) / left_divider
    p1_l += int(object_value == 1) / left_divider

    right_divider = objects_count - object_idx - 1
    p0_r *= (objects_count - object_idx) / right_divider
    p1_r *= (objects_count - object_idx) / right_divider
    p0_r -= int(object_value == 0) / right_divider
    p1_r -= int(object_value == 1) / right_divider

    current_split_value = (p0_l + p1_l - (p0_l * p0_l) - (p1_l * p1_l)) * left_divider / objects_count
    current_split_value += (p0_r + p1_r - (p0_r * p0_r) - (p1_r * p1_r)) * right_divider / objects_count

    return p0_l, p1_l, p0_r, p1_r, current_split_value


def process_data(X_learn, X_test, count=-1):
    awesome_features = [23, 40, 19, 22, 24, 0, 5, 44, 47, 18, 27]
    good_features = [23, 40, 22, 19, 24, 47, 14, 5, 31, 0, 13, 34, 35, 45, 26, 30, 44, 18, 32, 39, 1, 11, 15, 27, 29, 43, 67, 84, 139, 12, 38, 2, 6, 66]
    if (count == -1):
        count = len(good_features)
    for i in range(len(awesome_features)):
        for j in range(i + 1, len(awesome_features)):
            X_learn = np.append(X_learn, (X_learn[:, i] * X_learn[:, j]).reshape((X_learn.shape[0], 1)), axis=1)
            X_test = np.append(X_test, (X_test[:, i] * X_test[:, j]).reshape((X_test.shape[0], 1)), axis=1)
    return X_learn[:, good_features[:count]], X_test[:, good_features[:count]]


def main():
    X_learn, y_learn, X_test, ids = get_data()
    X_learn, X_test = process_data(X_learn, X_test, 15)
    # perform_model_validation(X_learn, y_learn) # chooses max_depth, good_features, features_count and min_leaf_size
    decision_tree = get_node(X_learn, y_learn)
    save_prediction(X_test, ids, decision_tree)
    

def perform_model_validation(X, y):
    # for max_depth_selection in range(7, 20, 2):
    # for feature_count in range(3, 34):
    for min_leaf_size_validator in range(1, 19, 2):
        global min_leaf_size
        min_leaf_size = min_leaf_size_validator
        # global popular_features
        # global max_depth
        # max_depth = max_depth_selection
        auc_sum, auc_per_fold = 0.0, []
        for X_learn, y_learn, X_test, y_test in cv(X, y, n_folds=4): 
            y_learn, y_test = y_learn.reshape((X_learn.shape[0], 1)), y_test.reshape((X_test.shape[0], 1))
            X_learn, X_test = process_data(X_learn, X_test, count=7) # feature_count
            decision_tree = get_node(X_learn, y_learn)
            prediction = get_prediction(X_test, decision_tree)
            current_auc = roc_auc_score(y_test, prediction)
            auc_sum += current_auc
            auc_per_fold.append(current_auc)
        print(min_leaf_size_validator, auc_sum / 4.0, auc_per_fold)
        # print('\t', len(popular_features), sum(popular_features.values()), popular_features)
        # popular_features = Counter()


def save_prediction(X_test, ids, decision_tree):    
    with open('out.csv', 'w', newline='\n') as f:
        writer = csv.writer(f)
        writer.writerow(["id","label"])
        writer.writerows(zip(ids.flatten().astype(np.int32), get_prediction(X_test, decision_tree)))


def get_prediction(X, decision_tree):
    return [decision_tree.predict(obj) for obj in X]


main()
