import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
import seaborn as sns
import os

class ClusterAnalysis:
    def __init__(self, df,basepath : os.PathLike | str, uuid : str):
        self.df = df
        self.basepath = basepath
        self.x = uuid
        self.paths : dict = {}
        self.df['Amount'] = self.df['Amount (INR)']
        self.encoder = LabelEncoder()
        self.scaler = StandardScaler()

    def preprocess_data(self):
        # Encode categorical columns
        self.df['Payment Type'] = self.encoder.fit_transform(self.df['Payment Type'])
        self.df['Category'] = self.encoder.fit_transform(self.df['Category'])

    def apply_kmeans(self, n_clusters=3):
        # Selecting relevant features for clustering
        features = ['Payment Type', 'Category', 'Amount']
        X = self.df[features]

        # Standardizing the features
        X_scaled = self.scaler.fit_transform(X)

        # Apply K-Means Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.df['Cluster'] = kmeans.fit_predict(X_scaled)

    def plot_violinplot(self):
        # Violin plot to show the distribution of 'Amount' by 'Category' and 'Payment Type'
        plt.figure(figsize=(12, 6))

        # Violin plot for 'Amount' by 'Category'
        plt.subplot(1, 2, 1)
        sns.violinplot(x='Category', y='Amount', data=self.df, palette='Purples')
        plt.title('Amount by Category')
        plt.xlabel('Category')
        plt.ylabel('Amount')

        # Violin plot for 'Amount' by 'Payment Type'
        plt.subplot(1, 2, 2)
        sns.violinplot(x='Payment Type', y='Amount', data=self.df, palette='Blues')
        plt.title('Amount by Payment Type')
        plt.xlabel('Payment Type')
        plt.ylabel('Amount')

        plt.suptitle('Violin Plot of Spending Distribution by Category and Payment Type')
        plt.tight_layout()

        print()
        plt.savefig(f'{self.basepath}.voilin.png')  # Save the plot as an image
        self.paths.update({f"{self.x}-spend_voilin" : f'{self.basepath}.voilin.png'})
        plt.close()
        
    def plot_heatmap(self):
        # Heatmap to show the correlation between features
        plt.figure(figsize=(8, 6))

        # Calculate the correlation matrix
        correlation_matrix = self.df[['Payment Type', 'Category', 'Amount', 'Cluster']].corr()

        # Create a heatmap of the correlation matrix
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt='.2f', center=0)
        
        plt.title('Correlation Heatmap of Features and Clusters')

        print()
        plt.savefig(f'{self.basepath}.heatmap.png')  # Save the plot as an image
        self.paths.update({f"{self.x}-spend_heat" : f'{self.basepath}.heatmap.png'})
        plt.close()

    def run(self):
        self.preprocess_data()
        self.apply_kmeans(n_clusters=3)
        self.plot_violinplot()
        self.plot_heatmap()
