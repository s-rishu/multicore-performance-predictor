import yaml
import pickle
import pandas as pd

#load predictors
#linear regression predictor
lr_filename = "lr_model.sav"
lr_model = pickle.load(open(lr_filename, 'rb'))

#decision tree predictor
dtr_filename = "dtr_model.sav"
dtr_model = pickle.load(open(dtr_filename, 'rb'))

#load input test file
input_filename = "test_input.yml"
input = open(input_filename, "r")
input_dict = yaml.load(input,Loader=yaml.Loader)
input_df = pd.DataFrame.from_dict(input_dict)
#print("Input Data:\n", input_df)

#predict speedup
#uncomment to use linear regression
#print("The predicted relative speedup wrt 1 thread using linear regression is :{}.\n".format(lr_model.predict(input_df)))
print("The predicted relative speedup wrt 1 thread using decision tree regression is :{}.\n".format(dtr_model.predict(input_df)))