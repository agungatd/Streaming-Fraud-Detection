from kafka3 import KafkaConsumer
import json

consumer = KafkaConsumer('transactions', bootstrap_servers=["127.0.0.1:29092"])

def main():
    for msg in consumer:
        print(json.loads(msg.value))
        # break

if __name__ == '__main__':
    main()