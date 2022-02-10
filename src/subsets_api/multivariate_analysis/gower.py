""" 
The gower distance similarity is not yet supported in scikitlearn. A work on the #16834 PR is pending.

This code is forked from https://github.com/adrinjalali/scikit-learn/blob/b5584/sklearn/metrics/pairwise.py#L870 
"""

import numpy as np
from itertools import compress

from scipy.spatial import distance
from scipy.sparse import issparse

from sklearn.metrics.pairwise import check_pairwise_arrays
from sklearn.utils.validation import check_consistent_length
from sklearn.utils import check_array
from sklearn.utils import _get_column_indices
from sklearn.utils.fixes import _object_dtype_isnan
from sklearn.preprocessing import MinMaxScaler


def _array_indexing(array, key, key_dtype, axis, complement):
    """Index an array or scipy.sparse consistently across NumPy version."""
    if issparse(array):
        # check if we have an boolean array-likes to make the proper indexing
        if key_dtype == 'bool':
            key = np.asarray(key)
    if isinstance(key, tuple):
        key = list(key)
    if complement:
        mask = np.ones(array.shape[0] if axis == 0 else array.shape[1], bool)
        mask[key] = False
        key = mask
    return array[key] if axis == 0 else array[:, key]


def _pandas_indexing(X, key, key_dtype, axis, complement):
    """Index a pandas dataframe or a series."""
    if hasattr(key, 'shape'):
        # Work-around for indexing with read-only key in pandas
        # FIXME: solved in pandas 0.25
        key = np.asarray(key)
        key = key if key.flags.writeable else key.copy()
    elif isinstance(key, tuple):
        key = list(key)
    # check whether we should index with loc or iloc
    indexer = X.iloc if key_dtype == 'int' else X.loc
    if complement:
        if key_dtype == 'str':
            # we reject string keys for rows
            key = _get_column_indices(X, key)
        if isinstance(key, tuple):
            key = list(key)
        mask = np.ones(X.shape[0] if axis == 0 else X.shape[1], bool)
        mask[key] = False
        key = mask
    return indexer[:, key] if axis else indexer[key]


def _list_indexing(X, key, key_dtype, complement):
    """Index a Python list."""
    if complement:
        if isinstance(key, tuple):
            key = list(key)
        mask = np.ones(len(X), bool)
        mask[key] = False
        key = mask
        key_dtype = 'bool'

    if np.isscalar(key) or isinstance(key, slice):
        # key is a slice or a scalar
        return X[key]
    if key_dtype == 'bool':
        # key is a boolean array-like
        return list(compress(X, key))
    # key is a integer array-like of key
    return [X[idx] for idx in key]

def _determine_key_type(key, accept_slice=True):
    """Determine the data type of key.
    Parameters
    ----------
    key : scalar, slice or array-like
        The key from which we want to infer the data type.
    accept_slice : bool, default=True
        Whether or not to raise an error if the key is a slice.
    Returns
    -------
    dtype : {'int', 'str', 'bool', None}
        Returns the data type of key.
    """
    err_msg = ("No valid specification of the columns. Only a scalar, list or "
               "slice of all integers or all strings, or boolean mask is "
               "allowed")

    dtype_to_str = {int: 'int', str: 'str', bool: 'bool', np.bool_: 'bool'}
    array_dtype_to_str = {'i': 'int', 'u': 'int', 'b': 'bool', 'O': 'str',
                          'U': 'str', 'S': 'str'}

    if key is None:
        return None
    if isinstance(key, tuple(dtype_to_str.keys())):
        try:
            return dtype_to_str[type(key)]
        except KeyError:
            raise ValueError(err_msg)
    if isinstance(key, slice):
        if not accept_slice:
            raise TypeError(
                'Only array-like or scalar are supported. '
                'A Python slice was given.'
            )
        if key.start is None and key.stop is None:
            return None
        key_start_type = _determine_key_type(key.start)
        key_stop_type = _determine_key_type(key.stop)
        if key_start_type is not None and key_stop_type is not None:
            if key_start_type != key_stop_type:
                raise ValueError(err_msg)
        if key_start_type is not None:
            return key_start_type
        return key_stop_type
    if isinstance(key, (list, tuple)):
        unique_key = set(key)
        key_type = {_determine_key_type(elt) for elt in unique_key}
        if not key_type:
            return None
        if len(key_type) != 1:
            raise ValueError(err_msg)
        return key_type.pop()
    if hasattr(key, 'dtype'):
        try:
            return array_dtype_to_str[key.dtype.kind]
        except KeyError:
            raise ValueError(err_msg)
    raise ValueError(err_msg)

def _safe_indexing(X, indices, *, axis=0, complement=False):
    """Return rows, items or columns of X using indices.
    .. warning::
        This utility is documented, but **private**. This means that
        backward compatibility might be broken without any deprecation
        cycle.
    Parameters
    ----------
    X : array-like, sparse-matrix, list, pandas.DataFrame, pandas.Series
        Data from which to sample rows, items or columns. `list` are only
        supported when `axis=0`.
    indices : bool, int, str, slice, array-like
        - If `axis=0`, boolean and integer array-like, integer slice,
          and scalar integer are supported.
        - If `axis=1`:
            - to select a single column, `indices` can be of `int` type for
              all `X` types and `str` only for dataframe. The selected subset
              will be 1D, unless `X` is a sparse matrix in which case it will
              be 2D.
            - to select multiples columns, `indices` can be one of the
              following: `list`, `array`, `slice`. The type used in
              these containers can be one of the following: `int`, 'bool' and
              `str`. However, `str` is only supported when `X` is a dataframe.
              The selected subset will be 2D.
    axis : int, default=0
        The axis along which `X` will be subsampled. `axis=0` will select
        rows while `axis=1` will select columns.
    complement : bool, default=False
        Whether to select the given columns or deselect them and return the
        rest.
    Returns
    -------
    subset
        Subset of X on axis 0 or 1.
    Notes
    -----
    CSR, CSC, and LIL sparse matrices are supported. COO sparse matrices are
    not supported.
    """
    if indices is None:
        return X

    if axis not in (0, 1):
        raise ValueError(
            "'axis' should be either 0 (to index rows) or 1 (to index "
            " column). Got {} instead.".format(axis)
        )

    indices_dtype = _determine_key_type(indices)

    if axis == 0 and indices_dtype == 'str':
        raise ValueError(
            "String indexing is not supported with 'axis=0'"
        )

    if axis == 1 and X.ndim != 2:
        raise ValueError(
            "'X' should be a 2D NumPy array, 2D sparse matrix or pandas "
            "dataframe when indexing the columns (i.e. 'axis=1'). "
            "Got {} instead with {} dimension(s).".format(type(X), X.ndim)
        )

    if axis == 1 and indices_dtype == 'str' and not hasattr(X, 'loc'):
        raise ValueError(
            "Specifying the columns using strings is only supported for "
            "pandas DataFrames"
        )

    if hasattr(X, "iloc"):
        return _pandas_indexing(X, indices, indices_dtype, axis=axis,
                                complement=complement)
    elif hasattr(X, "shape"):
        return _array_indexing(X, indices, indices_dtype, axis=axis,
                               complement=complement)
    else:
        return _list_indexing(X, indices, indices_dtype,
                              complement=complement)

def _split_categorical_numerical(X, categorical_features):
    # the following bit is done before check_pairwise_array to avoid converting
    # numerical data to object dtype. First we split the data into categorical
    # and numerical, then we do check_array

    if X is None:
        return None, None

    # TODO: this should be more like check_array(..., accept_pandas=True)
    if not hasattr(X, "shape"):
        X = check_array(X, dtype=np.object, force_all_finite=False)

    cols = categorical_features
    if cols is None:
        cols = []

    col_idx = _get_column_indices(X, cols)
    X_cat = _safe_indexing(X, col_idx, axis=1)
    X_num = _safe_indexing(X, col_idx, axis=1, complement=True)

    return X_cat, X_num


def gower_distances(X, Y=None, categorical_features=None, scale=True,
                    min_values=None, scale_factor=None):
    """Compute the distances between the observations in X and Y,
    that may contain mixed types of data, using an implementation
    of Gower formula.
    Parameters
    ----------
    X : {array-like, pandas.DataFrame} of shape (n_samples, n_features)
    Y : {array-like, pandas.DataFrame} of shape (n_samples, n_features), \
        default=None
    categorical_features : array-like of str, array-like of int, \
            array-like of bool, slice or callable, default=None
        Indexes the data on its second axis. Integers are interpreted as
        positional columns, while strings can reference DataFrame columns
        by name.
        A callable is passed the input data `X` and can return any of the
        above. To select multiple columns by name or dtype, you can use
        :obj:`~sklearn.compose.make_column_selector`.
        By default all non-numeric columns are considered categorical.
    scale : bool, default=True
        Indicates if the numerical columns should be scaled to [0, 1].
        If ``False``, the numerical columns are assumed to be already scaled.
        The scaling factors, _i.e._ ``min_values`` and ``scale_factor``, are
        taken from ``X``. If ``X`` and ``Y`` are both provided, ``min_values``
        and ``scale_factor`` have to be provided as well.
    min_values : ndarray of shape (n_features,), default=None
        Per feature adjustment for minimum. Equivalent to
        ``min_values - X.min(axis=0) * scale_factor``
        If provided, ``scale_factor`` should be provided as well.
        Only relevant if ``scale=True``.
    scale_factor : ndarray of shape (n_features,), default=None
        Per feature relative scaling of the data. Equivalent to
        ``(max_values - min_values) / (X.max(axis=0) - X.min(axis=0))``
        If provided, ``min_values`` should be provided as well.
        Only relevant if ``scale=True``.
    Returns
    -------
    distances : ndarray of shape (n_samples_X, n_samples_Y)
    References
    ----------
    Gower, J.C., 1971, A General Coefficient of Similarity and Some of Its
    Properties.
    Notes
    -----
    Categorical ordinal attributes should be treated as numeric for the purpose
    of Gower similarity.
    Current implementation does not support sparse matrices.
    This implementation modifies the Gower's original similarity measure in
    the sense that this implementation returns 1-S.
    """
    def _nanmanhatan(x, y):
        return np.nansum(np.abs(x - y))

    def _non_nans(x, y):
        return len(x) - np.sum(_object_dtype_isnan(x) | _object_dtype_isnan(y))

    def _nanhamming(x, y):
        return np.sum(x != y) - np.sum(
            _object_dtype_isnan(x) | _object_dtype_isnan(y))

    if issparse(X) or issparse(Y):
        raise TypeError("Gower distance does not support sparse matrices")

    if X is None or len(X) == 0:
        raise ValueError("X can not be None or empty")

    if scale:
        if (scale_factor is None) != (min_values is None):
            raise ValueError("min_value and scale_factor should be provided "
                             "together.")

    # scale_factor and min_values are either both None or not at this point
    if X is not Y and Y is not None and scale_factor is None and scale:
        raise ValueError("`scaling_factor` and `min_values` must be provided "
                         "when `Y` is provided and `scale=True`")

    if callable(categorical_features):
        cols = categorical_features(X)
    else:
        cols = categorical_features
    X_cat, X_num = _split_categorical_numerical(X, categorical_features=cols)
    Y_cat, Y_num = _split_categorical_numerical(Y, categorical_features=cols)

    if min_values is not None:
        min_values = np.asarray(min_values)
        scale_factor = np.asarray(scale_factor)
        check_consistent_length(min_values, scale_factor,
                                np.ndarray(shape=(X_num.shape[1], 0)))

    if X_num.shape[1]:
        X_num, Y_num = check_pairwise_arrays(X_num, Y_num, precomputed=False,
                                             dtype=float,
                                             force_all_finite=False)
        if scale:
            scale_data = X_num if Y_num is X_num else np.vstack((X_num, Y_num))
            if scale_factor is None:
                trs = MinMaxScaler().fit(scale_data)
            else:
                trs = MinMaxScaler()
                trs.scale_ = scale_factor
                trs.min_ = min_values
            X_num = trs.transform(X_num)
            Y_num = trs.transform(Y_num)

        nan_manhatan = distance.cdist(X_num, Y_num, _nanmanhatan)
        # nan_manhatan = np.nansum(np.abs(X_num - Y_num))
        valid_num = distance.cdist(X_num, Y_num, _non_nans)
    else:
        nan_manhatan = valid_num = None

    if X_cat.shape[1]:
        X_cat, Y_cat = check_pairwise_arrays(X_cat, Y_cat, precomputed=False,
                                             dtype=np.object,
                                             force_all_finite=False)
        nan_hamming = distance.cdist(X_cat, Y_cat, _nanhamming)
        valid_cat = distance.cdist(X_cat, Y_cat, _non_nans)
    else:
        nan_hamming = valid_cat = None

    # based on whether there are categorical and/or numerical data present,
    # we compute the distance metric
    # Division by zero and nans warnings are ignored since they are expected
    with np.errstate(divide='ignore', invalid='ignore'):
        if valid_num is not None and valid_cat is not None:
            D = (nan_manhatan + nan_hamming) / (valid_num + valid_cat)
        elif valid_num is not None:
            D = nan_manhatan / valid_num
        else:
            D = nan_hamming / valid_cat
    return D

