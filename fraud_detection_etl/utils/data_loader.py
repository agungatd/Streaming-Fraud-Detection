import os
from dotenv import load_dotenv
import requests
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, ArrayType
import time
import json
import threading

load_dotenv()  # Load environment variables from a .env file

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://127.0.0.1:5000/transactions")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
DELTA_LAKE_PATH = os.getenv("DELTA_LAKE_PATH", "../delta")

def produce_transactions_to_kafka():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'])
    while True:
        try:
            response = requests.get(API_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                for transaction in data:
                    producer.send("transactions", json.dumps(transaction).encode('utf-8'))
                # producer.flush()  # Ensure messages are sent
            else:
                print(f"Failed to fetch transactions from API: {response.status_code}\nError: {response.message}")
        except Exception as e:
            print(f"Error producing transactions to Kafka: {e}")
        finally:
            time.sleep(1)  # Wait 1 second before the next request

def load_transactions_from_kafka_to_delta_lake():
    spark = SparkSession.builder.appName("DataLoader").getOrCreate()

    schema = StructType([
        StructField("user_id", StringType()),
        StructField("product_id", StringType()),
        StructField("amount", DoubleType()),
        StructField("timestamp", TimestampType()),
        StructField("location", ArrayType(StructType([StructField("latitude", DoubleType()), StructField("longitude", DoubleType())]))),
        StructField("billing_address", StringType()), 
        StructField("shipping_address", StringType()), 
        StructField("credit_card_number", StringType()),  # Fill in remaining fields
    ])

    raw_transactions = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
        .option("subscribe", "transactions") \
        .load()

    transactions = raw_transactions \
        .select(from_json(raw_transactions.value.cast("string"), schema).alias("data")) \
        .select("data.*")
    
    transactions.show()

    # transactions.writeStream \
    #     .format("delta") \
    #     .outputMode("append") \
    #     .option("checkpointLocation", "/path/to/checkpoint") \
    #     .start(DELTA_LAKE_PATH) \
    #     .awaitTermination()

if __name__ == "__main__":
    produce_transactions_to_kafka_thread = threading.Thread(target=produce_transactions_to_kafka)
    produce_transactions_to_kafka_thread.start()

    load_transactions_from_kafka_to_delta_lake()