import pickle
import numpy as np
import cupy as cp

DEVICE = 'cuda'  # or 'cpu'
def format_predictions(data: list):
    thing = []
    for i in data:
        print(type(i))
        if type(i) == int or type(i) == float:
            thing.append(i)
        elif str(i) == "true":
            thing.append(0)
        elif i == "CASH OUT":
            thing.extend([True, False, False, False])
            break
        elif i == "DEBIT":
            thing.extend([False, True, False, False])
            break
        elif i == "PAYMENT":
            thing.extend([False, False, True, False])
            break
        elif i == "TRANSFER":
            thing.extend([False, False, False, True])
            break
        else:
            print("Something is serioudly wrong")
    print(thing)
    predict_fraud(thing)
            
    
def predict_fraud(data: list):
    with open("model.pkl", "rb") as file:
        loaded_model = pickle.load(file)

    if DEVICE == 'cuda':
        input_data = cp.array([data])
        predictions = loaded_model.predict(input_data)

        predictions = (predictions > 0.5).astype(int)
    else:
        input_data = np.array([data])
        predictions = loaded_model.predict(input_data)

    print ("Predictions:", predictions[0])


if __name__ == '__main__':
    data = [181.00, 181.0, 0.00, 0.0, 0.0, "true","TRANSFER"]
    print(format_predictions(data))