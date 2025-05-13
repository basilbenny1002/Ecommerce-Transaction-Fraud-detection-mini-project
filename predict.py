import pickle
import numpy as np

data = [181.00,          181.0,            0.00,             0.0,             0.0,                       0,          False,       False,         False,           True]
# Load the model
with open("model.pkl", "rb") as file:
    loaded_model = pickle.load(file)

# Example input data
input_data = np.array([data])

# Make predictions
predictions = loaded_model.predict(input_data,)

# Print the predictions
print(predictions)