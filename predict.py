import pickle
import numpy as np
import cupy as cp

DEVICE = 'cuda'  # or 'cpu'
def predict(data: list):
    with open("model.pkl", "rb") as file:
        loaded_model = pickle.load(file)

    if DEVICE == 'cuda':
        input_data = cp.array([data])
        predictions = loaded_model.predict(input_data)

        predictions = (predictions > 0.5).astype(int)
    else:
        input_data = np.array([data])
        predictions = loaded_model.predict(input_data)

    return predictions[0]
if __name__ == '__main__':
    data = [181.00, 181.0, 0.00, 0.0, 0.0, 0, False, False, False, True]
    print(predict(data))