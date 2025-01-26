import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from uuid import uuid4
class Summary:
    def start(self, data, basepath : os.PathLike | str, uuid : str):
        self.data = data
        self.basepath = basepath
        self.x = uuid
        self.paths : dict = {}
        self.data['Date'] = pd.to_datetime(self.data['Date'], format='%d/%m/%y')
        self.data['Quarter'] = self.data['Date'].dt.quarter
        self.data['Amount'] = self.data['Amount (INR)']

    def runner(self):
        self.Category_leader()
        self.Category_ascend_decend()
        self.Category_pay()
        self.Quarter_leader()
        self.Quarter_pay()
        self.Quarter_ascend_decend()
        self.Quarter_cat()

    def Category_leader(self):
        category_counts = self.data["Category"].value_counts()
        print(category_counts)
        # Unique Graph - Donut Chart
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90, 
               wedgeprops=dict(width=0.4, edgecolor='black'))
        ax.set_title("Category Counts")
        print()
        plt.savefig(f'{self.basepath}.Category_leader.png')  # Save the plot as an image
        self.paths.update({f"{self.x}-cat_leader" : f'{self.basepath}.Category_leader.png'})
        plt.close()

    def Category_ascend_decend(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Category").get_group(var)
        else:
            grpdata = self.data
        decend = grpdata.sort_values("Amount", ascending=True)
        print("Descending order:")
        print(decend[["Category", "Amount"]].head())
        
        ascend = grpdata.sort_values("Amount", ascending=False)
        print("Ascending order:")
        print(ascend[["Category", "Amount"]].head())
        
        # Unique Graph - Box Plot for Distribution
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(x="Category", y="Amount", data=decend, palette=["#6a0dad"])
        ax.set_title("Descending Amount by Category")
        plt.savefig(f'{self.basepath}.Category_ascend_decend_descend.png')
        self.paths.update({f"{self.x}-cat_asc_desc_desc" : '{self.basepath}.Category_ascend_decend_descend.png'})
        plt.close()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(x="Category", y="Amount", data=ascend, palette=["#3a3a3a"])
        ax.set_title("Ascending Amount by Category")
        plt.savefig(f'{self.basepath}.Category_ascend_decend_ascend.png')
        self.paths.update({f"{self.x}-cat_asc_desc_desc" : f'{self.basepath}.Category_ascend_decend_ascend.png'})
        plt.close()

    def Category_pay(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Category").get_group(var)
        else:
            grpdata = self.data
        category_payment_counts = grpdata["Payment Type"].value_counts()
        print(category_payment_counts)
        # Unique Graph - Bar Chart with Horizontal Orientation
        fig, ax = plt.subplots(figsize=(8, 6))
        category_payment_counts.plot(kind='barh', color="#6a0dad", ax=ax)
        ax.set_title("Payment Type Distribution by Category")
        ax.set_xlabel("Count")
        ax.set_ylabel("Payment Type")
        plt.savefig(f'{self.basepath}.Category_pay.png')
        self.paths.update({f"{self.x}-cat_pay" : f'{self.basepath}.Category_pay.png'})
        plt.close()

    def Quarter_leader(self):
        quarter_counts = self.data["Quarter"].value_counts()
        print(quarter_counts)
        # Unique Graph - Scatter Plot for Trend Analysis
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(quarter_counts.index, quarter_counts.values, color="#3a3a3a")
        ax.set_title("Quarter Counts")
        ax.set_xlabel("Quarter")
        ax.set_ylabel("Count")
        plt.savefig(f'{self.basepath}.Quarter_leader.png')
        self.paths.update({f"{self.x}-q_leader" : f'{self.basepath}.Quarter_leader.png'})
        plt.close()

    def Quarter_pay(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Quarter").get_group(var)
        else:
            grpdata = self.data
        quarter_payment_counts = grpdata["Payment Type"].value_counts()
        print(quarter_payment_counts)
        # Unique Graph - Bar Chart with Color Gradient
        fig, ax = plt.subplots(figsize=(8, 6))
        quarter_payment_counts.plot(kind='bar', color="#6a0dad", ax=ax)
        ax.set_title("Payment Type Distribution by Quarter")
        ax.set_xlabel("Payment Type")
        ax.set_ylabel("Count")
        plt.savefig(f'{self.basepath}.Quarter_pay.png')
        self.paths.update({f"{self.x}-q_pay" : f'{self.basepath}.Quarter_pay.png'})
        plt.close()

    def Quarter_ascend_decend(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Quarter").get_group(var)
        else:
            grpdata = self.data
        decend = grpdata.sort_values("Amount", ascending=True)
        print("Descending order:")
        print(decend[["Quarter", "Amount"]].head())
        
        ascend = grpdata.sort_values("Amount", ascending=False)
        print("Ascending order:")
        print(ascend[["Quarter", "Amount"]].head())
        
        # Unique Graph - Violin Plot
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.violinplot(x="Quarter", y="Amount", data=decend, color="#6a0dad", ax=ax)
        ax.set_title("Descending Amount by Quarter")
        plt.savefig(f'{self.basepath}.Quarter_ascend_decend_descend.png')
        plt.close()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.violinplot(x="Quarter", y="Amount", data=ascend, color="#3a3a3a", ax=ax)
        ax.set_title("Ascending Amount by Quarter")
        plt.savefig(f'{self.basepath}.Quarter_ascend_decend_ascend.png')
        plt.close()

    def Quarter_cat(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Quarter").get_group(var)
        else:
            grpdata = self.data
        quarter_category_counts = grpdata["Category"].value_counts()
        print(quarter_category_counts)
        # Unique Graph - Heatmap for Category Distribution
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap([quarter_category_counts.values], annot=True, fmt='d', cmap="Purples", 
                    xticklabels=quarter_category_counts.index, yticklabels=["Quarter"], ax=ax)
        ax.set_title("Category Distribution by Quarter")
        plt.savefig(f'{self.basepath}.Quarter_cat.png')
        self.paths.update({f"{self.x}-q_cat" : f'{self.basepath}.Quarter_cat.png'})
        plt.close()

    def save_all_graphs(self):
        
        self.Category_leader()
        self.Category_ascend_decend()
        self.Category_pay()
        self.Quarter_leader()
        self.Quarter_pay()
        self.Quarter_ascend_decend()
        self.Quarter_cat()
        print("All graphs saved in the 'graphs' folder.")