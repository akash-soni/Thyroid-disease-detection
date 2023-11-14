import os
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from kneed import KneeLocator
import matplotlib.pyplot as plt
import typing as typing
from thyroid.logging import logger
from thyroid.utils.exception import customException
from thyroid.entity.config_entity import ClusteringConfig
import pandas as pd

class DataClustering:
    """
            This class shall  be used to divide the data into clusters before training.

            Written By: akash
            Version: 1.0
            Revisions: None

            """
    def __init__(self, data, config: ClusteringConfig):
        self.config = config
        self.data = data
        self.Y = self.data['class']
        self.X = self.data.drop(columns=['class'])
        
        
    def plot_knee(self):
        """_summary_
        
        Input: dataframe
        
        Returns:
            _type_: kmeans plot
        """
        # scaler = StandardScaler()
        # self.X_scaled = scaler.fit_transform(self.X)
        wcss=[]
        for i in range (1,11):
            kmeans=KMeans(n_clusters=i,init='k-means++',random_state=42) # initializing the KMeans object
            kmeans.fit(self.X) # fitting the data to the KMeans Algorithm
            wcss.append(kmeans.inertia_)
        plt.plot(range(1,11),wcss) # creating the graph between WCSS and the number of clusters
        plt.title('The Elbow Method')
        plt.xlabel('Number of clusters')
        plt.ylabel('WCSS')
        #plt.show()
        plt.savefig(os.path.join(self.config.plot_dir, self.config.cluster_plot)) # saving the elbow plot locally
        # finding the value of the optimum cluster programmatically
        kn = KneeLocator(range(1, 11), wcss, curve='convex', direction='decreasing')
        logger.info('The optimum number of clusters is: '+str(kn.knee)+' . Exited the elbow_plot method of the KMeansClustering class')
        return kn.knee

    def create_clusters(self, optimal_k):
        kmeans = KMeans(n_clusters=optimal_k, init='k-means++', random_state=42)
        
        self.X['cluster']=kmeans.fit_predict(self.X) #  divide data into clusters

        with open(os.path.join(self.config.cluster_model_dir, self.config.cluster_model), 'wb') as file:
            pickle.dump(kmeans, file) # saving the KMeans model to directory                                                                  
        logger.info('succesfully created ' +str(optimal_k)+ 'clusters. Exited the create_clusters method of the KMeansClustering class')

        # save the data
        self.X['class'] = self.Y
        self.X.to_csv(os.path.join(self.config.clustered_dir, self.config.clustering_file), index=False)
        logger.info(f"file saved as {self.config.clustering_file}")
