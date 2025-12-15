"""
MongoDB Data Loader - Import HR data from JSON files into MongoDB
"""
import json
import os
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv
from bson import json_util

load_dotenv()

class MongoDataLoader:
    """Load HR data from JSON files into MongoDB"""

    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("DB_NAME", "HRWIKI")
        self.client = None
        self.db = None
        self.data_folder = Path("..") / "MongoDB Database_HRWIKI"

    def connect(self):
        """Connect to local MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
            print(f"[+] Connected to MongoDB: {self.db_name}")
            return True
        except Exception as e:
            print(f"[!] Failed to connect to MongoDB: {e}")
            print("\nPlease ensure MongoDB is running:")
            print("  - Windows: Run 'sc query MongoDB' to check service status")
            print("  - If stopped, start it with 'net start MongoDB'")
            return False

    def load_json_file(self, file_path: Path) -> list:
        """Load data from a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Use json_util to handle MongoDB extended JSON (e.g. $oid)
                data = json_util.loads(f.read())
                
                # Handle both single object and array formats
                if isinstance(data, dict):
                    return [data]
                return data
        except Exception as e:
            print(f"[!] Error reading {file_path.name}: {e}")
            return []

    def get_collection_name(self, filename: str) -> str:
        """Extract collection name from filename"""
        # Remove "HRWIKI." prefix and ".json" suffix
        if filename.startswith("HRWIKI."):
            collection_name = filename[7:]  # Remove "HRWIKI."
        else:
            collection_name = filename

        if collection_name.endswith(".json"):
            collection_name = collection_name[:-5]  # Remove ".json"

        return collection_name

    def import_collection(self, file_path: Path):
        """Import a single JSON file as a collection"""
        collection_name = self.get_collection_name(file_path.name)

        print(f"\nImporting: {file_path.name}")
        print(f"Collection: {collection_name}")

        # Load data
        data = self.load_json_file(file_path)
        if not data:
            print(f"  [WARN] No data found in {file_path.name}")
            return

        # Get or create collection
        collection = self.db[collection_name]

        # Clear existing data (optional - comment out to append instead)
        existing_count = collection.count_documents({})
        if existing_count > 0:
            print(f"  [WARN] Collection already has {existing_count} documents")
            # response = input("  Delete existing data? (y/n): ")
            response = 'y'
            if response.lower() == 'y':
                collection.delete_many({})
                print("  [+] Cleared existing data")

        # Insert data
        try:
            if len(data) == 1:
                result = collection.insert_one(data[0])
                print(f"  [+] Inserted 1 document")
            else:
                result = collection.insert_many(data)
                print(f"  [+] Inserted {len(result.inserted_ids)} documents")
        except Exception as e:
            print(f"  [!] Error inserting data: {e}")

    def import_all(self):
        """Import all JSON files from the data folder"""
        if not self.data_folder.exists():
            print(f"[!] Data folder not found: {self.data_folder}")
            print("Please ensure the 'MongoDB Database_HRWIKI' folder exists")
            return

        # Get all JSON files
        json_files = list(self.data_folder.glob("*.json"))

        if not json_files:
            print(f"[!] No JSON files found in {self.data_folder}")
            return

        print(f"\nFound {len(json_files)} JSON files to import:")
        for i, file in enumerate(json_files, 1):
            print(f"  {i}. {file.name}")

        print("\n" + "="*60)
        # response = input(f"\nImport all {len(json_files)} files? (y/n): ")
        response = 'y'

        if response.lower() != 'y':
            print("Import cancelled")
            return

        # Import each file
        successful = 0
        for file_path in json_files:
            try:
                self.import_collection(file_path)
                successful += 1
            except Exception as e:
                print(f"[!] Failed to import {file_path.name}: {e}")

        print(f"\n{'='*60}")
        print(f"Import complete: {successful}/{len(json_files)} files imported successfully")

        # Show collection statistics
        self.show_statistics()

    def show_statistics(self):
        """Show statistics for all collections"""
        print(f"\n{'='*60}")
        print("Database Statistics:")
        print(f"{'='*60}")

        collections = self.db.list_collection_names()
        for collection_name in collections:
            count = self.db[collection_name].count_documents({})
            print(f"  {collection_name}: {count} documents")

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("\n[+] MongoDB connection closed")

def main():
    """Main function"""
    print("""
    ================================================
         HRMS MongoDB Data Loader                
         Import JSON files into MongoDB          
    ================================================
    """)

    loader = MongoDataLoader()

    if not loader.connect():
        return

    try:
        loader.import_all()
    except KeyboardInterrupt:
        print("\n\nImport interrupted by user")
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
    finally:
        loader.close()

if __name__ == "__main__":
    main()
