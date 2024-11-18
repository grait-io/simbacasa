from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerUser, InputPeerChannel
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import requests
import json
import time
from dotenv import load_dotenv
import os
import sys
import traceback

# Load environment variables
load_dotenv()

class TeablePoller:
    def __init__(self):
        self.base_url = "https://teable.grait.io/api"
        self.api_token = os.getenv("TEABLE_API_TOKEN")
        self.table_id = os.getenv("TEABLE_TABLE_ID")
        self.telegram_group_id = os.getenv("TELGRAM_GROUP_ID")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
        }
        
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

    def get_approved_records(self):
        """Get all approved records that need processing"""
        records = self.get_records()
        approved_records = []

        for record in records:
            fields = record.get("fields", {})
            status = fields.get("status")
            telegram_id = fields.get("telegramID")
            record_id = record.get("id")

            if status == "approved" and telegram_id:
                approved_records.append({
                    "telegram_id": int(telegram_id),  # Ensure it's an integer
                    "record_id": record_id
                })

        return approved_records

class TelegramGroupManager:
    def __init__(self):
        # Get credentials from environment variables
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.group_id = int(os.getenv("TELGRAM_GROUP_ID"))
        
        # Initialize client
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        
    def connect(self):
        """Connect to Telegram and ensure authorization"""
        self.client.connect()
        
        if not self.client.is_user_authorized():
            # Request the code
            phone_code_hash = self.client.send_code_request(self.phone).phone_code_hash
            
            try:
                # Get the code from user input
                code = input('Enter the code you received: ')
                self.client.sign_in(
                    phone=self.phone,
                    code=code,
                    phone_code_hash=phone_code_hash
                )
            except PhoneCodeInvalidError:
                print("Invalid code entered. Please try again.")
                return False
            except SessionPasswordNeededError:
                # Handle 2FA if enabled
                password = input('Enter your 2FA password: ')
                self.client.sign_in(password=password)
        
        print("Successfully connected to Telegram!")
        return True

    def get_groups(self):
        """Get all groups and their details"""
        print("\nFetching all groups...")
        chats = []
        last_date = None
        chunk_size = 200
        groups = []
        
        result = self.client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)
        
        for chat in chats:
            try:
                if hasattr(chat, 'megagroup') and chat.megagroup:
                    title = str(chat.title)  # Ensure title is a string
                    if len(title) > 30:
                        title = title[:27] + "..."
                    
                    groups.append({
                        'title': title,
                        'id': str(chat.id),  # Convert to string to avoid formatting issues
                        'access_hash': str(chat.access_hash),
                        'members_count': str(getattr(chat, 'participants_count', 'N/A'))
                    })
            except Exception as e:
                print(f"Error processing chat: {str(e)}")
                continue
        
        if not groups:
            print("No groups found!")
            return []
        
        # Print groups in a formatted way
        print("\nAvailable Groups:")
        print("=" * 80)
        print(f"{'Title':<30} {'ID':<15} {'Access Hash':<20} {'Members':<10}")
        print("-" * 80)
        
        for g in groups:
            try:
                print(f"{g['title']:<30} {g['id']:<15} {g['access_hash']:<20} {g['members_count']:<10}")
            except Exception as e:
                print(f"Error printing group: {str(e)}")
                continue
                
        print("=" * 80)
        
        # If we have a target group ID, find and highlight its information
        target_id = str(self.group_id)  # Convert to string for comparison
        target_group = next((g for g in groups if g['id'] == target_id), None)
        
        if target_group:
            print(f"\nYOUR TARGET GROUP:")
            print(f"Title: {target_group['title']}")
            print(f"ID: {target_group['id']}")
            print(f"Access Hash: {target_group['access_hash']}")
            print(f"Members: {target_group['members_count']}")
            print("\nAdd this access hash to your .env file as TELEGRAM_GROUP_HASH")
        else:
            print(f"\nWARNING: Could not find group with ID {target_id} in your groups!")
            print("Make sure you have the correct group ID and you are a member of the group.")
        
        return groups
        
    def add_users(self, users):
        """Add multiple users to the group
        
        Args:
            users (list): List of dictionaries containing user info with keys:
                         - telegram_id: The user's Telegram ID
                         - record_id: The Teable record ID
        """
        # Get the target group's access hash from environment or fetch it
        group_hash = os.getenv("TELEGRAM_GROUP_HASH")
        if not group_hash:
            groups = self.get_groups()
            target_group = next((g for g in groups if g['id'] == str(self.group_id)), None)
            if not target_group:
                raise ValueError(f"Could not find group with ID {self.group_id}")
            group_hash = int(target_group['access_hash'])
        else:
            group_hash = int(group_hash)

        target_group_entity = InputPeerChannel(self.group_id, group_hash)
        error_count = 0
        successful_records = []
        
        for user in users:
            try:
                # Get the user's access hash
                user_entity = self.client.get_input_entity(user['telegram_id'])
                if not isinstance(user_entity, InputPeerUser):
                    print(f"Skipping user {user['telegram_id']}: Not a user entity")
                    continue

                print(f"Adding user with ID: {user['telegram_id']}")
                
                self.client(InviteToChannelRequest(
                    target_group_entity,
                    [user_entity]
                ))
                
                # Mark this record as successful
                successful_records.append(user['record_id'])
                
                # Wait between adds to avoid flood
                print("Waiting 60 seconds before next add...")
                time.sleep(60)
                
            except PeerFloodError:
                print("Getting Flood Error from Telegram. Script should be stopped. Try again after some time.")
                break
            except UserPrivacyRestrictedError:
                print(f"The user {user['telegram_id']} privacy settings do not allow you to add them. Marking as processed.")
                successful_records.append(user['record_id'])
                continue
            except Exception as e:
                print(f"Unexpected error while adding user {user['telegram_id']}: {str(e)}")
                traceback.print_exc()
                error_count += 1
                if error_count > 10:
                    print("Too many errors occurred. Stopping script.")
                    break
                continue
        
        return successful_records

    def close(self):
        """Close the Telegram client connection"""
        self.client.disconnect()

def main():
    # Check if we're just listing groups
    if len(sys.argv) > 1 and sys.argv[1] == '--list-groups':
        manager = TelegramGroupManager()
        try:
            if manager.connect():
                manager.get_groups()
        finally:
            manager.close()
        return

    # Normal operation
    poller = TeablePoller()
    manager = TelegramGroupManager()
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))
    
    print(f"""
=== Direct Telegram Group Addition Service Started ===
Polling interval: {poll_interval} seconds
Table ID: {poller.table_id}
Telegram Group ID: {poller.telegram_group_id}
    """)
    
    try:
        # Connect to Telegram
        if not manager.connect():
            print("Failed to connect to Telegram. Please try again.")
            return
        
        # If TELEGRAM_GROUP_HASH is not set, get it first
        if not os.getenv("TELEGRAM_GROUP_HASH"):
            print("\nTELEGRAM_GROUP_HASH not found in .env")
            manager.get_groups()
            print("\nPlease add the access hash to your .env file and restart the script.")
            return
        
        while True:
            try:
                # Get approved records
                approved_records = poller.get_approved_records()
                
                if approved_records:
                    print(f"\nProcessing {len(approved_records)} approved records")
                    print(f"Telegram IDs: {[r['telegram_id'] for r in approved_records]}")
                    
                    # Add users to group and get successful records
                    successful_records = manager.add_users(approved_records)
                    
                    # Update status for successful additions
                    if successful_records:
                        if poller.update_status(successful_records):
                            print(f"Successfully processed {len(successful_records)} records")
                        else:
                            print("Failed to update status for records")
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                traceback.print_exc()
                time.sleep(poll_interval)
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
    finally:
        manager.close()

if __name__ == "__main__":
    main()
