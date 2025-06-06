from tranco import Tranco
from datetime import datetime, timedelta
import os
import glob
import sys
import io
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# Set cache dir
cache_folder = "tranco"
os.makedirs(cache_folder, exist_ok=True)

def get_latest_csv(folder):
    csv_files = glob.glob(os.path.join(folder, "*.csv"))
    if not csv_files:
        return None
    return max(csv_files, key=os.path.getctime)

def domain_rank(domain):
    csv_path = download_tranco_if_not_exists()
    """Return the rank of the domain if found, else -1."""
    try:
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for rank, row in enumerate(reader, start=1):
                if row and domain.strip().lower() == row[1].strip().lower():
                    return rank
    except Exception as e:
        print(f"[!] Failed to read CSV: {e}")
    return -1

def download_tranco_if_not_exists():
    today_str = datetime.today().strftime('%Y-%m-%d')
    today_filename = os.path.join(cache_folder, f"tranco_list_{today_str}.csv")

    # ✅ If today's file exists, use it
    if os.path.exists(today_filename):
        print(f"[✓] Tranco list for today ({today_str}) already exists.")
        return today_filename

    # ❌ Delete yesterday's file if exists
    yesterday_str = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_filename = os.path.join(cache_folder, f"tranco_list_{yesterday_str}.csv")
    if os.path.exists(yesterday_filename):
        os.remove(yesterday_filename)
        print(f"[!] Removed outdated file: {yesterday_filename}")

    # ⬇️ Try downloading a new one
    t = Tranco(cache=True, cache_dir=cache_folder)

    for i in range(30):
        date = datetime.today() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        print(f"Trying {date_str}...")

        try:
            tr_list = t.list(date=date_str)
            latest_csv = get_latest_csv(cache_folder)

            if latest_csv and os.path.getsize(latest_csv) > 0:
                os.rename(latest_csv, today_filename)

                # Delete any other leftover CSVs
                for f in glob.glob(os.path.join(cache_folder, "*.csv")):
                    if f != today_filename:
                        os.remove(f)

                print(f"[✓] Saved Tranco list as '{today_filename}'")
                return today_filename
            else:
                print(f"[!] No valid CSV saved for {date_str}")
        except Exception as e:
            print(f"[X] Failed for {date_str} - {e}")
    else:
        print("No Tranco list found in the last 30 days.")
        return None

# ---- Main Execution ----
# csv_file_path = download_tranco_if_not_exists()

# Example usage:
if True:
    domain = "google.com"
    rank = domain_rank(domain)
    print(f"Rank of {domain}: {rank if rank != -1 else 'Not found'}")
