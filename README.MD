

## 🧠 Fraud Detection using XGBoost (Mini Project)

This is a **basic binary classification project** built for a **college mini project**.
The goal is to classify online transactions as either **fraudulent** or **legitimate** using the **XGBoost algorithm**.

### 🔍 What it does

* Reads a CSV dataset of transactions
* Uses the XGBoost model to classify each transaction as:

  * `1` → Fraud
  * `0` → Not Fraud
* Evaluates the model with simple accuracy or confusion matrix

### 🛠 Tech Used

* Python
* XGBoost
* Pandas
* Scikit-learn (for splitting data and metrics)



### ⚙️ How to Run


1. Clone the repo
2. Install requirements:

   ```
   pip install -r requirements.txt
   ```
3. Run the script:

   ```
   uvicorn app.main:app --reload   
4.Use this front end [@here](https://github.com/basilbenny1002/fraud-detection) 
   ```

> 💡 *This is a simple project meant for learning and academic purposes only.*



