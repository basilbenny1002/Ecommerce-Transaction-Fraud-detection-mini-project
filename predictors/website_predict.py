import pickle
import numpy as np
import pandas as pd # Still needed for the powerful to_datetime conversion
from scrapers.ssl_details import get_ssl_details
from scrapers.tranco_list import domain_rank
from scrapers.site_scores import get_trust_score, has_sitejabber_reviews
from scrapers.domain_age import get_domain_registration_details
from scrapers.utils import analyze_url, analyze_website_features


def format_data(url: str, credit_card_payment: int = None , money_back_option: int = None, cash_on_delivery: int = None, crypto_payment: int = None, free_contact_mails: int = None, logo_url: int = None):
    data = []
    details, shortened_url  = analyze_url(url)
    data.extend(details)
    if not credit_card_payment and not money_back_option and not cash_on_delivery and not crypto_payment and not free_contact_mails and not logo_url:
        features  = analyze_website_features(shortened_url)
        for key, value in features.items():
            data.append(int(value))
    else:
        data.append(credit_card_payment)
        data.append(money_back_option)
        data.append(cash_on_delivery)
        data.append(crypto_payment)
        data.append(free_contact_mails)
        data.append(logo_url)

    data.extend(get_ssl_details(shortened_url))
    data.extend(get_domain_registration_details(shortened_url))
    data.extend(get_trust_score(shortened_url))
    data.append(has_sitejabber_reviews(shortened_url))
    data.extend(domain_rank(shortened_url))
    print(data)
    return predict_fraud_from_list(url, data)

    


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
    with open('models/website_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Get the raw prediction (0 or 1)
    prediction_val = int(model.predict(input_array)[0])
    # Get the probability of the positive class (fraudulent)
    probability = float(model.predict_proba(input_array)[0][1])

    # Determine the prediction label
    prediction_label = "Fraudulent" if prediction_val == 1 else "Legitimate"
    return prediction_val, f"{probability:.2%}"
    return {
        "url": shop_url,
        "prediction": prediction_label,
        "confidence_fraud": f"{probability:.2%}"
    }

# --- Example Usage ---

# The URL of the shop you want to check
# shop_url_input = "https://www.amazon.com"

# # Provide the feature values in the exact order the model was trained on.
# # All values must be present.
# input_features = [
#     17,                             # Domain length
#     3,                              # Top domain length
#     1,                              # Presence of 'www'
#     0,                              # Number of digits
#     13,                             # Number of letters
#     1,                              # Number of dots
#     0,                              # Number of hyphens
#     1,                              # Has credit card payment
#     1,                              # Has money-back option
#     1,                              # Has cash on delivery
#     0,                              # Accepts crypto?
#     1,                              # Has free contact email
#     1,                              # Has logo
#     1,                              # Org in known SSL org list
#     0,                              # Not a young domain
#     "1995-07-30 00:00:00",          # Domain registration date (at index 15)
#     1,                              # Has TrustPilot reviews
#     4.6,                            # High TrustPilot score
#     1,                              # SiteJabber reviews exist
#     1,                              # Present in Tranco list
#     100                             # Tranco rank
# ]

# # Get the prediction
# result = predict_fraud_from_list(shop_url_input, input_features)
# print(result)



data, url = format_data("https://www.amazon.in/hz/mobile/mission?p=6HZjbXAv%2BuCoQJnp5zydwUz0qaZiQDzrfvlOokAcp3zCZahWUKXiCXf26y1CqQKevaul2MjjgTCBw4Qg5CblsMQT7g40FQcIIVPUi7gfaCwr1J2NYqr2H7nLaiLcrtLuznPAofGpKOkEVvfQ9xhbjJVZhxWItmRqmsZRWXtNno8Ut8vF3EQgpsTuFR%2Bi3F0ME6O9l6gZBJQB76yUGh98baIL1%2FhU%2BU3CVl2gf%2B%2B3Cck36600VX%2FO08gFEtDS5cnQpSkFbEUUkhJK2Cbef4T0xNx5CUFXlDxhiZ5DCt8Jkevx5oqp%2BikrEGmBTGfqL6LBAbwL1gLS66eHlOAe4xKzVeolBzcYQWEmdnVPW0DUDtbn%2FNEHU9NJcz9m3MdUSFOr&ref_=ci_mcx_mi&pf_rd_r=60H00ASZW7XB4VWXXPNQ&pf_rd_p=45c1a5b4-dab8-4658-948a-91185ec4c179&pd_rd_r=5d2f1862-a090-4f94-8dfe-6c931ff26092&pd_rd_w=s33dL&pd_rd_wg=xqEa0")

print(predict_fraud_from_list(url, data))

