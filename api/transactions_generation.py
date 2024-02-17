from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
import json

fake = Faker()
Faker.seed(42)

app = Flask(__name__)

def set_fraud_case(new_transactions, fake):
    fraud_type = np.random.choice(["unusual_location", "multiple_transactions", "high_value", "mismatched_addresses"])
    new_transactions[0]["reason_for_fraud"] = fraud_type

    if fraud_type == "unusual_location":
        unusual_location = fake.local_latlng(country_code="JP")  # Example: Simulate a transaction from Japan
        new_transactions[0]["location"] = unusual_location
    elif fraud_type == "multiple_transactions":
        # Simulate multiple transactions with the same user_id within a short timeframe
        for _, sec in enumerate(range(1, 3)):
            fraud_transaction = new_transactions[0]
            fraud_transaction["timestamp"] = (datetime.fromisoformat(fraud_transaction["timestamp"]) + timedelta(seconds=sec)).isoformat()
            new_transactions.append(fraud_transaction)
    elif fraud_type == "high_value":
        new_transactions[0]["amount"] = np.random.randint(100000, 10000000)  # Example: Generate a high amount
    elif fraud_type == "mismatched_addresses":
        new_transactions[0]["shipping_address"] = fake.address()  # Generate a different shipping address

    return new_transactions

def generate_transaction(fraud=False):
    # Generate transaction details randomly
    billing_address = fake.address()

    new_transactions = [{
        "user_id": fake.random_int(min=1, max=100),
        "product_id": fake.random_int(min=1000, max=9999),
        "amount": float(fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
        "timestamp": fake.date_time_between(start_date=datetime.now() - timedelta(days=3), end_date=datetime.now()).isoformat(),
        "location": fake.local_latlng(),
        "billing_address": billing_address,
        "shipping_address": billing_address,
        "credit_card_number": fake.credit_card_number()
        # "is_fraud": bool(fraud),
        # "reason_for_fraud": None
    }]

    # if fraud:
    #     # Generate random customize fraud transaction
    #     new_transactions = set_fraud_case(new_transactions, fake)

    return new_transactions

@app.route("/transactions", methods=["GET"])
def generate_transactions(quantity=30, fraud_rate=0.05):
    transactions = []
    response = {
        "status_code":404,
        "message":"No Data",
        "data":[]
    }
    try:
        for i in range(quantity):
            is_fraud = np.random.choice([True, False], p=[fraud_rate, 1 - fraud_rate])
            transaction = generate_transaction(fraud=is_fraud)
            if len(transaction) > 1:
                transactions = transactions + transaction
            else:
                transactions.append(transaction[0])

        if transactions == 0:
            raise Exception(f"Something happened in the server!")
        
        response["status_code"] = 200
        response["message"] = f"Fetch data success, {len(transactions)} transactions is fetched!"
        response["data"] = transactions
        
        return json.dumps(response)
    
    except Exception as e:
        response["status_code"] = 500
        response["message"] = f"[Error]: {e}"

        return json.dumps(response)
    

if __name__ == "__main__":
    app.run(debug=True)
