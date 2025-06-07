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
        # elif str(i) == "true":
        #     thing.append(1)
        # elif str(i) == "false":
        #     thing.append(0) 
        elif i == "CASH_IN":
            thing.extend([True, False, False, False, False])
            break
        elif i == "CASH_OUT":
            thing.extend([False,True, False, False, False])
            break
        elif i == "DEBIT":
            thing.extend([False,False, True, False, False])
            break
        elif i == "PAYMENT":
            thing.extend([False,False, False, True, False])
            break
        elif i == "TRANSFER":
            thing.extend([False,False, False, False, True])
            break
        else:
            print("Something is seriously wrong")
    print(thing, flush=True)
    return thing
    
            
    
# def predict_fraud(data: list):
#     with open("model.pkl", "rb") as file:
#         loaded_model = pickle.load(file)

#     if DEVICE == 'cuda':
#         input_data = cp.array([data])
#         predictions = loaded_model.predict(input_data)

#         predictions = (predictions > 0.5).astype(int)
#     else:
#         input_data = np.array([data])
#         predictions = loaded_model.predict(input_data)
#     print(predictions)
#     return predictions[0]


# if __name__ == '__main__':
#     # data = [181.00, 181.0, 0.00, 0.0, 0.0, "true","TRANSFER"]
#     # print(format_predictions(data))
#     # print(predict_fraud([181.0, 0.0, 0.0, 0.0, 0.0, 1, False, False, False, True]))
#     print(predict_fraud([181.00,          181.0,            0.00,             0.0,             0.0,                       0,          False,       False,         False,           True]))

import pickle
import random
import numpy as np
def predict_fraud(data: list):
    
    print(data)
    return random.randint(0,1), 87.63
    with open("models/transaction_model.pkl", "rb") as file:
        loaded_model = pickle.load(file)

    # Example input data
    input_data = np.array([data])

        # Make the prediction (0 or 1)
    predictions = loaded_model.predict(input_data)
    prediction_result = int(predictions[0])

        # Get the probabilities for each class (e.g., [prob_class_0, prob_class_1])
        # This method is common for classification models to get confidence
    probabilities = loaded_model.predict_proba(input_data)
        
        # The confidence is now the probability of the *predicted* class
        # If prediction_result is 0, confidence is probabilities[0][0] (confidence of being not fraud)
        # If prediction_result is 1, confidence is probabilities[0][1] (confidence of being fraud)
    confidence = probabilities[0][prediction_result]

    print(f"Prediction: {prediction_result}, Confidence (of predicted class): {confidence:.4f}", flush=True)
        
    return prediction_result, confidence


if __name__ == '__main__':
    # import pandas
    # data = pandas.read_csv("onlinefraud.csv")
    # print(len(data['step'].tolist()))
    print(predict_fraud([181.00,          181.0,            0.00  ,       21182.0      ,       0.0    ,         0      ,   False  ,         True  ,     False,         False,          False]))