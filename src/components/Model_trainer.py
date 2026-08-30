import os
import sys


from src.exception import CustomException
from src.logger    import logging

from sklearn.linear_model import LogisticRegression
from sklearn.svm          import SVC
from sklearn.neighbors    import KNeighborsClassifier
from sklearn.tree         import DecisionTreeClassifier
from sklearn.ensemble     import VotingClassifier
from sklearn.ensemble     import BaggingClassifier
from sklearn.ensemble     import AdaBoostClassifier
from sklearn.ensemble     import GradientBoostingClassifier
from sklearn.ensemble     import RandomForestClassifier
from xgboost              import XGBClassifier

from sklearn.metrics      import accuracy_score
from sklearn.metrics      import confusion_matrix
from sklearn.metrics      import precision_score
from sklearn.metrics      import recall_score
from sklearn.metrics      import f1_score

from dataclasses          import dataclass                  
from src.utils import save_object,evaluate_models

class ModelTrainerConfig:
    train_model_file_path = os.path.join("artifacts","model.pkl")
    
class ModelTrainer:
    def __init__(self):
        self.ModelTrainerConfig = ModelTrainerConfig()
        
    def initiate_model_traineer(self, train_arr, test_arr):
        try:
            X_train,y_train,X_test,y_test = (
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )

            models = {
                "LogisticRegression"        : LogisticRegression(),
                "SupportVectorMachine"      : SVC(),
                "KNeighborsClassifier"      : KNeighborsClassifier(),
                "DecisiontreeClassifier"    : DecisionTreeClassifier(),
                # "VotingClassifier"          : VotingClassifier(e),
                "BaggingClassifier"         : BaggingClassifier(),
                "AdaBoositingClassifier"    : AdaBoostClassifier(),
                "GradientBoostingClassifier": GradientBoostingClassifier(),
                "RandomForest"              : RandomForestClassifier(),
                "xgboost"                   : XGBClassifier()
            }
            
            params = {

                # 1. Logistic Regression
                "LogisticRegression": {
                    "C": [0.001, 0.01, 0.1, 1, 10],
                    "penalty": ["l1", "l2"],
                    "solver": ["liblinear", "saga"],
                    "max_iter": [100, 200, 500]
                },
                # 2. Support Vector Machine
                "SupportVectorMachine": {
                    "C": [0.1, 1, 10],
                    "gamma": ["scale", "auto", 0.1, 0.01],
                    "kernel": ["linear", "rbf", "poly"],
                    "degree": [2, 3, 4]
                },
                # 3. K-Nearest Neighbors
                "KNeighborsClassifier": {
                    "n_neighbors": [3, 5, 7, 10, 15],
                    "weights": ["uniform", "distance"],
                    "algorithm": ["auto", "ball_tree", "kd_tree"],
                    "p": [1, 2]
                },
                # 4. Decision Tree
                "DecisiontreeClassifier": {
                    "criterion": ["gini", "entropy", "log_loss"],
                    "max_depth": [None, 3, 5, 10, 15, 20],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                    "max_features": [None, "sqrt", "log2"]
                },
                # 5. Bagging Classifier
                "BaggingClassifier": {
                    "n_estimators": [10, 50, 100],
                    "max_samples": [0.5, 0.7, 1.0],
                    "max_features": [0.5, 0.7, 1.0],
                    "bootstrap": [True, False],
                    "bootstrap_features": [True, False]
                },
                # 6. AdaBoost
                "AdaBoostingClassifier": {
                    "n_estimators": [50, 100, 200],
                    "learning_rate": [0.01, 0.1, 0.5, 1.0]
                },
                # 7. Gradient Boosting
                "GradientBoostingClassifier": {
                    "n_estimators": [50, 100, 200],
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "max_depth": [3, 5, 7],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                    "subsample": [0.8, 1.0]
                },
                # 8. Random Forest
                "RandomForest": {
                    "n_estimators": [50, 100, 200],
                    "criterion": ["gini", "entropy", "log_loss"],
                    "max_depth": [None, 5, 10, 20],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                    "max_features": ["sqrt", "log2", None],
                    "bootstrap": [True, False]
                },
                # 9. XGBoost
                "XGBoost": {
                    "n_estimators": [50, 100, 200],
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "max_depth": [3, 5, 7],
                    "min_child_weight": [1, 3, 5],
                    "subsample": [0.7, 0.8, 1.0],
                    "colsample_bytree": [0.7, 0.8, 1.0],
                    "gamma": [0, 0.1, 0.3],
                    "reg_alpha": [0, 0.01, 0.1],
                    "reg_lambda": [1, 1.5, 2]
                }
            }
            model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=X_test,y_test=y_test,
                                        models=models,param=params)
        
            ## To get best model score from dict
            best_model_score = max(sorted(model_report.values()))

            ## To get best model name from dict

            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]

            if best_model_score<0.6:
                raise CustomException("No best model found")
            logging.info(f"Best found model on both training and testing dataset")

            save_object(
                file_path=self.ModelTrainerConfig.train_model_file_path,
                obj=best_model
            ) 

            predicted=best_model.predict(X_test)

            accuracy = accuracy_score(y_test, predicted)
            return accuracy 
        except Exception as e:
                raise CustomException(e, sys)

if __name__ == "__main__":
    from src.components.data_ingestion import DataIngestion
    from src.components.data_transformation import DataTransformation

    obj = DataIngestion()
    train_data, test_data = obj.initate_data_ingestion()

    data_transformation = DataTransformation()
    train_arr, test_arr, _ = data_transformation.initiate_data_transfromation(
        train_data,
        test_data
    )

    model_trainer = ModelTrainer()

    accuracy = model_trainer.initiate_model_traineer(
        train_arr,
        test_arr
    )

    print("Model Accuracy:", accuracy)  