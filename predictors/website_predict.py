import pickle
import numpy as np
import pandas as pd # Still needed for the powerful to_datetime conversion

def predict_fraud_from_list(shop_url, feature_values):
    """
    Predicts whether a shop is fraudulent using a trained model and a simple list.

    Args:
        shop_url (str): The URL of the online shop.
        feature_values (list): A list of feature values in the specific order
                               the model requires.

    Returns:
        dict: A dictionary containing the URL, prediction, and confidence score.
    """
    # --- Data Preparation ---

    # The model was trained on a numeric timestamp, not a date string.
    # We must convert the date string to a UNIX timestamp.
    # The 'Domain registration date' is at index 15 in our list.
    DATE_INDEX = 15

    # Make a copy to avoid changing the original list
    processed_values = list(feature_values)

    try:
        # Use pandas' robust `to_datetime` to parse the date string
        date_val = pd.to_datetime(processed_values[DATE_INDEX])
        # Convert to a UNIX timestamp (in seconds)
        timestamp = int(date_val.timestamp())
        processed_values[DATE_INDEX] = timestamp
    except (ValueError, TypeError):
        # If conversion fails, use a neutral value like -1
        processed_values[DATE_INDEX] = -1


    # Convert the list of features into a 2D NumPy array.
    # The model expects a 2D array for prediction, e.g., [[val1, val2, ...]]
    input_array = np.array([processed_values], dtype=float)

    # --- Load Model and Predict ---

    # Load the trained model from the file
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Get the raw prediction (0 or 1)
    prediction_val = int(model.predict(input_array)[0])
    # Get the probability of the positive class (fraudulent)
    probability = float(model.predict_proba(input_array)[0][1])

    # Determine the prediction label
    prediction_label = "Fraudulent" if prediction_val == 1 else "Legitimate"

    return {
        "url": shop_url,
        "prediction": prediction_label,
        "confidence_fraud": f"{probability:.2%}"
    }

# --- Example Usage ---

# The URL of the shop you want to check
shop_url_input = "https://www.amazon.com"

# Provide the feature values in the exact order the model was trained on.
# All values must be present.
input_features = [
    17,                             # Domain length
    3,                              # Top domain length
    1,                              # Presence of 'www'
    0,                              # Number of digits
    13,                             # Number of letters
    1,                              # Number of dots
    0,                              # Number of hyphens
    1,                              # Has credit card payment
    1,                              # Has money-back option
    1,                              # Has cash on delivery
    0,                              # Accepts crypto?
    1,                              # Has free contact email
    1,                              # Has logo
    1,                              # Org in known SSL org list
    0,                              # Not a young domain
    "1995-07-30 00:00:00",          # Domain registration date (at index 15)
    1,                              # Has TrustPilot reviews
    4.6,                            # High TrustPilot score
    1,                              # SiteJabber reviews exist
    1,                              # Present in Tranco list
    100                             # Tranco rank
]

# Get the prediction
result = predict_fraud_from_list(shop_url_input, input_features)
print(result)