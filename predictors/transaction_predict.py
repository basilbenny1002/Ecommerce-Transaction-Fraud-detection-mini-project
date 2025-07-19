# import pickle
# import numpy as np
# import cupy as cp

# DEVICE = 'cuda'  # or 'cpu'
# def format_predictions(data: list):
#     thing = []
#     for i in data:
#         print(type(i))
#         if type(i) == int or type(i) == float:
#             thing.append(i)
#         # elif str(i) == "true":
#         #     thing.append(1)
#         # elif str(i) == "false":
#         #     thing.append(0) 
#         elif i == "CASH_IN":
#             thing.extend([False, False, False, False])
#             break
#         elif i == "CASH_OUT":
#             thing.extend([True, False, False, False])
#             break
#         elif i == "DEBIT":
#             thing.extend([False, True, False, False])
#             break
#         elif i == "PAYMENT":
#             thing.extend([False, False, True, False])
#             break
#         elif i == "TRANSFER":
#             thing.extend([False, False, False, True])
#             break
#         else:
#             print("Something is seriously wrong")
#     print(thing, flush=True)
#     return thing
    
            
    
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

# import pickle
# import random
# import numpy as np
# def predict_fraud(data: list):
    
#     print(data)
#     # return random.randint(0,1), 87.63
#     with open("models/transaction_model.pkl", "rb") as file:
#         loaded_model = pickle.load(file)

#     # Example input data
#     input_data = np.array([data])

#         # Make the prediction (0 or 1)
#     predictions = loaded_model.predict(input_data)
#     prediction_result = int(predictions[0])

#     probabilities = loaded_model.predict_proba(input_data)
        
#     confidence = float(probabilities[0][prediction_result])

#     print(f"Prediction: {prediction_result}, Confidence (of predicted class): {confidence:.4f}", flush=True)
        
#     return prediction_result, round(confidence * 100, 2)


# if __name__ == '__main__':
#     # import pandas
#     # data = pandas.read_csv("onlinefraud.csv")
#     # print(len(data['step'].tolist()))
#     print(predict_fraud([181.00,          181.0,            0.00  ,       21182.0      ,       0.0    ,         0      ,   False  ,         True  ,     False,         False,          False]))



# import pickle
# import pandas as pd

# # 🧠 1. Load the trained XGBoost model
# with open('transaction_model.pkl', 'rb') as f:
#     model = pickle.load(f)

# # 🚀 2. Prediction function
# def predict_transaction(
#     source,
#     browser,
#     sex,
#     age,
#     country_name,
#     n_device_occur,
#     signup_month,
#     signup_day,
#     signup_day_name,
#     purchase_month,
#     purchase_day,
#     purchase_day_name,
#     purchase_over_time
# ):
#     """
#     Takes raw feature values, preprocesses them, and returns:
#       - predicted class (0 or 1)
#       - confidence score (probability of predicted class)
#     """
#     # Convert to a single-row DataFrame
#     df = pd.DataFrame([{
#         'source': source,
#         'browser': browser,
#         'sex': sex,
#         'age': age,
#         'country_name': country_name,
#         'n_device_occur': n_device_occur,
#         'signup_month': signup_month,
#         'signup_day': signup_day,
#         'signup_day_name': signup_day_name,
#         'purchase_month': purchase_month,
#         'purchase_day': purchase_day,
#         'purchase_day_name': purchase_day_name,
#         'purchase_over_time': purchase_over_time
#     }])

#     # Ensure categorical columns match training encoding
#     for col in ['source', 'browser', 'sex', 'country_name', 'signup_day_name', 'purchase_day_name']:
#         df[col] = df[col].astype('category')

#     # Predict class and probabilities
#     pred_proba = model.predict_proba(df)[0]
#     pred_class = int(model.predict(df)[0])
#     confidence = float(pred_proba[pred_class])

#     return pred_class, confidence

# # 🧪 3. CLI support
# if __name__ == '__main__':
#     # Example raw input—feel free to change values to test
#     raw_input = {
#         'source': 'Ads',
#         'browser': 'Chrome',
#         'sex': 'F',
#         'age': 29,
#         'country_name': 'United States',
#         'n_device_occur': 2,
#         'signup_month': 7,
#         'signup_day': 15,
#         'signup_day_name': 'Tuesday',
#         'purchase_month': 7,
#         'purchase_day': 16,
#         'purchase_day_name': 'Wednesday',
#         'purchase_over_time': 1500.0,
#     }

#     pred, conf = predict_transaction(**raw_input)
#     label = 'FRAUD' if pred == 1 else 'NOT FRAUD'
#     print(f" Prediction: {label} (Confidence: {conf:.2%})")


import pickle
import pandas as pd
import numpy as np

# 1. Load the trained model + scaler
with open('models/transaction_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# 2. Columns definition (must match your train.py)
cat_cols = [
    'source', 'browser', 'sex',
    'country_name', 'signup_day_name', 'purchase_day_name'
]
num_cols = [
    'n_device_occur', 'signup_month', 'signup_day',
    'purchase_month', 'purchase_day',
    'purchase_over_time', 'age'
]

def _preprocess(df: pd.DataFrame) -> pd.DataFrame:
    # a) handle infinities exactly as in train.py
    for col in num_cols:
        vals = df[col]
        finite = vals[np.isfinite(vals)]
        if not finite.empty:
            finite_min, finite_max = finite.min(), finite.max()
            df[col] = vals.replace(np.inf,  finite_max)\
                          .replace(-np.inf, finite_min)
        else:
            df[col] = vals.replace([np.inf, -np.inf], 0)

    # b) scale numeric features
    df[num_cols] = scaler.transform(df[num_cols])

    # c) enforce categorical dtype
    for col in cat_cols:
        df[col] = df[col].astype('category')

    return df

def predict_transaction(
    source: str,
    browser: str,
    sex: str,
    age: float,
    country_name: str,
    n_device_occur: float,
    signup_month: float,
    signup_day: float,
    signup_day_name: str,
    purchase_month: float,
    purchase_day: float,
    purchase_day_name: str,
    purchase_over_time: float
) -> tuple[int, float]:
    """
    Returns (predicted_class, confidence_score)
    """
    # build single-row DataFrame
    row = {
        'source': source,
        'browser': browser,
        'sex': sex,
        'age': age,
        'country_name': country_name,
        'n_device_occur': n_device_occur,
        'signup_month': signup_month,
        'signup_day': signup_day,
        'signup_day_name': signup_day_name,
        'purchase_month': purchase_month,
        'purchase_day': purchase_day,
        'purchase_day_name': purchase_day_name,
        'purchase_over_time': purchase_over_time
    }
    df = pd.DataFrame([row])

    # preprocess & predict
    df = _preprocess(df)
    proba = model.predict_proba(df)[0]
    cls   = int(model.predict(df)[0])
    conf = float(proba[cls])* 100
    return cls, round(conf, 2)

# # 3. CLI example
# if __name__ == '__main__':
#     sample = {
#         'source': 'Ads',
#         'browser': 'Chrome',
#         'sex': 'F',
#         'age': 29,
#         'country_name': 'United States',
#         'n_device_occur': 2,
#         'signup_month': 7,
#         'signup_day': 15,
#         'signup_day_name': 'Tuesday',
#         'purchase_month': 7,
#         'purchase_day': 16,
#         'purchase_day_name': 'Wednesday',
#         'purchase_over_time': 1500.0,
#     }

#     pred, conf = predict_transaction(**sample)
#     print(pred, conf)
#     label = 'FRAUD' if pred == 1 else 'NOT FRAUD'
#     print(f" Prediction: {label} (Confidence: {conf:.2%})")
