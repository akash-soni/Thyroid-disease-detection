import os
import pandas as pd
import shutil
import re
from thyroid.logging import logger
from thyroid.entity.config_entity import DataValidationConfig
from pathlib import Path

class DataValidation:
    def __init__(self, config: DataValidationConfig):
        self.config = config



    def remove_extrafiles(self):
        """remove all extra files and subdirectories which are not needed"""
        for root, dirs, files in os.walk(self.config.ingestion_dir):
            print(files,dirs)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                shutil.rmtree(dir_path)
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                if not any(file_name.startswith(name) for name in self.config.ALL_REQUIRED_FILES):
                    os.remove(file_path)


    def process_row(self, record):
        cleaned_attributes = []
        rows = record.strip().split('\n')  # Split input into rows
        for attribute in record.strip().split(','):
            attribute = re.sub(r'-', 'negative', attribute)  # Replace '-' with 'negative'
            if '.|' in attribute:
                cleaned_attributes.append(attribute.split('.|')[0])
            elif '[' in attribute:
                cleaned_attributes.append(attribute.split('[')[0])
            else:
                cleaned_attributes.append(attribute)
        return cleaned_attributes

    def remove_ids_from_all_data(self,data) -> list:
        """ remove all ids from data set"""
        id_removed_data = []
        if data:
            for row in data:
                id_removed_data.append(self.process_row(row))
        return(id_removed_data)





    def read_data_file(self, file_path):
        #if file_path.lower().endswith('.data' or '.test'):
        try:
            with open(file_path, 'r') as file:
                data = file.readlines()
                print("read_data_file")
                return data
            
        except FileNotFoundError:
            return "File not found."
        except Exception as e:
            return "An error occurred: " + str(e)
        else:
            # if the file does not end with .data
            return False


    def apply_columns_and_labels(self, data, data_type:str):
        """ add columns names and convert label names to hyper or hypothyroid"""
 

        # label names
        # Replacing values in the 'class' column
        if(data_type == "all"):

            # add column names
       
            all_df = pd.DataFrame(data, columns=self.config.columns)

            all_df['class'] = all_df['class'].replace(['goitre', 'T3 toxic', 'hyperthyroid', 'secondary toxic'], 'hyperthyroid')
            all_df['class'] = all_df['class'].replace(['primary hypothyroid', 'compensated hypothyroid', 'secondary hypothyroid'], 'hypothyroid')
        
            return(all_df)

        if(data_type == "thyroid_data"):

            # add column names
       
            thyroid_df = pd.DataFrame(data, columns=self.config.columns)

            thyroid_df['class'].replace(['A','AK','B','C','C|I','D','D|R'],"hyperthyroid",inplace = True)
            thyroid_df['class'].replace(['E','F','FK','G','GK','H','H|K'],"hypothyroid",inplace = True)

            for value in set(thyroid_df['class']):
                if(value != 'hypothyroid' and value != 'hyperthyroid'):
                    thyroid_df['class'].replace(value,'negative',inplace=True)
            return(thyroid_df)

    def get_files(self, name:str)->list:
        # read the "all" types data files
        files = os.listdir(self.config.ingestion_dir)
        all_rows = []
        for file in files:
            if (file.startswith(name)) and (file.endswith(('.data', '.test'))):
                file_path = os.path.join(self.config.ingestion_dir, file)
                data_rows = self.read_data_file(file_path)
                logger.info(f"read file {file}") 
                all_rows.extend(data_rows)
        logger.info(f"combined data from all the above files")
        return(all_rows)

    def combine_all_data_files(self):
        logger.info("Working on all data files [allhyper.data,allhyper.test,allhypo.data,allhypo.test]")
        all_rows = self.get_files("all")

        # remove IDs 
        no_ids_rows = self.remove_ids_from_all_data(all_rows)
        logger.info(f"patient IDS from the above combined data")

        # apply column labels and converting class name  to hyperthyroid or hypothyroid
        all_df = self.apply_columns_and_labels(no_ids_rows, "all")
        logger.info(f"applied column labels and converted class name to hyperthyroid or hypothyroid")

        # save the data
        all_df.to_csv(os.path.join(self.config.root_dir, "all-hyper-hypo.csv"), index=False)
        logger.info(f"file saved as all-hyper-hypo.csv")




    def validate_thyroid0378_file(self):
        logger.info("Working on all data files thyroid0378.data")
        all_rows = self.get_files("thyroid0387")

        # remove IDs 
        no_ids_rows = self.remove_ids_from_all_data(all_rows)
        logger.info(f"patient IDS from the above combined data")

        # apply column labels and converting class name  to hyperthyroid or hypothyroid
        all_df = self.apply_columns_and_labels(no_ids_rows, "thyroid_data")
        logger.info(f"applied column labels and converted class name to hyperthyroid or hypothyroid")

        # save the data
        all_df.to_csv(os.path.join(self.config.root_dir, "thyroid0387.csv"), index=False)
        logger.info(f"file saved as thyroid0387.csv")


    def get_columns_from_names_files(self, file_name: str):
        files = os.listdir(self.config.ingestion_dir)
        for file in files:
            if (file.startswith(file_name)) and (file.endswith(('.names'))):
                with open(os.path.join(self.config.ingestion_dir, file), 'r') as name_file:
                    columns = [line.split(':')[0].strip() for line in name_file.readlines()]
        
        data_columns = columns[2:-1] # get column names from 2nd position to last column name
        return data_columns


    def validate_hypothyroid_file(self):
        logger.info("Working on hypothyroid.data")
        all_rows = self.get_files("hypothyroid")
        
        # split data on commas
        data_list = [item.strip().split(',') for item in all_rows]
        
        # get column names
        columns = self.get_columns_from_names_files("hypothyroid")
        columns.insert(0, 'class') # insert class name at 0th index
        logger.info(f"Obtained column names from hypothyroid.names")

        hypothyroid_df = pd.DataFrame(data_list, columns=columns)

        # save the data
        hypothyroid_df.to_csv(os.path.join(self.config.root_dir, "hypothyroid.csv"), index=False)
        logger.info(f"file saved as hypothyroid.csv")

    def validate_euthyroid_file(self):
        logger.info("Working on sick-euthyroid.data")
        all_rows = self.get_files("sick-euthyroid")
        
        # split data on commas
        data_list = [item.strip().split(',') for item in all_rows]

        # get column names
        columns = self.get_columns_from_names_files("sick-euthyroid")
        columns.insert(0, 'class') # insert class name at 0th index
        logger.info(f"Obtained column names from sick-euthyroid.names")

        sick_eu_df = pd.DataFrame(data_list, columns=columns)
        negative_records = sick_eu_df[sick_eu_df['class'] == 'negative']

        # save the data
        negative_records.to_csv(os.path.join(self.config.root_dir, "euthyroid-neegative.csv"), index=False)
        logger.info(f"file saved as euthyroid-neegative.csv")


    def fillNewAttributes(self,row,attribute):
        if row[attribute] > 0:
            return 't'
        else:
            return 'f'
    
    def update_ann(self, ann_df):
        ann_df = ann_df.apply(pd.to_numeric, errors='coerce')

        # map all continuous attributes in multiple of 100
        continuos_attributes = ['age','TSH','T3','TT4','T4U','FTI']
        ann_df[continuos_attributes] = ann_df[continuos_attributes] * 100

        ann_df['sex'] = ann_df['sex'].map({0:'f',1:'m'})
        ann_df['class'] = ann_df['class'].map({3:'negative',2:'hypothyroid',1:'hyperthyroid'})

        ann_df['TSH_measured'] = ann_df.apply(lambda row: self.fillNewAttributes(row,'TSH'), axis=1)
        ann_df['T3_measured'] = ann_df.apply(lambda row: self.fillNewAttributes(row,'T3'), axis=1)
        ann_df['TT4_measured'] = ann_df.apply(lambda row: self.fillNewAttributes(row,'TT4'), axis=1)
        ann_df['T4U_measured'] = ann_df.apply(lambda row: self.fillNewAttributes(row,'T4U'), axis=1)
        ann_df['FTI_measured'] = ann_df.apply(lambda row: self.fillNewAttributes(row,'FTI'), axis=1)

        return ann_df

    def validate_ann_file(self):
        logger.info("Working on ann-train.data and ann0-test.data")
        all_rows = self.get_files("ann")

        data_list = [record.strip().split() for record in all_rows]
        ann_df = pd.DataFrame(data_list, columns=self.config.ann_columns)
        logger.info(f"Appended column names from ann")

        ann_df = self.update_ann(ann_df)
        logger.info(f"Ann dataset created")

        # save the data
        ann_df.to_csv(os.path.join(self.config.root_dir, "ann-data.csv"), index=False)
        logger.info(f"file saved as ann-data.csv")


    def merge_data(self):
        file_list = os.listdir(self.config.root_dir)


        # Create an empty list to store dataframes
        dataframes = []

        logger.info("Merging all dataframes")
        # Iterate through the files
        for file_name in file_list:
            # Check if the file is a CSV file
            if file_name.endswith('.csv'):
                # Create the full file path
                file_path = os.path.join(self.config.root_dir, file_name)
                
                # Read the CSV file into a pandas dataframe
                df = pd.read_csv(file_path)
                dataframes.append(df)
        # Concatenate all dataframes
        concatenated_df = pd.concat(dataframes, axis=0)


        # save the data
        concatenated_df.to_csv(os.path.join(self.config.root_dir, "merged-data.csv"), index=False)
        logger.info(f"file saved as merged-data.csv")