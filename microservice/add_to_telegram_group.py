from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, EditBannedRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerUser, InputPeerChannel, ChatBannedRights, Channel
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, ChannelInvalidError
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import requests
import json
import time
import threading
from dotenv import load_dotenv
import os
import sys
import traceback
import re  # Added for ID validation
"""
Purpose:

Automate Telegram group user management
Add or remove users based on record status in a Teable table
Provide webhook notifications for status changes
Key Components:

TeablePoller: Manages interactions with Teable API

Fetches records
Updates record statuses
Calls webhooks for record state changes
TelegramGroupManager: Handles Telegram group interactions

Connects to Telegram API
Adds users to group
Removes users from group
Handles authentication and error scenarios
ProcessedIdsStorage: Tracks processed user IDs

Prevents duplicate actions
Stores processed IDs in a JSON file
Workflow:

Continuously polls Teable table
Processes records with statuses:
"submitted": Send webhook notification
"approved": Add users to Telegram group
"refused": Remove users from Telegram group
Notable Features:

Environment variable configuration
Error handling and logging
Rate limiting (60-second delay between actions)
Optional test webhooks
Support for 2FA Telegram login
The script provides a robust, automated solution for managing Telegram group membership with extensive error handling and logging capabilities.
"""


# Ensure environment variables are loaded
load_dotenv()

def safe_int_convert(value, default=None, error_message=None):
    """
    Safely convert a value to an integer with optional default and error handling.
    
    :param value: Value to convert
    :param default: Default value if conversion fails
    :param error_message: Custom error message to print if conversion fails
    :return: Converted integer or default value
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError) as e:
        if error_message:
            print(error_message)
        if default is None:
            raise
        return default

def get_required_env_var(var_name, default=None, required=True, convert_func=None):
    """
    Retrieve an environment variable with optional type conversion and requirement.
    
    :param var_name: Name of the environment variable
    :param default: Default value if not set (only used if not required)
    :param required: Whether the variable is required
    :param convert_func: Optional function to convert the value
    :return: Value of the environment variable
    """
    value = os.getenv(var_name)
    
    if value is None:
        if required:
            raise ValueError(f"Missing required environment variable: {var_name}")
        return default
    
    if convert_func:
        try:
            return convert_func(value)
        except (ValueError, TypeError) as e:
            if required:
                raise ValueError(f"Invalid value for {var_name}: {str(e)}")
            return default
    
    return value

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""
    pass

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
            return {"added": [], "removed": [], "webhook_received": [], "webhook_accepted": []}
        except Exception as e:
            print(f"Error loading processed IDs: {str(e)}")
            return {"added": [], "removed": [], "webhook_received": [], "webhook_accepted": []}

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
        # Validate and retrieve configuration
        try:
            self.base_url = get_required_env_var("BASE_URL")
            self.api_token = get_required_env_var("TEABLE_API_TOKEN")
            self.table_id = get_required_env_var("TEABLE_TABLE_ID")
            self.telegram_group_id = get_required_env_var("TELGRAM_GROUP_ID")
            
            # Webhook URLs (some can be optional)
            self.n8n_webhook_received_url = get_required_env_var("N8N_WEBHOOK_RECEIVED_URL", required=False)
            self.n8n_webhook_accepted_url = get_required_env_var("N8N_WEBHOOK_ACCEPTED_URL", required=False)
            
            # Test Webhook URLs (optional)
            self.n8n_webhook_test_received_url = get_required_env_var("N8N_WEBHOOK_TEST_RECEIVED_URL", required=False)
            self.n8n_webhook_test_accepted_url = get_required_env_var("N8N_WEBHOOK_TEST_ACCEPTED_URL", required=False)
        except ValueError as e:
            print(f"Configuration Error: {e}")
            sys.exit(1)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
        }
        
        # Print configuration for debugging
        print(f"Using Telegram Group ID: {self.telegram_group_id}")
        print(f"N8N Received Webhook URL: {self.n8n_webhook_received_url}")
        print(f"N8N Accepted Webhook URL: {self.n8n_webhook_accepted_url}")
        print(f"N8N Test Received Webhook URL: {self.n8n_webhook_test_received_url}")
        print(f"N8N Test Accepted Webhook URL: {self.n8n_webhook_test_accepted_url}")

    def is_valid_telegram_id(self, telegram_id):
        """
        Validate Telegram ID.
        Telegram IDs are typically positive integers.
        """
        try:
            # Convert to integer and check if it's a positive number
            id_int = int(telegram_id)
            return id_int > 0
        except (ValueError, TypeError):
            return False

    def get_records(self):
        """Fetch all records from the table"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        try:
            print(f"\nFetching records from: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            records = response.json().get("records", [])
            print(f"Fetched {len(records)} records from table")
            if len(records) > 0:
                print("Sample record fields:", records[0].get("fields", {}))
            return records
        except requests.exceptions.RequestException as e:
            print(f"Error fetching records: {str(e)}")
            return []

    def update_double_status(self, record_id: str, telegram_id: str):
        """Update a record to double status and modify its telegramID"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        payload = {
            "fieldKeyType": "id",
            "typecast": True,
            "records": [{
                "id": record_id,
                "fields": {
                    "fldE151819s5A2x1fnH": "double",  # status field
                    "fldtDljIL5MBhcwoms4": f"double_{telegram_id}"  # telegramID field
                }
            }]
        }
        
        try:
            print(f"Sending PATCH request to update double status: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Updated record {record_id} to double status")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to update record to double status: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response body: {e.response.text}")
            return False

    def update_status(self, record_ids: list, new_status: str):
        """Update the status of multiple records"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        records = [{"id": record_id, "fields": {"fldE151819s5A2x1fnH": new_status}} for record_id in record_ids]
        
        payload = {
            "fieldKeyType": "id",
            "typecast": True,
            "records": records
        }
        
        try:
            print(f"Sending PATCH request to: {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            response = requests.patch(url, headers=self.headers, json=payload)
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")
            response.raise_for_status()
            print(f"Updated status to '{new_status}' for records: {record_ids}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to update record status: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response body: {e.response.text}")
            return False

    def call_webhook(self, webhook_url: str, payload: dict, is_test: bool = False):
        """Generic method to call a webhook"""
        try:
            response = requests.post(
                webhook_url, 
                json=payload, 
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print(f"Successfully called {'test ' if is_test else ''}webhook: {webhook_url}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error calling {'test ' if is_test else ''}webhook {webhook_url}: {str(e)}")
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

            # Skip records with invalid Telegram IDs
            if status == "approved" and telegram_id:
                if not self.is_valid_telegram_id(telegram_id):
                    print(f"Skipping record {record_id} with invalid Telegram ID: {telegram_id}")
                    continue

                telegram_id = int(telegram_id)
                # Commented out processed records check
                #if not processed_storage.is_processed(telegram_id, "added"):
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

            # Skip records with invalid Telegram IDs
            if status == "refused" and telegram_id:
                if not self.is_valid_telegram_id(telegram_id):
                    print(f"Skipping record {record_id} with invalid Telegram ID: {telegram_id}")
                    continue

                telegram_id = int(telegram_id)
                # Commented out processed records check
                #if not processed_storage.is_processed(telegram_id, "removed"):
                refused_records.append({
                    "telegram_id": telegram_id,
                    "telegram_username": telegram_username,
                    "record_id": record_id
                })

        return refused_records

class TelegramGroupManager:
    def __init__(self):
        # Validate and retrieve Telegram configuration using safe conversion
         # [Previous initialization code remains the same]
        self.last_user_add_time = 0
        self.add_user_lock = threading.Lock()
        self.add_user_event = threading.Event()
        try:
            self.api_id = get_required_env_var(
                "TELEGRAM_API_ID", 
                convert_func=int
            )
            self.api_hash = get_required_env_var("TELEGRAM_API_HASH")
            self.phone = get_required_env_var("TELEGRAM_PHONE")
            self.group_id = get_required_env_var(
                "TELGRAM_GROUP_ID", 
                convert_func=int
            )
        except ValueError as e:
            print(f"Telegram Configuration Error: {e}")
            sys.exit(1)
        
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

    def add_users(self, users, processed_storage):
        """Add multiple users to the group with dynamic rate limiting"""
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
        
        def wait_if_needed():
            """Dynamically wait between user additions"""
            with self.add_user_lock:
                current_time = time.time()
                time_since_last_add = current_time - self.last_user_add_time
                
                if time_since_last_add < 60:
                    wait_time = 60 - time_since_last_add
                    print(f"Waiting {wait_time:.2f} seconds before next user addition")
                    time.sleep(wait_time)
                
                self.last_user_add_time = time.time()
        
        for user in users:
            try:
                # Wait dynamically between user additions
                wait_if_needed()

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
                
                #processed_storage.mark_as_processed(user['telegram_id'], "added")
                successful_records.append(user['record_id'])
                
            except PeerFloodError:
                print("Getting Flood Error from Telegram. Script should be stopped. Try again after some time.")
                break
            except UserPrivacyRestrictedError:
                print(f"The user {user['telegram_id']} privacy settings do not allow you to add them.")
                #processed_storage.mark_as_processed(user['telegram_id'], "added")
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

        return successful_records
    
    def close(self):
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
    poll_interval = int(get_required_env_var("POLL_INTERVAL_SECONDS", default="5"))
    
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
                # Fetch all records
                records = poller.get_records()
                
                # Process records
                print("\nChecking records...")
                for record in records:
                    fields = record.get("fields", {})
                    status = fields.get("status")
                    telegram_id = fields.get("telegramID")
                    telegram_username = fields.get("telegramUsername", "")
                    name = fields.get("First name", "")
                    record_id = record.get("id")
                    
                    print(f"Processing record: ID={record_id}, Status={status}, TelegramID={telegram_id}")

                    # Webhook for submitted status
                    if status == "submitted" and telegram_id:
                        print(f"\nFound submitted record with ID {record_id}")
                        
                        # Check for existing records with the same telegramID
                        print(f"\nChecking for existing records with telegramID: {telegram_id}")
                        existing_record = None
                        for r in records:
                            r_fields = r.get("fields", {})
                            r_status = r_fields.get("status")
                            r_telegram_id = r_fields.get("telegramID")
                            print(f"Checking record {r['id']}: status={r_status}, telegramID={r_telegram_id}")
                            if r_telegram_id == telegram_id and r["id"] != record_id and r_status == "telegram":
                                existing_record = r
                                print(f"Found matching record with telegram status!")
                                break
                        
                        if existing_record:
                            print(f"Found existing record with same telegramID: {existing_record['id']}")
                            # Update current record to double status and modify telegramID
                            poller.update_double_status(record_id, telegram_id)
                            continue
                        
                        # If no existing record found, proceed with normal webhook flow
                        print(f"Processing webhook for record {record_id}")
                        webhook_payload = {
                            "telegramID": telegram_id,
                            "telegramUsername": telegram_username,
                            "name": name
                        }
                        print(f"Webhook payload prepared: {webhook_payload}")
                        
                        # Try test webhook first
                        if poller.n8n_webhook_test_received_url:
                            print(f"Attempting test webhook: {poller.n8n_webhook_test_received_url}")
                            test_webhook_success = poller.call_webhook(
                                poller.n8n_webhook_test_received_url, 
                                webhook_payload, 
                                is_test=True
                            )
                        else:
                            print("No test webhook URL configured")
                            test_webhook_success = False
                        
                        # If test webhook fails or doesn't exist, try main webhook
                        if not test_webhook_success:
                            if poller.n8n_webhook_received_url:
                                print(f"Attempting main webhook: {poller.n8n_webhook_received_url}")
                                if poller.call_webhook(poller.n8n_webhook_received_url, webhook_payload):
                                    print(f"Main webhook successful for record {record_id}")
                                    #processed_storage.mark_as_processed(telegram_id, "webhook_received")
                                    print(f"Updating status to pending for record {record_id}")
                                    poller.update_status([record_id], 'pending')
                                else:
                                    print(f"Main webhook failed for record {record_id}")
                            else:
                                print("No main webhook URL configured")
                        #else:
                        #    print(f"Record {record_id} already processed for webhook")

                # Handle approved records
                approved_records = poller.get_approved_records(processed_storage)
                if approved_records:
                    print(f"\nProcessing {len(approved_records)} approved records")
                    print(f"Telegram IDs: {[r['telegram_id'] for r in approved_records]}")
                    
                    successful_records = manager.add_users(approved_records, processed_storage)
                    
                    if successful_records:
                        for record_id in successful_records:
                            record = next((r for r in records if r['id'] == record_id), None)
                            if record:
                                fields = record.get("fields", {})
                                telegram_id = int(fields.get("telegramID"))
                                telegram_username = fields.get("telegramUsername", "")
                                name = fields.get("name", "")
                                
                                # Webhook for telegram status
                                webhook_payload = {
                                    "telegramID": telegram_id,
                                    "telegramUsername": telegram_username,
                                    "name": name
                                }
                                
                                # Try test webhook first
                                test_webhook_success = poller.n8n_webhook_test_accepted_url and poller.call_webhook(
                                    poller.n8n_webhook_test_accepted_url, 
                                    webhook_payload, 
                                    is_test=True
                                )
                                
                                # If test webhook fails or doesn't exist, try main webhook
                                if not test_webhook_success and poller.call_webhook(poller.n8n_webhook_accepted_url, webhook_payload):
                                    #processed_storage.mark_as_processed(telegram_id, "webhook_accepted")
                                    pass  # Added to maintain proper indentation

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
