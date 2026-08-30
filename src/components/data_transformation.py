import sys
from dataclasses import dataclass


import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

from src.logger import logging
from src.exception import CustomException
import os


from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path:str = os.path.join("artifacts","preprocessor.pkl")
    

class DataTransformation:
    def __init__(self):
        self.data_transformation = DataTransformationConfig()
        
    def get_data_transformer_object(self):
        '''
        This function is responsible for data transformation
        
        '''
        try:
            numerical_features = [
                'age', 
                'income', 
                'browsing_time',
                'pages_viewed',
                'previous_purchases'
            ]
            categorical_featues = [
                'gender',
                'product_category',
                'discount_used'
            ]
            
            num_pipe = Pipeline(
                steps=[
                    ('impute',SimpleImputer(strategy='mean')),
                    ('scaler',StandardScaler())
                ]
            )
            
            cat_pipe = Pipeline(
                steps=[
                    ('impute',SimpleImputer(strategy='most_frequent')),
                    ('OneHotEncoder',OneHotEncoder()),
                    ('scler',StandardScaler(with_mean=False))
                ]
            )
            
            logging.info(f"Numerical columns:   {numerical_features}")
            logging.info(f"Categorical columns: {categorical_featues}")
            
            
            preprocessor = ColumnTransformer(
                [
                    ("num_pipeline",num_pipe,numerical_features),
                    ("cat_pipeline",cat_pipe,categorical_featues)
                ]
            )
            
            return preprocessor
        except Exception as e:
           raise CustomException(e, sys)
    
    def initiate_data_transfromation(self,train_path,test_path):
        
        try:
            train_df = pd.read_csv(train_path)
            test_df  = pd.read_csv(test_path)
            
            logging.info("Reading train data and test data is completed")
            
            
            logging.info("Obtaining preprocessor object")
            
            preprocessor_obj = self.get_data_transformer_object()
            
            target_columns_name = "purchased"
            
            input_feature_train_df = train_df.drop(columns=[target_columns_name])
            target_feature_train_df = train_df[target_columns_name]
            
            input_feature_test_df = test_df.drop(columns=[target_columns_name])
            target_feature_test_df = test_df[target_columns_name]
            
            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            
            
            input_feature_train_arr = preprocessor_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr  = preprocessor_obj.transform(input_feature_test_df)
            
            train_arr = np.c_[
                input_feature_train_arr, np.array(target_feature_train_df)
            ]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info(f"Saved preprocessing object.")
            
            save_object(
                file_path = self.data_transformation.preprocessor_obj_file_path,
                obj=preprocessor_obj
            )
            
            return (
                train_arr,
                test_arr,
                self.data_transformation.preprocessor_obj_file_path
            )
        except Exception as e:
            raise CustomException(e, sys)