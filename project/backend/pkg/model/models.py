import sklearn
from sklearn.ensemble import (ExtraTreesRegressor, GradientBoostingRegressor,
                              RandomForestRegressor)
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.svm import LinearSVR
from xgboost import XGBRegressor
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll import scope

def load_sklearn_models():
    model_list = [ExtraTreesRegressor, 
                  GradientBoostingRegressor,
                  RandomForestRegressor]
    # ,Lasso,LinearRegression,LinearSVR

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


def model_hyperparameters(model_name,
                          random_state: int = 42):

    match model_name:
        case "XGBRegressor":
            params = dict(colsample_bytree=hp.uniform("colsample_bytree", 0.5, 1.0),     # Controls the fraction of features (columns) that will be randomly sampled for each tree.
                          gamma=hp.uniform("gamma", 0.1, 1.0),                           # Minimum loss reduction required to make a further partition on a leaf node of the tree.
                          learning_rate=hp.loguniform("learning_rate", -3, 0),
                          max_depth=scope.int(hp.quniform("max_depth", 4, 100, 1)),      # Maximum depth of a tree.
                          min_child_weight=hp.loguniform("min_child_weight", -1, 3),  
                          objective="reg:squarederror",
                          random_state=random_state,                                     # Preferred over seed.
                          reg_alpha=hp.loguniform("reg_alpha", -5, -1),                  # L1 regularization term on weights (xgb’s alpha).
                          reg_lambda=hp.loguniform("reg_lambda", -6, -1),                # L2 regularization term on weights (xgb’s lambda).
                          subsample=hp.uniform("subsample", 0.1, 1.0),                   # Fraction of samples to be used for each tree.
                          )
            return params
        
        case "LinearRegression":
            choices = dict(fit_intercept=True)
            return choices
        
        case "Lasso":
            params = dict(alpha=hp.uniform("alpha", 0.0001, 1.0),             # Regularization strength; must be a positive float
                          max_iter=scope.int(hp.quniform("max_iter", 1000, 5000, 100)))
            return params
        
        case "ExtraTreesRegressor":
            params = dict(
                max_depth=scope.int(hp.quniform("max_depth", 5, 30, 5)),
                min_samples_leaf=scope.int(hp.quniform("min_samples_leaf", 1, 10, 1)),
                min_samples_split=scope.int(hp.quniform("min_samples_split", 2, 20, 2)),
                n_estimators=scope.int(hp.quniform("n_estimators", 10, 40, 10)),
                random_state=random_state,
            )
            return params
        
        case "GradientBoostingRegressor":
            params = dict(
                learning_rate=hp.loguniform("learning_rate", -5, 0),                    # Between e^-5 and e^0
                max_depth=scope.int(hp.quniform("max_depth", 5, 40, 1)),
                min_samples_leaf=scope.int(hp.quniform("min_samples_leaf", 1, 10, 1)),
                min_samples_split=scope.int(hp.quniform("min_samples_split", 2, 20, 1)),
                n_estimators=scope.int(hp.quniform("n_estimators", 10, 50, 10)),
                random_state=random_state,
            )
            return params
        
        case "RandomForestRegressor":
            params = dict(
                max_depth=scope.int(hp.quniform("max_depth", 5, 45, 5)),
                min_samples_leaf=scope.int(hp.quniform("min_samples_leaf", 1, 10, 1)),
                min_samples_split=scope.int(hp.quniform("min_samples_split", 2, 20, 1)),
                n_estimators=scope.int(hp.quniform("n_estimators", 10, 60, 10)),
                random_state=random_state,
            )
            return params
        
        case "LinearSVR":
            params = dict(epsilon=hp.uniform("epsilon", 0.0, 1.0),
                          C=hp.loguniform("C", -7, 3),            # This would give you a range of values between e^-7 and e^3
                          max_iter=scope.int(hp.quniform("max_iter", 1000, 5000, 100)),
            )
            return params
        
        case _:
            raise ValueError("Valid model_name should be one of `ExtraTreesRegressor," + \
                             "GradientBoostingRegressor,RandomForestRegressor,Lasso," + \
                             "LinearRegression,LinearSVR`")