import whois
from datetime import datetime, timedelta

def get_domain_registration_details(domain_name):
    """
    Retrieves WHOIS information for a domain to determine its age and registration date.

    Args:
        domain_name (str): The domain to look up (e.g., 'google.com').

    Returns:
        dict: A dictionary containing the age indication and the registration date.
              Returns an error message if the lookup fails.
    """
    results = {
        "is_young_domain": None,
        "registration_date": None,
        "status_message": ""
    }

    try:
        # 1. Perform the WHOIS lookup
        w = whois.whois(domain_name)

        # 2. Check if a creation date exists in the record
        if not w.creation_date:
            results["is_young_domain"] = 2  # 2 - 'hidden' or not found
            results["registration_date"] = "N/A"
            results["status_message"] = "Registration date is hidden or could not be found."
            return results

        # The library can return a list or a single datetime object
        # We take the first entry if it's a list
        reg_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date

        # 3. Calculate the domain's age
        now = datetime.now()
        age = now - reg_date
        
        # 4. Determine if the domain is 'young' (400 days or less)
        if age.days <= 400:
            results["is_young_domain"] = 1  # 1 - 'young' domain name
        else:
            results["is_young_domain"] = 0  # 0 - 'old' domain name

        # Format the date for clean output
        results["registration_date"] = reg_date.strftime("%Y-%m-%d %H:%M:%S")
        results["status_message"] = "Successfully retrieved details."

    except Exception as e:
        results["is_young_domain"] = 2 # Treat errors as 'hidden'/unavailable
        results["registration_date"] = "N/A"
        results["status_message"] = f"An error occurred: {e}"

    return [results["is_young_domain"], results["registration_date"]]

# print(get_domain_registration_details("google.com"))