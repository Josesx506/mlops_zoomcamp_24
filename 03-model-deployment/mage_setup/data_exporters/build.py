from typing import List, Tuple

from pandas import DataFrame, Series
from scipy.sparse._csr import csr_matrix
from sklearn.base import BaseEstimator

from mlops.utils.data_preparation.encoders import vectorize_features

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_exporter
def export(
    data: DataFrame, *args, **kwargs
) -> Tuple[
    csr_matrix,
    Series,
    BaseEstimator,
]:
    df = data
    target = kwargs.get('target', 'duration')
    categorical = ['PULocationID', 'DOLocationID']
    

    X, _, dv = vectorize_features(df[categorical])
    y: Series = df[target]

    return X, y, dv
