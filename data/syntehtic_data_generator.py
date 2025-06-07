import csv
import random
import io
import pandas as pd

# --- Configuration ---
NUM_ROWS_PER_CHUNK = 2000
NUM_CHUNKS = 500 # Total rows = NUM_ROWS_PER_CHUNK * NUM_CHUNKS
OUTPUT_FILENAME = "ecommerce_transactions_capped.csv"

TRANSACTION_TYPES = ['CASH_IN', 'CASH_OUT', 'PAYMENT', 'TRANSFER', 'DEBIT']
FRAUD_ELIGIBLE_TYPES = ['TRANSFER', 'CASH_OUT']

MAX_AMOUNT_CAP = 10000.00
# Threshold for a transaction to be system-flagged (isFlaggedFraud=1),
# relevant for large TRANSFERs (fraudulent or not).
# Let's set it to 80% of the MAX_AMOUNT_CAP.
FLAGGED_FRAUD_THRESHOLD = MAX_AMOUNT_CAP * 0.8

# --- Helper Functions ---

def generate_account_id(prefix="C"):
    """Generates a random account ID."""
    return f"{prefix}{random.randint(100000000, 999999999)}"

def generate_transaction_details(step_val, is_fraud_target):
    """Generates a single transaction row."""
    transaction = {}
    transaction['step'] = step_val

    # Balances can still be high, but transaction amounts will be capped.
    oldbalanceOrg = round(random.uniform(0, 1000000), 2) # Reduced range for more relevance with capped amounts
    oldbalanceDest_initial = round(random.uniform(0, 500000), 2)

    transaction['nameOrig'] = generate_account_id("C")
    transaction['nameDest'] = generate_account_id("M")

    transaction['isFlaggedFraud'] = 0 # Default

    if is_fraud_target:
        transaction['isFraud'] = 1
        transaction['type'] = random.choice(FRAUD_ELIGIBLE_TYPES)

        # Ensure there's a significant balance for impactful fraud,
        # even if the transaction amount itself is capped.
        if oldbalanceOrg < 1000 and oldbalanceOrg < MAX_AMOUNT_CAP:
            oldbalanceOrg = round(random.uniform(1000, MAX_AMOUNT_CAP * 2), 2) # Up to 2x cap
        elif oldbalanceOrg < 1000: # If oldbalanceOrg is already > MAX_AMOUNT_CAP, but < 1000 (unlikely with cap)
            oldbalanceOrg = round(random.uniform(1000, oldbalanceOrg + 1000), 2)


        # Fraudulent amount is min of original balance and the cap
        transaction['amount'] = min(oldbalanceOrg, MAX_AMOUNT_CAP)
        transaction['oldbalanceOrg'] = oldbalanceOrg
        transaction['newbalanceOrig'] = round(oldbalanceOrg - transaction['amount'], 2)

        transaction['oldbalanceDest'] = oldbalanceDest_initial
        transaction['newbalanceDest'] = round(oldbalanceDest_initial + transaction['amount'], 2)

        if transaction['type'] == 'TRANSFER' and transaction['amount'] > FLAGGED_FRAUD_THRESHOLD:
            transaction['isFlaggedFraud'] = 1

    else: # Non-fraudulent transaction
        transaction['isFraud'] = 0
        transaction['type'] = random.choice(TRANSACTION_TYPES)
        transaction['oldbalanceOrg'] = oldbalanceOrg
        transaction['oldbalanceDest'] = oldbalanceDest_initial

        if transaction['type'] == 'CASH_IN':
            # Orig receives, Dest (M) is source.
            source_balance_for_cash_in = transaction['oldbalanceDest']

            if source_balance_for_cash_in <= 1.00:
                # If dest has no money, generate a small arbitrary amount for CASH_IN
                # and retroactively set oldbalanceDest to cover it.
                transaction['amount'] = round(random.uniform(1.00, min(100.00, MAX_AMOUNT_CAP)), 2)
                transaction['oldbalanceDest'] = transaction['amount'] + round(random.uniform(0.01, 50.00), 2) # Ensure source had enough
            else:
                # Amount is up to 80% of source's balance, capped by MAX_AMOUNT_CAP
                max_from_source = source_balance_for_cash_in * 0.8
                upper_amount_limit = min(max_from_source, MAX_AMOUNT_CAP)

                if upper_amount_limit < 1.00:
                    transaction['amount'] = round(max(0.01, upper_amount_limit), 2) # Min 0.01 if possible
                else:
                    transaction['amount'] = round(random.uniform(1.00, upper_amount_limit), 2)

            transaction['newbalanceOrig'] = round(oldbalanceOrg + transaction['amount'], 2)
            transaction['newbalanceDest'] = round(transaction['oldbalanceDest'] - transaction['amount'], 2)

        elif transaction['type'] in ['CASH_OUT', 'PAYMENT', 'TRANSFER', 'DEBIT']:
            # Orig sends, Dest (M) receives.
            if oldbalanceOrg <= 0.00: # Strict check for no balance
                transaction['amount'] = 0.00
            elif oldbalanceOrg <= 1.00: # Very low balance
                 transaction['amount'] = round(random.uniform(0.01, min(oldbalanceOrg, MAX_AMOUNT_CAP)),2)
            else:
                # Amount is up to 80% of originator's balance, capped by MAX_AMOUNT_CAP
                max_from_orig = oldbalanceOrg * 0.8
                upper_amount_limit = min(max_from_orig, MAX_AMOUNT_CAP)

                if upper_amount_limit < 1.00: # If 80% or cap is very small
                    transaction['amount'] = round(max(0.01, upper_amount_limit), 2)
                else:
                    transaction['amount'] = round(random.uniform(1.00, upper_amount_limit), 2)

            transaction['newbalanceOrig'] = round(oldbalanceOrg - transaction['amount'], 2)
            transaction['newbalanceDest'] = round(transaction['oldbalanceDest'] + transaction['amount'], 2)

            if transaction['type'] == 'TRANSFER' and transaction['amount'] > FLAGGED_FRAUD_THRESHOLD:
                if random.random() < 0.1: # 10% chance for a non-fraud large transfer to be flagged
                    transaction['isFlaggedFraud'] = 1

        transaction.setdefault('amount', 0.0) # Ensure amount is always present
        transaction.setdefault('newbalanceOrig', transaction['oldbalanceOrg'])
        transaction.setdefault('newbalanceDest', transaction['oldbalanceDest'])


    for key in ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']:
        transaction[key] = abs(round(transaction.get(key, 0.0), 2))

    if transaction['newbalanceOrig'] < 0: transaction['newbalanceOrig'] = 0.00
    if transaction['newbalanceDest'] < 0: transaction['newbalanceDest'] = 0.00
    if transaction['amount'] < 0: transaction['amount'] = 0.00 # Should be covered by abs

    return transaction

# --- Main Generation Logic ---
all_transactions = []
current_step = 1

print(f"Generating {NUM_CHUNKS * NUM_ROWS_PER_CHUNK} transactions...")
print(f"Max transaction amount capped at: {MAX_AMOUNT_CAP}")
print(f"Flagged fraud threshold (for large transfers): {FLAGGED_FRAUD_THRESHOLD}")


for i in range(NUM_CHUNKS):
    # chunk_transactions = [] # Not strictly needed if appending directly
    print(f"Generating chunk {i+1}/{NUM_CHUNKS}...")
    for j in range(NUM_ROWS_PER_CHUNK):
        is_target_fraud = (j % 2 == 0)

        transaction_data = generate_transaction_details(current_step, is_target_fraud)
        all_transactions.append(transaction_data) # Append directly
        current_step += 1
    # all_transactions.extend(chunk_transactions) # Not needed if appending directly

random.shuffle(all_transactions) # Shuffle all transactions after generation

# --- Output to CSV String (or file) ---
csv_output = io.StringIO()
fieldnames = ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig',
              'nameDest', 'oldbalanceDest', 'newbalanceDest', 'isFraud', 'isFlaggedFraud']
writer = csv.DictWriter(csv_output, fieldnames=fieldnames)

writer.writeheader()
writer.writerows(all_transactions)

csv_data_string = csv_output.getvalue()
csv_output.close()

with open(OUTPUT_FILENAME, 'w', newline='') as f:
    f.write(csv_data_string)

print(f"\nGenerated {len(all_transactions)} transactions.")
print(f"Data saved to {OUTPUT_FILENAME}")

print("\n--- Sample of Generated CSV (first 20 lines) ---")
header_and_first_20_lines = csv_data_string.splitlines()[:21]
for line in header_and_first_20_lines:
    print(line)

fraud_count = sum(1 for row in all_transactions if row['isFraud'] == 1)
total_count = len(all_transactions)
if total_count > 0:
    print(f"\n--- Sanity Check ---")
    print(f"Total transactions: {total_count}")
    print(f"Fraudulent transactions: {fraud_count} ({ (fraud_count/total_count)*100:.2f}%)")
    print(f"Non-Fraudulent transactions: {total_count - fraud_count} ({ ((total_count-fraud_count)/total_count)*100:.2f}%)")

    actual_max_amount = 0
    if all_transactions:
        actual_max_amount = max(row['amount'] for row in all_transactions)
    print(f"Actual maximum transaction amount in dataset: {actual_max_amount:.2f}")

    flagged_fraud_count = sum(1 for row in all_transactions if row['isFlaggedFraud'] == 1)
    print(f"Flagged as fraud (isFlaggedFraud=1): {flagged_fraud_count}")
else:
    print("No transactions generated.")


if input("\nPress Enter to order the steps or tye exit to quit...").lower() == "exit":
    exit()
# Path to your CSV file
csv_file = "ecommerce_transactions_capped.csv"

# Read the CSV
df = pd.read_csv(csv_file)

# Check if 'step' column exists
if 'step' in df.columns:
    # Replace 'step' values with numbers 1 to len(df)
    df['step'] = range(1, len(df) + 1)

    # Write the updated DataFrame back to the same file
    df.to_csv(csv_file, index=False)
    print("Step column updated successfully.")
else:
    print("Error: 'step' column not found in the CSV.")