#!/usr/bin/env python
# coding: utf-8

# In[1]:
import pandas as pd
# In[2]:

# In[3]:


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class Summary:
    def start(self, data):
        self.data = data
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
        fig = go.Figure(data=[go.Pie(labels=category_counts.index, values=category_counts.values, hole=0.3)])
        fig.update_traces(marker=dict(colors=["#6a0dad", "#3a3a3a"]))  # Purple and Black
        fig.update_layout(title="Category Counts", template="plotly_dark")
        fig.show()

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
        fig_descend = px.box(decend, x="Category", y="Amount", 
                             title="Descending Amount by Category", 
                             labels={"Category": "Category", "Amount": "Amount"}, 
                             template="plotly_dark")
        fig_descend.update_traces(marker=dict(color="#6a0dad"))  # Purple color
        fig_descend.show()
        
        fig_ascend = px.box(ascend, x="Category", y="Amount", 
                            title="Ascending Amount by Category", 
                            labels={"Category": "Category", "Amount": "Amount"}, 
                            template="plotly_dark")
        fig_ascend.update_traces(marker=dict(color="#3a3a3a"))  # Black color
        fig_ascend.show()

    def Category_pay(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Category").get_group(var)
        else:
            grpdata = self.data
        category_payment_counts = grpdata["Payment Type"].value_counts()
        print(category_payment_counts)
        # Unique Graph - Bar Chart with Horizontal Orientation
        fig = px.bar(category_payment_counts, x=category_payment_counts.values, y=category_payment_counts.index, 
                     orientation='h', title="Payment Type Distribution by Category", 
                     labels={"x": "Count", "y": "Payment Type"}, template="plotly_dark")
        fig.update_traces(marker=dict(color="#6a0dad"))  # Purple color
        fig.show()

    def Quarter_leader(self):
        quarter_counts = self.data["Quarter"].value_counts()
        print(quarter_counts)
        # Unique Graph - Scatter Plot for Trend Analysis
        fig = px.scatter(x=quarter_counts.index, y=quarter_counts.values, 
                         title="Quarter Counts", labels={"x": "Quarter", "y": "Count"}, template="plotly_dark")
        fig.update_traces(marker=dict(color="#3a3a3a"))  # Black color
        fig.show()

    def Quarter_pay(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Quarter").get_group(var)
        else:
            grpdata = self.data
        quarter_payment_counts = grpdata["Payment Type"].value_counts()
        print(quarter_payment_counts)
        # Unique Graph - Bar Chart with Color Gradient
        fig = px.bar(quarter_payment_counts, x=quarter_payment_counts.index, y=quarter_payment_counts.values, 
                     title="Payment Type Distribution by Quarter", 
                     labels={"x": "Payment Type", "y": "Count"}, template="plotly_dark")
        fig.update_traces(marker=dict(color="#6a0dad"))  # Purple color
        fig.show()

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
        fig_descend = px.violin(decend, x="Quarter", y="Amount", box=True, 
                               title="Descending Amount by Quarter", 
                               labels={"Quarter": "Quarter", "Amount": "Amount"}, template="plotly_dark")
        fig_descend.update_traces(marker=dict(color="#6a0dad"))  # Purple color
        fig_descend.show()
        
        fig_ascend = px.violin(ascend, x="Quarter", y="Amount", box=True, 
                               title="Ascending Amount by Quarter", 
                               labels={"Quarter": "Quarter", "Amount": "Amount"}, template="plotly_dark")
        fig_ascend.update_traces(marker=dict(color="#3a3a3a"))  # Black color
        fig_ascend.show()

    def Quarter_cat(self, var=None):
        if var is not None:
            grpdata = self.data.groupby("Quarter").get_group(var)
        else:
            grpdata = self.data
        quarter_category_counts = grpdata["Category"].value_counts()
        print(quarter_category_counts)
        # Unique Graph - Heatmap for Category Distribution
        fig = px.imshow([quarter_category_counts.values], 
                        labels=dict(x="Category", y="Quarter", color="Count"),
                        title="Category Distribution by Quarter", 
                        template="plotly_dark")
        fig.update_traces(colorscale="Purples")  # Purple color scale
        fig.show()


# In[4

# In[5]:

# In[6]

# In[ ]:




