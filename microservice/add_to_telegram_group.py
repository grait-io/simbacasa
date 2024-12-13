from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, EditBannedRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerUser, InputPeerChannel, ChatBannedRights, Channel
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, ChannelInvalidError
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

class ProcessedIdsStorage:
    def __init__(self, filename="processed_ids.json"):
        self.filename = filename
        self.processed_ids = self._load_processed_ids()

    def _load_processed_ids(self):
        """Load processed IDs from storage file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return json.load(f)
            return {"added": [], "removed": []}
        except Exception as e:
            print(f"Error loading processed IDs: {str(e)}")
            return {"added": [], "removed": []}

    def _save_processed_ids(self):
        """Save processed IDs to storage file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.processed_ids, f)
        except Exception as e:
            print(f"Error saving processed IDs: {str(e)}")

    def is_processed(self, telegram_id: int, action_type: str) -> bool:
        """Check if a Telegram ID has been processed for a specific action"""
        return telegram_id in self.processed_ids.get(action_type, [])

    def mark_as_processed(self, telegram_id: int, action_type: str):
        """Mark a Telegram ID as processed for a specific action"""
        if action_type not in self.processed_ids:
            self.processed_ids[action_type] = []
        if telegram_id not in self.processed_ids[action_type]:
            self.processed_ids[action_type].append(telegram_id)
            self._save_processed_ids()

class TeablePoller:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
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

    def update_status(self, record_ids: list, new_status: str):
        """Update the status of multiple records"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        records = [{"id": record_id, "fields": {"status": new_status}} for record_id in record_ids]
        
        payload = {
            "fieldKeyType": "name",
            "typecast": True,
            "records": records
        }
        
        try:
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Updated status to '{new_status}' for records: {record_ids}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to update record status: {str(e)}")
            return False

    def get_approved_records(self, processed_storage):
        """Get all approved records that need processing"""
        records = self.get_records()
        approved_records = []

        for record in records:
            fields = record.get("fields", {})
            status = fields.get("status")
            telegram_id = fields.get("telegramID")
            telegram_username = fields.get("telegramUsername", "")
            record_id = record.get("id")

            if status == "approved" and telegram_id:
                telegram_id = int(telegram_id)
                if not processed_storage.is_processed(telegram_id, "added"):
                    approved_records.append({
                        "telegram_id": telegram_id,
                        "telegram_username": telegram_username,
                        "record_id": record_id
                    })

        return approved_records

    def get_refused_records(self, processed_storage):
        """Get all refused records that need processing"""
        records = self.get_records()
        refused_records = []

        for record in records:
            fields = record.get("fields", {})
            status = fields.get("status")
            telegram_id = fields.get("telegramID")
            telegram_username = fields.get("telegramUsername", "")
            record_id = record.get("id")

            if status == "refused" and telegram_id:
                telegram_id = int(telegram_id)
                if not processed_storage.is_processed(telegram_id, "removed"):
                    refused_records.append({
                        "telegram_id": telegram_id,
                        "telegram_username": telegram_username,
                        "record_id": record_id
                    })

        return refused_records

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

    def remove_users(self, users, processed_storage):
        """Remove multiple users from the group"""
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

        rights = ChatBannedRights(
            until_date=None,
            view_messages=True,
            send_messages=True,
            send_media=True,
            send_stickers=True,
            send_gifs=True,
            send_games=True,
            send_inline=True,
            embed_links=True
        )

        for user in users:
            try:
                # Try to get user entity first by username if available
                user_entity = None
                if user.get('telegram_username'):
                    try:
                        user_entity = self.client.get_input_entity(user['telegram_username'])
                    except ValueError:
                        pass

                # If username lookup failed, try by ID
                if not user_entity:
                    try:
                        user_entity = self.client.get_input_entity(user['telegram_id'])
                    except ValueError:
                        print(f"Could not find user {user['telegram_id']}. Skipping...")
                        continue

                if not isinstance(user_entity, InputPeerUser):
                    print(f"Skipping user {user['telegram_id']}: Not a user entity")
                    continue

                print(f"Removing user with ID: {user['telegram_id']}")
                
                self.client(EditBannedRequest(
                    target_group_entity,
                    user_entity,
                    rights
                ))
                
                processed_storage.mark_as_processed(user['telegram_id'], "removed")
                successful_records.append(user['record_id'])
                
                print("Waiting 60 seconds before next removal...")
                time.sleep(60)
                
            except Exception as e:
                print(f"Error removing user {user['telegram_id']}: {str(e)}")
                traceback.print_exc()
                error_count += 1
                if error_count > 10:
                    print("Too many errors occurred. Stopping script.")
                    break
                continue
        
        return successful_records
        
    def add_users(self, users, processed_storage):
        """Add multiple users to the group"""
        # Get the target group entity
        try:
            # First try to get the group directly
            target_group = self.client.get_entity(self.group_id)
            if not isinstance(target_group, Channel):
                raise ValueError("Target is not a channel/group")
            
            print(f"Successfully found group: {target_group.title}")
            target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)
        except Exception as e:
            print(f"Error getting group entity directly: {str(e)}")
            # Fallback to using stored hash
            group_hash = os.getenv("TELEGRAM_GROUP_HASH")
            if not group_hash:
                raise ValueError("Could not find group and no access hash provided")
            target_group_entity = InputPeerChannel(self.group_id, int(group_hash))

        error_count = 0
        successful_records = []
        
        for user in users:
            try:
                # Try to get user entity first by username if available
                user_entity = None
                if user.get('telegram_username'):
                    try:
                        print(f"Trying to add user by username: {user['telegram_username']}")
                        user_entity = self.client.get_input_entity(user['telegram_username'])
                    except ValueError as e:
                        print(f"Could not find user by username: {str(e)}")

                # If username lookup failed, try by ID
                if not user_entity:
                    try:
                        print(f"Trying to add user by ID: {user['telegram_id']}")
                        user_entity = self.client.get_input_entity(user['telegram_id'])
                    except ValueError as e:
                        print(f"Could not find user by ID: {str(e)}")
                        print("Please ensure the user has interacted with the bot or provide their username")
                        continue

                if not isinstance(user_entity, InputPeerUser):
                    print(f"Skipping user {user['telegram_id']}: Not a user entity")
                    continue

                print(f"Adding user with ID: {user['telegram_id']}")
                
                self.client(InviteToChannelRequest(
                    channel=target_group_entity,
                    users=[user_entity]
                ))
                
                processed_storage.mark_as_processed(user['telegram_id'], "added")
                successful_records.append(user['record_id'])
                
                print("Waiting 60 seconds before next add...")
                time.sleep(60)
                
            except PeerFloodError:
                print("Getting Flood Error from Telegram. Script should be stopped. Try again after some time.")
                break
            except UserPrivacyRestrictedError:
                print(f"The user {user['telegram_id']} privacy settings do not allow you to add them. Marking as processed.")
                processed_storage.mark_as_processed(user['telegram_id'], "added")
                successful_records.append(user['record_id'])
                continue
            except ChannelInvalidError:
                print("Invalid channel error. Trying to refresh group entity...")
                try:
                    target_group = self.client.get_entity(self.group_id)
                    target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)
                    print("Successfully refreshed group entity")
                    continue  # Retry the current user
                except Exception as refresh_error:
                    print(f"Failed to refresh group entity: {str(refresh_error)}")
                    break
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
    processed_storage = ProcessedIdsStorage()
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))
    
    print(f"""
=== Direct Telegram Group Addition/Removal Service Started ===
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
                # Handle approved records
                approved_records = poller.get_approved_records(processed_storage)
                if approved_records:
                    print(f"\nProcessing {len(approved_records)} approved records")
                    print(f"Telegram IDs: {[r['telegram_id'] for r in approved_records]}")
                    
                    successful_records = manager.add_users(approved_records, processed_storage)
                    
                    if successful_records:
                        if poller.update_status(successful_records, 'telegram'):
                            print(f"Successfully processed {len(successful_records)} approved records")
                        else:
                            print("Failed to update status for approved records")

                # Handle refused records
                refused_records = poller.get_refused_records(processed_storage)
                if refused_records:
                    print(f"\nProcessing {len(refused_records)} refused records")
                    print(f"Telegram IDs: {[r['telegram_id'] for r in refused_records]}")
                    
                    successful_records = manager.remove_users(refused_records, processed_storage)
                    
                    if successful_records:
                        if poller.update_status(successful_records, 'removed'):
                            print(f"Successfully processed {len(successful_records)} refused records")
                        else:
                            print("Failed to update status for refused records")
                
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
