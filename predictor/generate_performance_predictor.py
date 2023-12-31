

## **Loading Data**

import pandas as pd
import numpy as np
import seaborn as sns
import pickle

# define input features
index = ["ProgId", "InputId", "ConfigId"]

mem_features = ["Mem_Latency", "L1_Sets", "L1_Latency",
                "L2_Sets","L2_Latency",]

program_features = ["L1_Hits_1Thread", "L1_Misses_1Thread", "L2_Hits_1Thread", "L3_Misses_1Thread", # "L2_Misses_1Thread", "L3_Hits_1Thread",
                    "Instructions_1Thread", "Instructions_2Thread", "BranchPredictionAccuracy_1Thread", "pThreads"]

input_features = mem_features + program_features

target = "SpeedUp"

# load data
data_path = "../sim_data/stats.csv"
data = pd.read_csv(data_path)

# check data types
print("Initial Data Columns:\n", data.dtypes)

#clean data to remove groups that don't have data for 2 threads

data = data[(data['ProgId']!=12) & (data['InputId']!=5)]
data = data[(data['ProgId']!=13) & (data['InputId']!=3)]

"""## **Calculate SpeedUp**
---
"""

# calculate speedup for each row
data["SpeedUp"] = data.groupby(index)['SimTime'].transform(lambda x: x / x[data['pThreads'] == 1].values[0])

data["L1_Hits_1Thread"] = data.groupby(index)['L1_Hits'].transform(lambda x: x[data['pThreads'] == 1].values[0])
data["L1_Misses_1Thread"] = data.groupby(index)['L1_Misses'].transform(lambda x: x[data['pThreads'] == 1].values[0])

data["L2_Hits_1Thread"] = data.groupby(index)['L2_Hits'].transform(lambda x: x[data['pThreads'] == 1].values[0])
data["L2_Misses_1Thread"] = data.groupby(index)['L2_Misses'].transform(lambda x: x[data['pThreads'] == 1].values[0])

data["L3_Hits_1Thread"] = data.groupby(index)['L3_Hits'].transform(lambda x: x[data['pThreads'] == 1].values[0])
data["L3_Misses_1Thread"] = data.groupby(index)['L3_Misses'].transform(lambda x: x[data['pThreads'] == 1].values[0])


data["Instructions_1Thread"] = data.groupby(index)['Instructions'].transform(lambda x: x[data['pThreads'] == 1].values[0])
data["Instructions_2Thread"] = data.groupby(index)['Instructions'].transform(lambda x: x[data['pThreads'] == 2].values[0])

data["BranchPredictionAccuracy_1Thread"] = data.groupby(index)['BranchPredictionAccuracy'].transform(lambda x: x[data['pThreads'] == 1].values[0])

# drop columns that are no longer needed
data = data[input_features + [target]]
#print(data.head(10))

"""## **Feature Selection**
---
"""

#exploring useful features through correlation matrix
# corr = data.corr()
# ax = sns.heatmap(
#     corr,
#     vmin=-1, vmax=1, center=0,
#     cmap=sns.diverging_palette(20, 220, n=200),
#     square=True
# )
# ax.set_xticklabels(
#     ax.get_xticklabels(),
#     rotation=45,
#     horizontalalignment='right'
# )

print("Final modelling attributes along with target variable:\n\n")
print(data.dtypes)

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, max_error, mean_absolute_error

"""## **Splitting the dataset for training and testing**
---
"""

#splitting into training and test sets
from sklearn.model_selection import train_test_split
#shuffle data
data = data.sample(frac = 1)
Y = data[target]
X = data.drop(columns=[target])

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=.20, random_state=39)

"""## **Exploring Linear Regression**
---
"""

# train the linear regression model
lr_model = LinearRegression()
lr_model.fit(X_train, Y_train)

# test the linear regression model
Y_pred = lr_model.predict(X_test)

# get maximum residual error
print("Test outcomes for linear regression:\n")
print("Maximum Residual Error: {}\n".format(max_error(Y_test, Y_pred)))

# get mean squared error
print("Mean Squared Error: {}\n".format(mean_squared_error(Y_test, Y_pred)))

# get mean absolute error
print("Mean Absolute Error: {}\n".format(mean_absolute_error(Y_test, Y_pred)))

#check accuracy percentage with absolute prediction error <0.5
absolute_error = abs(Y_test - Y_pred)
within_range_count = sum(absolute_error <= 0.5)
percentage_within_range = (within_range_count / len(Y_test)) * 100

print(f"Percentage of Y_pred values with prediction error within +0.5 to -0.5: {percentage_within_range:.2f}%\n")

# save the model to disk
filename = 'lr_model.sav'
pickle.dump(lr_model, open(filename, 'wb'))

"""## **Exploring Decision Tree Regression**
---
"""

# train the decesion tree regression model
dtr_model = DecisionTreeRegressor()
dtr_model.fit(X_train, Y_train)

# test the decesion tree regression model
Y_pred = dtr_model.predict(X_test)

# get maximum residual error
print("Test outcomes for decision tree regression:\n")
print("Maximum Residual Error: {}\n".format(max_error(Y_test, Y_pred)))

# get mean squared error
print("Mean Squared Error: {}\n".format(mean_squared_error(Y_test, Y_pred)))

# get mean absolute error
print("Mean Absolute Error: {}\n".format(mean_absolute_error(Y_test, Y_pred)))

#check accuracy percentage with absolute prediction error <0.5
absolute_error = abs(Y_test - Y_pred)
within_range_count = sum(absolute_error <= 0.5)
percentage_within_range = (within_range_count / len(Y_test)) * 100

print(f"Percentage of Y_pred values with prediction error within +0.5 to -0.5: {percentage_within_range:.2f}%\n")

# print("Feature Names in Decision Tree Model: \n", dtr_model.feature_names_in_)
# print("Feature Importance in Decision Tree Model: \n", dtr_model.feature_importances_)

# save the model to disk
filename = 'dtr_model.sav'
pickle.dump(dtr_model, open(filename, 'wb'))