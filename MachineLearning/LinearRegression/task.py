import matplotlib.pyplot as plt
import numpy as np
import csv
import random


def random_split(X, y, test_ratio=0.5):
    used_indices = set()
    objects_count, feature_count = X.shape
    X_test, y_test, X_train, y_train = [], [], [], []
    while (len(used_indices) < test_ratio * objects_count):
        rand_idx = random.randint(0, objects_count - 1)
        if (rand_idx not in used_indices):
            used_indices.add(rand_idx)
            X_test.append(X[rand_idx])
            y_test.append(y[rand_idx])
    X_train = np.array([X[i] for i in range(objects_count) if i not in used_indices])
    y_train = np.array([y[i] for i in range(objects_count) if i not in used_indices])
    return X_train, y_train, np.array(X_test), np.array(y_test)


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

positive_features_indices = []


def save_positive_features_indices(X_learn, X_test):
    global positive_features_indices
    positive_features_indices = [i for i in range(X_learn.shape[1]) if (np.min(X_learn[:, i]) > 0 and np.min(X_test[:, i]) > 0)]


def get_positive(X):
    return np.array([X[:, i] for i in positive_features_indices]).T


def log_features(X):
    return np.log(get_positive(X) + 1)


def square_features(X):
    return np.power(get_positive(X), 2.0)


def inv_features(X):
    return np.power(get_positive(X), -1.0)


def generate_additional_features(X, y):
    return np.concatenate((X, log_features(X), square_features(X), inv_features(X)), axis=1), y


def plot_hist(X, idx):
    plt.hist(X[:, idx], bins='sqrt')
    plt.title(idx)
    plt.show()


def plot_hist_flat(arr):
    plt.hist(arr, bins='sqrt')
    plt.show()


def get_learn_data():
    data = np.genfromtxt('learn.csv', delimiter=',')
    X = data[1:,1:-1]    # 1st+ rows, 1st + column (skip id), except last column
    X = np.append(np.ones((X.shape[0], 1)), X, axis=1)
    y = data[1:, -1]     # only last column
    return X, y


def get_test_data():
    data = np.genfromtxt('test.csv', delimiter=',')
    ids = data[1:, :1]   # only first column
    X = data[1:,1:]      # 1st+ rows, 1st+ column (skip id)
    X = np.append(np.ones((X.shape[0], 1)), X, axis=1)
    return X, ids


def rmse(a, b):
    return np.sqrt(np.sum(np.power(a - b, 2.0)) / a.size) 


def get_predictor(X, y):
    return np.dot(np.dot(np.linalg.pinv(np.dot(X.T, X)), X.T), y)


def main():
    save_positive_features_indices(get_learn_data()[0], get_test_data()[0])
    good_features_indices = forward_stepwise_selection_cv(*generate_additional_features(*get_learn_data()))
    save_prediction(*generate_additional_features(*get_learn_data()), good_features_indices)
    

def save_prediction(X_train, y_train, good_features_indices):
    X_real, ids = generate_additional_features(*get_test_data())
    print(X_real.shape)
    predictor = get_predictor(X_train[:, good_features_indices], y_train)
    prediction = get_prediction_in_range(X_real[:, good_features_indices], predictor)
    # prediction = get_prediction(X_real[:, good_features_indices], predictor)
    # plot_hist_flat(prediction)
    print('max: ', np.max(prediction), ', min: ', np.min(prediction))
    with open('out.csv', 'w', newline='\n') as f:
        writer = csv.writer(f)
        writer.writerow(["id","target"])
        writer.writerows(zip(ids.flatten().astype(np.int32), prediction))


def forward_stepwise_selection_cv(X, y):
    objects_count, feature_count = X.shape
    y = y.reshape(objects_count, 1)
    current_features_indices = [0]
    for _ in range(8): # features in output model, or use while loop
        best_feature_idx, best_feature_value = -1, float("inf")
        for feature_idx in range(feature_count):
            feature_rmse = 0.0
            for X_train, y_train, X_test, y_test in cv(X, y, n_folds=10): 
                new_features_indices = current_features_indices + [feature_idx]
                predictor = get_predictor(X_train[:, new_features_indices], y_train)
                feature_rmse += rmse(y_test, get_prediction(X_test[:, new_features_indices], predictor))
            if (feature_rmse < best_feature_value):
                best_feature_idx, best_feature_value = feature_idx, feature_rmse
        current_features_indices.append(best_feature_idx)
        # plot_hist(X_train, best_feature_idx)
        print("On this step selected feature is: ", best_feature_idx, ", with rmse ", best_feature_value)
    return current_features_indices


def get_prediction(data, predictor):
    return np.dot(data, predictor)
    

def get_prediction_in_range(data, predictor):
    prediction = get_prediction(data, predictor)
    for pr_idx in range(prediction.shape[0]):
        prediction[pr_idx] = max(0.0, min(50.0, prediction[pr_idx]))
    return prediction


main()
