"""Random Forest classification and computation of assessment metrics."""

import numpy as np
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier

from raster import is_raster


def transform_input(scene):
    """Transform input variables (here Landsat NDSV).

    Parameters
    ----------
    scene : landsat.Scene
        Input Landsat scene.

    Returns
    -------
    X : array
        Transformed input data as an array of shape (n_samples, n_features).
    """
    n_features = len(scene.ndsv_)
    n_samples = scene.profile['width'] * scene.profile['height']
    X = np.zeros(shape=(n_samples, n_features), dtype=np.float)
    ndsv = scene.ndsv
    for i in range(n_features):
        X[:, i] = ndsv[i, :, :].ravel()
    return X


def transform_test(true, pred):
    """Transform true and predicted raster data sets to
    flat arrays.

    Parameters
    ----------
    true : array-like
        Testing data set raster as a 2D NumPy array.
    pred : array-like
        Predicted values as a 2D NumPy array.

    Returns
    -------
    y_true : array
        1D array of true labels of shape (n_samples).
    y_pred : array
        1D array of predicted labels of shape (n_samples).
    """
    y_pred = pred[true > 0].ravel()
    y_true = true[true > 0].ravel()
    return y_true, y_pred


def transform_training(scene, training):
    """Transform training data set.

    Parameters
    ----------
    scene : landsat.Scene
        Input Landsat scene.
    training : 2D numpy array
        Training data raster as a 2D numpy array.

    Returns
    -------
    X : array
        Training samples as an array of shape (n_samples, n_features).
    y : array
        Training labels as an array of shape (n_samples).
    """
    n_features = len(scene.ndsv_)
    n_samples = np.count_nonzero(training)
    X = np.zeros(shape=(n_samples, n_features), dtype=np.float)
    ndsv = scene.ndsv
    for i in range(n_features):
        X[:, i] = ndsv[i, :, :][training > 0].ravel()
    y = training[training > 0].ravel()
    return X, y


def classify(
        scene,
        training,
        oversampling=False,
        undersampling=False,
        water=None,
        **kwargs):
    """Classify Landsat scene using Random Forest.

    Parameters
    ----------
    scene : landsat.Scene
        Input Landsat scene.
    training : 2D numpy array
        Input training data set as a 2D numpy array.
    oversampling : bool, optional
        If set to `True`, random oversampling will be performed on the
        minority class.
    undersampling : bool, optional
        If set to `True`, random undersampling will be performed on the
        majority class.
    water : 2D numpy array, optional
        If provided, water pixels will be ignored and classified as
        non-built.
    kwargs : **kwargs
        Additionnal arguments to the Random Forest classifier.

    Returns
    -------
    classes : 2D numpy array
        Binary output as a 2D numpy array.
    probabilities : 2D numpy array
        Probabilistic output as a 2D numpy array.
    """
    X = transform_input(scene)
    x_train, y_train = transform_training(scene, training)

    random_state = kwargs.pop('random_state', None)

    if oversampling:
        ros = RandomOverSampler(random_state=random_state)
        x_train, y_train = ros.fit_sample(x_train, y_train)

    if undersampling:
        ros = RandomUnderSampler(random_state=random_state)
        x_train, y_train = ros.fit_sample(x_train, y_train)

    rf = RandomForestClassifier(**kwargs)
    rf.fit(x_train, y_train)

    probabilities = rf.predict_proba(X)
    probabilities = probabilities[:, 0].reshape(scene.red.shape)

    if is_raster(water):
        probabilities[water] = 0

    return probabilities


def assess(probabilities, testing_dataset, threshold=0.75):
    """Compute validation metrics.

    Parameters
    ----------
    probabilities : 2D numpy array
        Predicted probabilities of belonging to
        the built-up class as a 2D NumPy array.
    testing_dataset : 2D numpy array
        Testing data set as as 2D NumPy array.
    threshold : float
        Threshold applied to the probabilistic output
        to obtain a binary product (0-1).

    Returns
    -------
    summary : dict
        Assessment metrics in a dictionnary.
    """
    summary = {}

    # Binary product obtained by thresholding the probabilities
    classes = np.zeros(shape=probabilities.shape, dtype=np.uint8)
    classes[probabilities >= threshold] = 1
    classes[probabilities < threshold] = 2

    # 1. Binary classification metrics:

    # Assign value 2 to all non-built land covers
    true, pred = testing_dataset.copy(), classes.copy()
    true[true >= 2] = 2
    pred[pred >= 2] = 2

    # Transform and binarize input data
    y_true, y_pred = transform_test(true, pred)
    y_true, y_pred = y_true == 1, y_pred == 1

    summary['accuracy'] = metrics.accuracy_score(
        y_true, y_pred
    )

    summary['balanced_accuracy'] = metrics.recall_score(
        y_true, y_pred
    )

    summary['precision'] = metrics.precision_score(
        y_true, y_pred
    )

    summary['recall'] = metrics.recall_score(
        y_true, y_pred
    )

    summary['f1_score'] = metrics.f1_score(
        y_true, y_pred
    )

    summary['confusion_matrix'] = metrics.confusion_matrix(
        y_true, y_pred
    )

    # 2. Continuous metrics based on probabilities:

    # Assign value 2 to all non-built land covers
    true = testing_dataset.copy()
    true[true >= 2] = 2

    # Transform and binarize input data
    y_true, y_pred = transform_test(true, probabilities)
    y_true = y_true == 1

    summary['pr_curve'] = metrics.precision_recall_curve(
        y_true, y_pred
    )

    summary['avg_precision'] = metrics.average_precision_score(
        y_true, y_pred, average='weighted'
    )

    # 3. Per land cover accuracies

    land_covers = {
        'builtup': 1,
        'baresoil': 2,
        'lowveg': 3,
        'highveg': 4
    }

    for label, value in land_covers.items():

        mask = testing_dataset == value
        true = testing_dataset[mask]
        pred = classes[mask]
        total = np.count_nonzero(mask)

        if label == 'builtup':
            accuracy = np.count_nonzero(pred == 1) / total
        else:
            accuracy = np.count_nonzero(pred >= 2) / total

        summary['{}_accuracy'.format(label)] = accuracy

    return summary
