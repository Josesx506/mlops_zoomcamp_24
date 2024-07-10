import sklearn
from sklearn.ensemble import (ExtraTreesRegressor, GradientBoostingRegressor,
                              RandomForestRegressor)
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.svm import LinearSVR
from xgboost import XGBRegressor

def load_sklearn_models():
    model_list = [ExtraTreesRegressor, 
                  GradientBoostingRegressor,
                  RandomForestRegressor,
                  Lasso,LinearRegression,
                  LinearSVR]

    # ensemble_models = [
    #         "ensemble.ExtraTreesRegressor",
    #         "ensemble.GradientBoostingRegressor",
    #         "ensemble.RandomForestRegressor",
    #         "linear_model.Lasso",
    #         "linear_model.LinearRegression",
    #         "svm.LinearSVR"
    #     ]
    # for module_and_class_name in ensemble_models:
    #     parts = module_and_class_name.split(".")
    #     cls = sklearn
    #     for part in parts:
    #         cls = getattr(cls, part)
        
    #     model_list.append(cls)
    
    return model_list

def load_xgboost_models():
    return [XGBRegressor]

def load_all_models():
    return load_sklearn_models() + load_xgboost_models()