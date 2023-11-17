import os
import pandas as pd
import numpy as np
import pickle
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder
from collections import Counter
import typing as typing
from sklearn.impute import KNNImputer
from thyroid.utils.exception import customException
from thyroid.logging import logger
from thyroid.entity.config_entity import DataTransformationConfig
from thyroid.components.clustering import DataClustering
from pathlib import Path
from thyroid.config.configuration import ConfigurationManager


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def convert_to_numerics(self,df):
        df[self.config.numerical_columns] = df[self.config.numerical_columns].apply(pd.to_numeric, errors='coerce')
        return(df)

    def case_normalization(self):
        """
        Method: this method will normalize all values to small case, will convert 'y' to 't' and 'n' to 'f'
        , it will replace '?' with nan and will convert columns to numerics
        Input: dataframe
        Outputs: normalized dataframe
        """


        file_path = self.config.merged_file
        df = pd.read_csv(os.path.join(self.config.validation_dir,file_path))

        # Convert all object columns to lowercase
        df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)

        # Replace '?' with NaN
        df.replace('?', np.nan, inplace=True)

        # Replace 'y' with 't' and 'n' with 'f'
        df.replace({'y': 't', 'n': 'f'}, inplace=True)

        for column in self.config.categorical_columns:
            df[column].replace({'0': 'f', '1': 't'}, inplace=True)

        # convert "age","TSH","T3","TT4","T4U","FTI" to numeric
        df = self.convert_to_numerics(df)

        return(df)
    

    def impute_column(self,column):
        imputer = KNNImputer(n_neighbors=3, weights="uniform", missing_values=np.nan) 
        imputed_values = imputer.fit_transform(column.values.reshape(-1, 1))
        
        return np.round(imputed_values, 2)

    def handle_missing_values(self, df):
        """
        Method: This method will eliminate columns with more than 30% missing values, handle missing values and drop unnecessary columns   
        Inputs: data frame with missing values
        Output: data frame with no missing values and useless columns
        """
        # Drop columns with more missing values than the threshold
        logger.info("Drop columns with more missing values than the threshold = {self.config.threshold}")
        column_threshold = int(self.config.threshold * len(df))
        df = df.dropna(axis=1, thresh=column_threshold)

        # Impute missing values 
        logger.info("Impute missing values in numerical column")
        columns_to_impute = self.config.numerical_columns[1:]
        for column in columns_to_impute:
            df[column] = self.impute_column(df[column]) 

        # Mode Impute missing values for remaining categorical columns 
        logger.info("Impute other columns missing values using mode")
        mode_columns = ['hypopituitary', 'I131_treatment', 'psych','sex']
        for column in mode_columns:
            mode_value = df[column].mode()[0]  # Get the mode value of the column
            df[column].fillna(mode_value, inplace=True)


        # median_imputation for age column
        logger.info("Impute age column using median")
        median_value = df['age'].median()  # Calculate the median value of the age column
        df['age'].fillna(median_value, inplace=True)

        # drop the measured columns
        df.drop(columns=self.config.drop_columns, inplace=True)

        return (df)
    

    def calculate_age_iqr(self,df):
        """_summary_

        Args:
            df (_type_): _description_

        Returns:
            _type_: _description_
        """

        logger.info("removing outliers from age column")
        age = self.config.numerical_columns[0]
        # Calculate IQR for the 'age' column
        Q1 = df[age].quantile(0.25)
        Q3 = df[age].quantile(0.75)
        IQR = Q3 - Q1

        # Define the upper and lower bounds for outlier removal
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Remove outliers from the 'age' column
        df = df[(df['age'] >= lower_bound) & (df['age'] <= upper_bound)]

        return (df)

    def calculate_z_score(self,df):
        # Define a threshold for identifying outliers (e.g., Z-score > 2)
        logger.info("removing outliers using z-score")
        # Iterate over the columns and remove outliers
        non_outliers_data_frame = df.copy()  # Create a copy to store non-outliers
        for column in self.config.numerical_columns[1:]:
            z_scores = np.abs((non_outliers_data_frame[column] - non_outliers_data_frame[column].mean()) / non_outliers_data_frame[column].std())
            non_outliers_data_frame = non_outliers_data_frame[(z_scores <= self.config.z_threshold)]

        return non_outliers_data_frame

    def no_duplicates_and_binary_convert(self, df):
        # map sex column values to 0 and 1
        logger.info("converting sex column -> 'f' to 0 and 'm' to 1")
        sex = self.config.categorical_columns_to_convert[0]
        df[sex] = df[sex].map({'f': 0, 'm': 1})

        # map all othere categorical function to 0 and 1
        logger.info("mapping 'f' to 0 and 't' to 1")
        for column in self.config.categorical_columns_to_convert[1:]:
            if len(df[column].unique()) == 2:
                df[column] = df[column].map({'f': 0, 't': 1})


        # remove duplicate rows
        df = df.drop_duplicates()
        logger.info("duplicate rows removed")

        return(df)


    def outlier_removal(self,df):
        """_summary_ 
        Method:
            remove outliers from numerical columns
        Args:
            df (_type_): _description_
        """
        logger.info("Outliers removal started")
        # compute IQR on age column to remove outliers
        df = self.calculate_age_iqr(df)
        logger.info("IQR on age column completed")
        # compute Z-score on remaining numerical columns to remove outliers
        df = self.calculate_z_score(df)
        logger.info("Z-score on remaining numerical columns")
        df = self.no_duplicates_and_binary_convert(df)
        logger.info("remvoed duplicates and converted to binary")

        return df
        
    def imbalance_handling(self, df):
        """_summary_

        Args:
            df (_type_): imbalanced data frame

        Returns:
            _type_: dataframe with balanced data points
        """
        X = df.drop(columns=['class'])
        y = df['class']

        prev_count = Counter(y)
        logger.info("Class distribution before SMOTE: {prev_count}")

        smote = SMOTE(sampling_strategy='auto', random_state=42)

        X_resampled, y_resampled = smote.fit_resample(X, y)

        resampled_count = Counter(y_resampled)
        logger.info("Class distribution after SMOTE: {resampled_count})} ")

        resampled_data = pd.concat([X_resampled, y_resampled], axis=1)
        
        return resampled_data
    
    
    def labelencoding_and_save(self, df):
        encode = LabelEncoder().fit(df['class'])

        df['class'] = encode.transform(df['class'])


        # we will save the encoder as pickle to use when we do the prediction. We will need to decode the predcited values
        # back to original
        with open(os.path.join(self.config.encoding_dir, self.config.encoder_file), 'wb') as file:
            pickle.dump(encode, file)
        logger.info("label encoding successfull")

        # save the data
        df.to_csv(os.path.join(self.config.data_dir, self.config.data_file), index=False)
        logger.info(f"file saved as {self.config.data_file}")

        
        return df
    
    def get_clustered_data(self,df):
        config = ConfigurationManager()
        data_clustering_config = config.get_data_clustering_config()
        data_clustering = DataClustering(df,config=data_clustering_config)
        optimal_clusters = data_clustering.plot_knee()
        data_clustering.create_clusters(optimal_clusters)
        
