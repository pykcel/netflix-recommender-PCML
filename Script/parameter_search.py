import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
from helpers import compute_error, split_data, calculate_mse
from postprocessing import construct_full_features
from matrix_factorization import ALS, matrix_factorization_SGD


def finding_gamma(train, test, gamma_array, lambda_user, lambda_item, num_features):
    """ Compute the train and test RMSE of the SGD prediction using the given parameters for each value in the gamma_array.

    :param train: train dataset
    :param test: test dataset
    :param gamma_array: the gamma values we will train
    :param lambda_user: the regularization SGD parameter
    :param lambda_item: the the regularization SGD parameter
    :param num_features: the number of features of our item's and user's matrices
    :return: the train RMSE and the test RMSE for each gamma
    """
    rmse_train_array = []
    rmse_test_array = []

    nz_row_te, nz_col_te = test.nonzero()
    nz_test = list(zip(nz_row_te, nz_col_te))
    nz_row_tr, nz_col_tr = train.nonzero()
    nz_train = list(zip(nz_row_tr, nz_col_tr))

    for gamma in gamma_array:
        print("predicting for gamma {}".format(gamma))
        predicted_user_features, predicted_item_features = matrix_factorization_SGD(train, test, gamma, lambda_user,
                                                                                    lambda_item, num_features)
        rmse_train_array.append(compute_error(train, predicted_user_features, predicted_item_features, nz_train))
        rmse_test_array.append(compute_error(test, predicted_user_features, predicted_item_features, nz_test))
    print(np.array(rmse_test_array))
    return np.array(rmse_train_array), np.array(rmse_test_array)


def find_min_num_ratings(min_num_ratings_array, ratings, num_items_per_user, num_users_per_item, p_test, lambda_item,
                         lambda_user, num_features):

    full_user_features_array = []
    full_item_features_array = []
    rmse_test_full_array = []
    rmse_train_full_array = []
    for min_num_ratings in min_num_ratings_array:
        print("Minimum number of ratings : {}".format(min_num_ratings))
        valid_ratings, train, test, valid_users, valid_items, train_full, test_full = split_data(
            ratings, num_items_per_user, num_users_per_item, min_num_ratings, p_test)

        predicted_user_features, predicted_item_features, _, _ = ALS(train, test, lambda_user, lambda_item,
                                                                     num_features)

        full_user_features, full_item_features = construct_full_features(predicted_user_features,
                                                                         predicted_item_features,
                                                                         valid_users, valid_items, min_num_ratings,
                                                                         train_full,
                                                                         lambda_user, lambda_item)
        full_user_features_array.append(full_user_features)
        full_item_features_array.append(full_item_features)

        nz_row_te, nz_col_te = test_full.nonzero()
        nz_full_test = list(zip(nz_row_te, nz_col_te))
        nz_row_tr, nz_col_tr = train_full.nonzero()
        nz_full_train = list(zip(nz_row_tr, nz_col_tr))

        rmse_train_full = compute_error(train_full, full_user_features, full_item_features, nz_full_train)
        rmse_test_full = compute_error(test_full, full_user_features, full_item_features, nz_full_test)
        rmse_train_full_array.append(rmse_train_full)
        rmse_test_full_array.append(rmse_test_full)
    return full_item_features_array, full_user_features_array, rmse_train_full_array, rmse_test_full_array


def finding_num_features(train, test, num_features_array):
    rmse_train_array = []
    rmse_test_array = []
    item_features_array = []
    user_features_array = []
    nz_row_te, nz_col_te = test.nonzero()
    nz_test = list(zip(nz_row_te, nz_col_te))
    nz_row_tr, nz_col_tr = train.nonzero()
    nz_train = list(zip(nz_row_tr, nz_col_tr))

    for num_features in num_features_array:
        print("predicting for {} of features".format(num_features))
        predicted_user_features, predicted_item_features, rmse_train_table, rmse_test = ALS(train, test, 0.09, 0.09,
                                                                                            num_features)
        item_features_array.append(predicted_item_features)
        user_features_array.append(predicted_user_features)
        rmse_train_array.append(rmse_train_table[len(rmse_train_table) - 1])
        rmse_test_array.append(rmse_test)
    return rmse_train_array, rmse_test_array, item_features_array, user_features_array


def finding_lambdas(train, test, lambda_user_array, lambda_item_array, num_features):
    rmse_train_array = []
    rmse_test_array = []

    nz_row_te, nz_col_te = test.nonzero()
    nz_test = list(zip(nz_row_te, nz_col_te))
    nz_row_tr, nz_col_tr = train.nonzero()
    nz_train = list(zip(nz_row_tr, nz_col_tr))

    for lambda_user in lambda_user_array:
        rmse_train_array_user = []
        rmse_test_array_user = []
        for lambda_item in lambda_item_array:
            print("predicting for lambda_user {} and lambda_item {}".format(lambda_user, lambda_item))
            predicted_user_features, predicted_item_features, _, __ = ALS(train, test, lambda_user, lambda_item,
                                                                          num_features)
            rmse_train_array_user.append(
                compute_error(train, predicted_user_features, predicted_item_features, nz_train))
            rmse_test_array_user.append(compute_error(test, predicted_user_features, predicted_item_features, nz_test))
        rmse_train_array.append(rmse_train_array_user)
        rmse_test_array.append(rmse_test_array_user)
    # print(np.array(rmse_test_array))
    return np.array(rmse_train_array), np.array(rmse_test_array)


def finding_weighted_average(test,predictions_a, predictions_b):
    """

    :param predictions_a:
    :param predictions_b:
    :return:
    """
    a = np.linspace(0, 1.0, num=101)
    rmse_min = 10
    a_min = 0

    # for j in range(lambda_item_list.shape[0]):
    for i, value in enumerate(a):
        prediction_from_two = np.multiply(predictions_a, value) + np.multiply(predictions_b, 1 - value)
        x, y = test.nonzero()
        rmse = np.sqrt(calculate_mse(test[x, y], prediction_from_two[x, y]).sum() / (test.nnz))
        if rmse_min > rmse:
            rmse_min = rmse
            a_min = value

    print("RMSE={}".format(rmse_min))
    return a_min
