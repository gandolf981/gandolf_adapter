from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, MONGO_USER, MONGO_PASSWORD
import time


client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_URI}{DB_NAME}?authSource=admin')
# client = MongoClient(f'mongodb://administrator:11x92wyF2A@144.172.92.16:27017/')
def test():
    print("🔌 Connecting...")

    try:
        print("🧪 Ping:", client.admin.command("ping"))

        db = client["test_db"]
        col = db["test_col"]

        print("✍️ Writing...")
        res = col.update_one(
        {"hash": "asdasdasd"},  
        {"$set": {"data":"darta"}},
        upsert=True
    )
        print("Inserted:")


        print("✅ Mongo OK")

    except Exception as e:
        print("❌ ERROR:", e)

if __name__ == "__main__":
    test()