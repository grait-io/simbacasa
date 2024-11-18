import requests
import json
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class TeablePoller:
    def __init__(self):
        self.base_url = "https://teable.grait.io/api"
        self.api_token = os.getenv("TEABLE_API_TOKEN")
        self.table_id = os.getenv("TEABLE_TABLE_ID")
        self.telegram_group_id = os.getenv("TELGRAM_GROUP_ID")
        
        # Use the specific n8n webhook URL
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
        }
        
        print(f"Initialized with webhook URL: {self.n8n_webhook_url}")
        print(f"Using Telegram Group ID: {self.telegram_group_id}")

    def get_records(self):
        """Fetch all records from the table"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("records", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching records: {str(e)}")
            return []

    def trigger_n8n_workflow(self, telegram_ids: list):
        """Trigger n8n webhook for multiple telegram IDs"""
        data = {
            "telegramIDs": telegram_ids,
            "telegramGroupId": self.telegram_group_id
        }

        try:
            print(f"Triggering webhook for telegram IDs: {telegram_ids}")
            print(f"Request data: {json.dumps(data)}")
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "python-requests",
                "Accept": "*/*"
            }
            
            response = requests.post(
                self.n8n_webhook_url, 
                json=data,
                headers=headers,
                verify=True
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response content: {response.text}")
            
            if response.status_code != 200:
                print(f"Unexpected status code: {response.status_code}")
                return False
                
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to trigger webhook: {str(e)}")
            print(f"Exception type: {type(e)}")
            if hasattr(e, 'response'):
                print(f"Response status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            return False

    def update_status(self, record_ids: list):
        """Update the status of multiple records"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        records = [{"id": record_id, "fields": {"status": "processed"}} for record_id in record_ids]
        
        payload = {
            "fieldKeyType": "name",
            "typecast": True,
            "records": records
        }
        
        try:
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Updated status to processed for records: {record_ids}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to update record status: {str(e)}")
            return False

    def process_records(self):
        """Process approved records and trigger n8n webhook in batch"""
        records = self.get_records()
        approved_records = []
        processed_count = 0

        # Collect all approved records
        for record in records:
            fields = record.get("fields", {})
            status = fields.get("status")
            telegram_id = fields.get("telegramID")
            record_id = record.get("id")

            if status == "approved" and telegram_id:
                approved_records.append({
                    "telegram_id": telegram_id,
                    "record_id": record_id
                })

        if approved_records:
            telegram_ids = [record["telegram_id"] for record in approved_records]
            record_ids = [record["record_id"] for record in approved_records]
            
            print(f"\nProcessing {len(approved_records)} approved records")
            print(f"Telegram IDs: {telegram_ids}")
            
            if self.trigger_n8n_workflow(telegram_ids):
                if self.update_status(record_ids):
                    processed_count = len(approved_records)
                    print(f"Successfully processed {processed_count} records")
                else:
                    print("Failed to update status for records")
            else:
                print("Failed to trigger webhook for records")

        return processed_count

def main():
    poller = TeablePoller()
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))
    
    print(f"""
=== Teable to Telegram Group Poller Started ===
Polling interval: {poll_interval} seconds
N8N Webhook URL: {poller.n8n_webhook_url}
Table ID: {poller.table_id}
Telegram Group ID: {poller.telegram_group_id}
    """)
    
    while True:
        try:
            processed = poller.process_records()
            if processed > 0:
                print(f"Processed {processed} records")
            time.sleep(poll_interval)
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(poll_interval)

if __name__ == "__main__":
    main()
