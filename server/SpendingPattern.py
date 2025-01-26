#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[30]:
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
import plotly.graph_objects as go

class ClusterAnalysis:
    def __init__(self, df):
        self.df = df
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

    def plot_boxplot(self):
        # Box plot of 'Amount' by 'Category' and 'Payment Type'
        fig = go.Figure()

        # Create a box plot for 'Amount' by 'Category'
        fig.add_trace(go.Box(
            y=self.df['Amount'],
            x=self.df['Category'],
            name='Category',
            marker_color='#6a0dad',  # Purple color
            boxmean='sd'
        ))

        # Create a box plot for 'Amount' by 'Payment Type'
        fig.add_trace(go.Box(
            y=self.df['Amount'],
            x=self.df['Payment Type'],
            name='Payment Type',
            marker_color='#3a3a3a',  # Dark grey color for Payment Type
            boxmean='sd'
        ))

        fig.update_layout(
            title='Box Plot of Spending Distribution by Category and Payment Type',
            xaxis=dict(title='Category / Payment Type'),
            yaxis=dict(title='Amount'),
            template="plotly_dark"
        )

        fig.show()
    def plot_scatter_with_regions(self):
        # Create a scatter plot for clusters
        fig = go.Figure()

        # Scatter plot points for each cluster
        fig.add_trace(go.Scatter(
            x=self.df['Payment Type'],
            y=self.df['Category'],
            mode='markers',
            marker=dict(
                color=self.df['Cluster'],
                colorscale='Purples',
                size=10,
                opacity=0.7
            ),
            text=self.df['Amount'],
            name='Clustered Points',  # Proper legend label for points
            showlegend=True  # Ensure this trace shows in the legend
        ))

        # Highlight regions based on clusters (using polygons)
        cluster_regions = {
            0: {'x': [0, 1, 1, 0], 'y': [0, 0, 1, 1], 'color': 'rgba(106, 13, 173, 0.2)', 'name': 'Cluster 0 Region'},
            1: {'x': [1, 2, 2, 1], 'y': [0, 0, 1, 1], 'color': 'rgba(58, 58, 58, 0.2)', 'name': 'Cluster 1 Region'},
            2: {'x': [2, 3, 3, 2], 'y': [0, 0, 1, 1], 'color': 'rgba(103, 58, 183, 0.2)', 'name': 'Cluster 2 Region'}
        }

        # Add shaded regions for each cluster with proper legends
        for cluster, region in cluster_regions.items():
            fig.add_trace(go.Scatter(
                x=region['x'],
                y=region['y'],
                fill='toself',
                fillcolor=region['color'],
                line=dict(color='rgba(255,255,255,0)'),
                name=region['name'],  # Proper legend label for regions
                showlegend=True  # Ensure this trace shows in the legend
            ))

        # Update layout and axes
        fig.update_layout(
            title='Scatter Plot with Clusters and Regions Highlighted',
            xaxis=dict(title='Payment Type'),
            yaxis=dict(title='Category'),
            template="plotly_dark",
            showlegend=True  # Show the legend in the plot
        )

        fig.show()


# In[31]:

# In[32]:
# In[ ]:




