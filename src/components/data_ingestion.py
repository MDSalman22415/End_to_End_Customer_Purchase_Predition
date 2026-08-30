import sys
import os
from src.logger import logging
from src.exception import CustomException
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
import pandas as pd

from src.components.data_transformation import DataTransformationConfig
from src.components.data_transformation import DataTransformation

from src.components.Model_trainer import ModelTrainerConfig
from src.components.Model_trainer import ModelTrainer


@dataclass
class DataIngentionConfig:
    train_data_path: str = os.path.join('artifacts',"train.csv")
    test_data_path:  str = os.path.join('artifacts',"test.csv")
    row_data_path:   str = os.path.join('artifacts',"row.csv")
    
class DataIngestion:
    def __init__(self):
        self.ingention_config = DataIngentionConfig()
    
    def initate_data_ingestion(self):
        logging.info("Entered the data ingestion methos or component")
        
        try:
            df = pd.read_csv("data/Analysis.csv")
            
            logging.info("Read the dataset as dataframe")
            
            os.makedirs(os.path.dirname(self.ingention_config.test_data_path),exist_ok=True)
            
            logging.info("artifactes folder is creted")
            
            df.to_csv(self.ingention_config.row_data_path,index=False,header=True)
            
            logging.info("Row data file is save in artifates folder")
            
            logging.info("Train test split is initiated")
            
            train_set, test_set = train_test_split(df,test_size=0.2,random_state=42)
            
            train_set.to_csv(
                self.ingention_config.train_data_path,
                index=False,
                header=True
            )
            
            test_set.to_csv(
                self.ingention_config.test_data_path,
                index=False,
                header=True
            )
            
            
            
            
            logging.info("Train test split is comleted")
            
            logging.info("Ingestion of the data is completed")
            
            
            return (
                self.ingention_config.train_data_path,
                self.ingention_config.test_data_path
            )
            
        except Exception as e:
            raise CustomException(sys, e)
        
if __name__ == "__main__":
    print("MAIN BLOCK STARTED")

    obj = DataIngestion()
    print("Data ingestion object created")

    train_data, test_data = obj.initate_data_ingestion()
    print("Data ingestion completed")

    data_trainformation = DataTransformation()
    print("Data transformation object created")

    train_arr, test_arr, _ = data_trainformation.initiate_data_transfromation(
        train_data, test_data
    )
    print("Data transformation completed")

    model_trainer = ModelTrainer()
    print("Model trainer object created")

    result = model_trainer.initiate_model_traineer(
        train_arr,
        test_arr
    )

    print("Training completed")
    print(result)