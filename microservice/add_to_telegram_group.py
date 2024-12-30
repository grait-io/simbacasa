from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, EditBannedRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerUser, InputPeerChannel, ChatBannedRights, Channel
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, ChannelInvalidError, UserNotMutualContactError
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import requests
import json
import time
import threading
from dotenv import load_dotenv
import os
import sys
import traceback
import re
import logging
import logging.handlers
from datetime import datetime

def setup_logging():
    """Configure logging with file rotation and console output"""
    # Get log level from environment variable, default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('telegram_manager')
    logger.setLevel(numeric_level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # File handler with rotation
    log_file = os.path.join(log_dir, 'telegram_manager.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(numeric_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_level)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Ensure environment variables are loaded
load_dotenv()

# Setup logging
logger = setup_logging()

def safe_int_convert(value, default=None, error_message=None):
    """
    Safely convert a value to an integer with optional default and error handling.
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError) as e:
        if error_message:
            logger.error(error_message)
        if default is None:
            raise
        return default

def get_required_env_var(var_name, default=None, required=True, convert_func=None):
    """
    Retrieve an environment variable with optional type conversion and requirement.
    """
    value = os.getenv(var_name)
    
    if value is None:
        if required:
            logger.error(f"Missing required environment variable: {var_name}")
            raise ValueError(f"Missing required environment variable: {var_name}")
        return default
    
    if convert_func:
        try:
            return convert_func(value)
        except (ValueError, TypeError) as e:
            if required:
                logger.error(f"Invalid value for {var_name}: {str(e)}")
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
            logger.error(f"Error loading processed IDs: {str(e)}")
            return {"added": [], "removed": [], "webhook_received": [], "webhook_accepted": []}

    def _save_processed_ids(self):
        """Save processed IDs to storage file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.processed_ids, f)
        except Exception as e:
            logger.error(f"Error saving processed IDs: {str(e)}")

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
            logger.debug(f"Marked Telegram ID {telegram_id} as processed for {action_type}")

class TeablePoller:
    def __init__(self):
        try:
            self.base_url = get_required_env_var("BASE_URL")
            self.api_token = get_required_env_var("TEABLE_API_TOKEN")
            self.table_id = get_required_env_var("TEABLE_TABLE_ID")
            self.telegram_group_id = get_required_env_var("TELGRAM_GROUP_ID")
            
            self.n8n_webhook_received_url = get_required_env_var("N8N_WEBHOOK_RECEIVED_URL", required=False)
            self.n8n_webhook_accepted_url = get_required_env_var("N8N_WEBHOOK_ACCEPTED_URL", required=False)
            self.n8n_webhook_test_received_url = get_required_env_var("N8N_WEBHOOK_TEST_RECEIVED_URL", required=False)
            self.n8n_webhook_test_accepted_url = get_required_env_var("N8N_WEBHOOK_TEST_ACCEPTED_URL", required=False)
        except ValueError as e:
            logger.error(f"Configuration Error: {e}")
            sys.exit(1)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
        }
        
        # Log configuration
        logger.info(f"TeablePoller initialized with group ID: {self.telegram_group_id}")
        logger.debug("Webhook URLs configured:")
        logger.debug(f"- Received: {self.n8n_webhook_received_url}")
        logger.debug(f"- Accepted: {self.n8n_webhook_accepted_url}")
        logger.debug(f"- Test Received: {self.n8n_webhook_test_received_url}")
        logger.debug(f"- Test Accepted: {self.n8n_webhook_test_accepted_url}")

    def is_valid_telegram_id(self, telegram_id):
        """Validate Telegram ID"""
        try:
            id_int = int(telegram_id)
            return id_int > 0
        except (ValueError, TypeError):
            logger.warning(f"Invalid Telegram ID format: {telegram_id}")
            return False

    def get_records_with_filter(self, status):
        """Fetch records with specific status"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        filter_params = {
            "fieldKeyType": "id",
            "filter": json.dumps({"conjunction":"and","filterSet":[{"fieldId":"fldE151819s5A2x1fnH","operator":"is","value":status}]})
        }
        try:
            logger.debug(f"Fetching {status} records from: {url}")
            logger.debug(f"Filter params: {json.dumps(filter_params)}")
            response = requests.get(url, headers=self.headers, params=filter_params)
            response.raise_for_status()
            response_data = response.json()
            logger.debug(f"API Response: {json.dumps(response_data)}")
            records = response_data.get("records", [])
            
            # Log the actual status values we're getting back
            if records:
                statuses = [r.get("fields", {}).get("fldE151819s5A2x1fnH") for r in records]
                logger.debug(f"Status values in response: {statuses}")
            
            total_records = len(records)
            logger.info(f"Fetched {total_records} {status} records")
            
            if len(records) > 0:
                logger.debug(f"Sample record fields: {records[0].get('fields', {})}")
            return records
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {status} records: {str(e)}")
            return []

    def update_double_status(self, record_id: str, telegram_id: str):
        """Update a record to double status"""
        url = f"{self.base_url}/table/{self.table_id}/record"
        payload = {
            "fieldKeyType": "id",
            "typecast": True,
            "records": [{
                "id": record_id,
                "fields": {
                    "fldE151819s5A2x1fnH": "double",
                    "fldtDljIL5MBhcwoms4": f"double_{telegram_id}"
                }
            }]
        }
        
        try:
            logger.debug(f"Updating record {record_id} to double status")
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully updated record {record_id} to double status")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update record to double status: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response body: {e.response.text}")
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
            logger.debug(f"Updating status to '{new_status}' for records: {record_ids}")
            logger.debug(f"Status update payload: {json.dumps(payload)}")
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully updated {len(record_ids)} records to status '{new_status}'")
            logger.debug(f"Status update response: {response.text}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update record status: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response body: {e.response.text}")
            return False

    def call_webhook(self, webhook_url: str, payload: dict, is_test: bool = False):
        """Call a webhook with the given payload"""
        try:
            logger.debug(f"Calling {'test ' if is_test else ''}webhook: {webhook_url}")
            logger.debug(f"Sending webhook request to {webhook_url} with payload: {json.dumps(payload)}")
            response = requests.post(
                webhook_url, 
                json=payload, 
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            logger.info(f"Successfully called {'test ' if is_test else ''}webhook with status code {response.status_code}")
            logger.debug(f"Webhook response: {response.text}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {'test ' if is_test else ''}webhook: {str(e)}")
            return False

    def get_approved_records(self, processed_storage):
        """Get approved records that need processing"""
        # Get approved records and check for telegram username
        records = self.get_records_with_filter("approved")
        approved_records = []

        logger.debug(f"Processing {len(records)} approved records")
        for record in records:
            fields = record.get("fields", {})
            telegram_id = fields.get("fldtDljIL5MBhcwoms4")  # This is the actual field name from Teable
            telegram_username = fields.get("fldt5LbTEuUWxq7iboV", "")  # This appears to be the username field
            record_id = record.get("id")

            logger.debug(f"Processing approved record {record_id} with telegram_id: {telegram_id}, username: {telegram_username}")
            if telegram_id:
                try:
                    telegram_id = int(telegram_id)
                    if telegram_id > 0:
                        approved_records.append({
                            "telegram_id": telegram_id,
                            "telegram_username": telegram_username,  # Keep this for the webhook payload
                            "record_id": record_id
                        })
                        logger.debug(f"Added record {record_id} to approved records with telegram_id: {telegram_id}")
                    else:
                        logger.warning(f"Skipping record {record_id} with non-positive Telegram ID: {telegram_id}")
                except (ValueError, TypeError):
                    logger.warning(f"Skipping record {record_id} with invalid Telegram ID format: {telegram_id}")
            else:
                logger.warning(f"Skipping record {record_id} with missing Telegram ID")

        logger.info(f"Found {len(approved_records)} approved records to process")
        return approved_records

    def get_refused_records(self, processed_storage):
        """Get refused records that need processing"""
        records = self.get_records_with_filter("refused")  # Get all refused records
        refused_records = []

        for record in records:
            fields = record.get("fields", {})
            telegram_id = fields.get("fldtDljIL5MBhcwoms4")  # This is the actual field name from Teable
            telegram_username = fields.get("fldt5LbTEuUWxq7iboV", "")  # This appears to be the username field
            record_id = record.get("id")

            if telegram_id and self.is_valid_telegram_id(telegram_id):
                telegram_id = int(telegram_id)
                refused_records.append({
                    "telegram_id": telegram_id,
                    "telegram_username": telegram_username,
                    "record_id": record_id
                })
            else:
                logger.warning(f"Skipping record {record_id} with invalid Telegram ID: {telegram_id}")

        logger.info(f"Found {len(refused_records)} refused records to process")
        return refused_records

class TelegramGroupManager:
    def __init__(self):
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
            logger.error(f"Telegram Configuration Error: {e}")
            sys.exit(1)
        
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        logger.info("TelegramGroupManager initialized")
        
    def connect(self):
        """Connect to Telegram and ensure authorization"""
        logger.info("Connecting to Telegram...")
        self.client.connect()
        
        if not self.client.is_user_authorized():
            logger.info("Authorization required")
            phone_code_hash = self.client.send_code_request(self.phone).phone_code_hash
            
            try:
                code = input('Enter the code you received: ')
                self.client.sign_in(
                    phone=self.phone,
                    code=code,
                    phone_code_hash=phone_code_hash
                )
            except PhoneCodeInvalidError:
                logger.error("Invalid code entered")
                return False
            except SessionPasswordNeededError:
                logger.info("2FA is enabled, requesting password")
                password = input('Enter your 2FA password: ')
                self.client.sign_in(password=password)
        
        logger.info("Successfully connected to Telegram")
        return True

    def get_groups(self):
        """Get all groups and their details"""
        logger.info("Fetching all groups...")
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
                    title = str(chat.title)
                    if len(title) > 30:
                        title = title[:27] + "..."
                    
                    groups.append({
                        'title': title,
                        'id': str(chat.id),
                        'access_hash': str(chat.access_hash),
                        'members_count': str(getattr(chat, 'participants_count', 'N/A'))
                    })
            except Exception as e:
                logger.error(f"Error processing chat: {str(e)}")
                continue
        
        if not groups:
            logger.warning("No groups found!")
            return []
        
        logger.info(f"Found {len(groups)} groups")
        for g in groups:
            logger.debug(f"Group: {g['title']} (ID: {g['id']}, Members: {g['members_count']})")
        
        target_id = str(self.group_id)
        target_group = next((g for g in groups if g['id'] == target_id), None)
        
        if target_group:
            logger.info(f"Target group found: {target_group['title']}")
            logger.debug(f"Access Hash: {target_group['access_hash']}")
        else:
            logger.warning(f"Target group with ID {target_id} not found!")
        
        return groups

    def add_users(self, users, processed_storage, poller):
        """Add multiple users to the group"""
        logger.info(f"Adding {len(users)} users to group")
        try:
            target_group = self.client.get_entity(self.group_id)
            if not isinstance(target_group, Channel):
                raise ValueError("Target is not a channel/group")
            
            logger.info(f"Using group: {target_group.title}")
            target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)
        except Exception as e:
            logger.error(f"Error getting group entity: {str(e)}")
            group_hash = os.getenv("TELEGRAM_GROUP_HASH")
            if not group_hash:
                logger.error("Could not find group and no access hash provided")
                raise ValueError("Could not find group and no access hash provided")
            target_group_entity = InputPeerChannel(self.group_id, int(group_hash))

        successful_records = []
        
        def wait_if_needed():
            with self.add_user_lock:
                current_time = time.time()
                time_since_last_add = current_time - self.last_user_add_time
                
                if time_since_last_add < 60:
                    wait_time = 60 - time_since_last_add
                    logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
                
                self.last_user_add_time = time.time()
        
        for user in users:
            try:
                wait_if_needed()

                user_entity = None
                # Only try to add users who have a username
                if not user.get('telegram_username'):
                    logger.info(f"User {user['telegram_id']} has no username, sending to webhook flow")
                    webhook_payload = {
                        "telegramID": user['telegram_id'],
                        "telegramUsername": ""
                    }

                    # Try test webhook first
                    test_webhook_url = os.getenv("N8N_WEBHOOK_INVITE_TEST_URL")
                    if test_webhook_url:
                        try:
                            logger.info(f"Calling test invite webhook for user {user['telegram_id']}")
                            response = requests.post(test_webhook_url, json=webhook_payload)
                            response.raise_for_status()
                            logger.info(f"Successfully called test invite webhook for user {user['telegram_id']}")
                            # Update status to invited
                            poller.update_status([user['record_id']], 'invited')
                            successful_records.append(user['record_id'])
                            continue
                        except Exception as webhook_error:
                            logger.warning(f"Test invite webhook failed: {str(webhook_error)}, falling back to production webhook")

                    # Fall back to production webhook
                    prod_webhook_url = os.getenv("N8N_WEBHOOK_INVITE_URL")
                    if prod_webhook_url:
                        try:
                            logger.info(f"Calling production invite webhook for user {user['telegram_id']}")
                            response = requests.post(prod_webhook_url, json=webhook_payload)
                            response.raise_for_status()
                            logger.info(f"Successfully called production invite webhook for user {user['telegram_id']}")
                            # Update status to invited
                            poller.update_status([user['record_id']], 'invited')
                            successful_records.append(user['record_id'])
                        except Exception as webhook_error:
                            logger.error(f"Production invite webhook failed: {str(webhook_error)}")
                            # Check if it's a 500 error
                            if hasattr(webhook_error, 'response') and webhook_error.response.status_code == 500:
                                logger.info(f"Server returned 500 error, updating status to blocked for user {user['telegram_id']}")
                                poller.update_status([user['record_id']], 'blocked')
                    continue

                try:
                    logger.debug(f"Trying to add user by username: {user['telegram_username']}")
                    user_entity = self.client.get_input_entity(user['telegram_username'])
                except ValueError as e:
                    logger.warning(f"Could not find user by username: {str(e)}")
                    continue

                if not isinstance(user_entity, InputPeerUser):
                    logger.warning(f"Skipping user {user['telegram_id']}: Not a user entity")
                    continue

                logger.info(f"Adding user {user['telegram_id']} to group")
                
                self.client(InviteToChannelRequest(
                    channel=target_group_entity,
                    users=[user_entity]
                ))
                
                successful_records.append(user['record_id'])
                logger.info(f"Successfully added user {user['telegram_id']}")
                
            except PeerFloodError:
                logger.error("Telegram flood error detected. Stopping user addition.")
                break
            except UserPrivacyRestrictedError:
                logger.warning(f"User {user['telegram_id']} has privacy restrictions")
                
                # Call webhook for users with privacy restrictions
                webhook_payload = {
                    "telegramID": user['telegram_id'],
                    "telegramUsername": user.get('telegram_username', '')
                }

                # Try test webhook first
                test_webhook_url = os.getenv("N8N_WEBHOOK_INVITE_TEST_URL")
                if test_webhook_url:
                    try:
                        logger.info(f"Calling test invite webhook for user {user['telegram_id']}")
                        response = requests.post(test_webhook_url, json=webhook_payload)
                        response.raise_for_status()
                        logger.info(f"Successfully called test invite webhook for user {user['telegram_id']}")
                        # Update status to invited
                        poller.update_status([user['record_id']], 'invited')
                        successful_records.append(user['record_id'])
                        continue
                    except Exception as webhook_error:
                        logger.warning(f"Test invite webhook failed: {str(webhook_error)}, falling back to production webhook")

                # Fall back to production webhook if test webhook failed or doesn't exist
                prod_webhook_url = os.getenv("N8N_WEBHOOK_INVITE_URL")
                if prod_webhook_url:
                    try:
                        logger.info(f"Calling production invite webhook for user {user['telegram_id']}")
                        response = requests.post(prod_webhook_url, json=webhook_payload)
                        response.raise_for_status()
                        logger.info(f"Successfully called production invite webhook for user {user['telegram_id']}")
                        # Update status to invited
                        poller.update_status([user['record_id']], 'invited')
                    except Exception as webhook_error:
                        logger.error(f"Production invite webhook failed: {str(webhook_error)}")
                        # Check if it's a 500 error
                        if hasattr(webhook_error, 'response') and webhook_error.response.status_code == 500:
                            logger.info(f"Server returned 500 error, updating status to blocked for user {user['telegram_id']}")
                            poller.update_status([user['record_id']], 'blocked')
                        
                successful_records.append(user['record_id'])
                continue
            except ChannelInvalidError:
                logger.error("Invalid channel error. Attempting to refresh group entity...")
                try:
                    target_group = self.client.get_entity(self.group_id)
                    target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)
                    logger.info("Successfully refreshed group entity")
                    continue
                except Exception as refresh_error:
                    logger.error(f"Failed to refresh group entity: {str(refresh_error)}")
                    break
            except UserNotMutualContactError:
                logger.warning(f"User {user['telegram_id']} is not a mutual contact")
                
                # Call webhook for users who are not mutual contacts
                webhook_payload = {
                    "telegramID": user['telegram_id'],
                    "telegramUsername": user.get('telegram_username', '')
                }

                # Try test webhook first
                test_webhook_url = os.getenv("N8N_WEBHOOK_INVITE_TEST_URL")
                if test_webhook_url:
                    try:
                        logger.info(f"Calling test invite webhook for user {user['telegram_id']}")
                        response = requests.post(test_webhook_url, json=webhook_payload)
                        response.raise_for_status()
                        logger.info(f"Successfully called test invite webhook for user {user['telegram_id']}")
                        # Update status to invited
                        poller.update_status([user['record_id']], 'invited')
                        successful_records.append(user['record_id'])
                        continue
                    except Exception as webhook_error:
                        logger.warning(f"Test invite webhook failed: {str(webhook_error)}, falling back to production webhook")

                # Fall back to production webhook if test webhook failed or doesn't exist
                prod_webhook_url = os.getenv("N8N_WEBHOOK_INVITE_URL")
                if prod_webhook_url:
                    try:
                        logger.info(f"Calling production invite webhook for user {user['telegram_id']}")
                        response = requests.post(prod_webhook_url, json=webhook_payload)
                        response.raise_for_status()
                        logger.info(f"Successfully called production invite webhook for user {user['telegram_id']}")
                        # Update status to invited
                        poller.update_status([user['record_id']], 'invited')
                    except Exception as webhook_error:
                        logger.error(f"Production invite webhook failed: {str(webhook_error)}")
                        # Check if it's a 500 error
                        if hasattr(webhook_error, 'response') and webhook_error.response.status_code == 500:
                            logger.info(f"Server returned 500 error, updating status to blocked for user {user['telegram_id']}")
                            poller.update_status([user['record_id']], 'blocked')
                        
                successful_records.append(user['record_id'])
                continue
            except Exception as e:
                logger.error(f"Unexpected error while adding user {user['telegram_id']}: {str(e)}")
                logger.error(traceback.format_exc())

        return successful_records
    
    def close(self):
        """Close the Telegram client connection"""
        logger.info("Closing Telegram client connection")
        self.client.disconnect()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--list-groups':
        logger.info("Running in list-groups mode")
        manager = TelegramGroupManager()
        try:
            if manager.connect():
                manager.get_groups()
        finally:
            manager.close()
        return

    poller = TeablePoller()
    manager = TelegramGroupManager()
    processed_storage = ProcessedIdsStorage()
    poll_interval = int(get_required_env_var("POLL_INTERVAL_SECONDS", default="5"))
    
    logger.info(f"""
=== Direct Telegram Group Addition/Removal Service Started ===
Polling interval: {poll_interval} seconds
Table ID: {poller.table_id}
Telegram Group ID: {poller.telegram_group_id}
    """)
    
    try:
        if not manager.connect():
            logger.error("Failed to connect to Telegram")
            return
        
        if not os.getenv("TELEGRAM_GROUP_HASH"):
            logger.warning("TELEGRAM_GROUP_HASH not found in .env")
            manager.get_groups()
            logger.info("Please add the access hash to your .env file and restart the script")
            return
        
        while True:
            try:
                # Get submitted records using filter
                submitted_records = poller.get_records_with_filter("submitted")  # Get all submitted records
                for record in submitted_records:
                    fields = record.get("fields", {})
                    telegram_id = fields.get("fldtDljIL5MBhcwoms4")  # This is the actual field name from Teable
                    telegram_username = fields.get("fldt5LbTEuUWxq7iboV", "")  # This appears to be the username field from logs
                    name = fields.get("First name", "")  # Keep this as is since we don't see it in logs
                    record_id = record.get("id")
                    
                    logger.debug(f"Record {record_id} fields: {json.dumps(fields)}")
                    logger.debug(f"Telegram ID from record: {telegram_id} (type: {type(telegram_id)})")
                    
                    if telegram_id:
                        logger.info(f"Processing submitted record {record_id}")
                        
                        # Check for existing record with same Telegram ID
                        existing_records = poller.get_records_with_filter("telegram")  # Get all telegram records
                        logger.debug(f"Checking for duplicates of Telegram ID {telegram_id} among {len(existing_records)} existing records")
                        
                        existing_record = None
                        for r in existing_records:
                            existing_telegram_id = r.get("fields", {}).get("fldtDljIL5MBhcwoms4")
                            # Convert both IDs to strings for comparison to handle potential type mismatches
                            if str(existing_telegram_id) == str(telegram_id) and r["id"] != record_id:
                                existing_record = r
                                logger.debug(f"Found match: Record {r['id']} has Telegram ID {existing_telegram_id}")
                                break
                            else:
                                logger.debug(f"No match: Record {r['id']} has Telegram ID {existing_telegram_id}")
                        
                        if existing_record:
                            logger.info(f"Found existing record {existing_record['id']} with Telegram ID {telegram_id}")
                            logger.info(f"Updating record {record_id} to double status")
                            poller.update_double_status(record_id, telegram_id)
                            continue
                        
                        # No duplicate found, proceed with normal flow
                        logger.info(f"No duplicate found for Telegram ID {telegram_id}, proceeding with webhook")
                        webhook_payload = {
                            "telegramID": telegram_id,
                            "telegramUsername": telegram_username,
                            "name": name
                        }
                        
                        # Try test webhook first if configured
                        test_webhook_success = False
                        if poller.n8n_webhook_test_received_url:
                            logger.info(f"Attempting test webhook for record {record_id}")
                            test_webhook_success = poller.call_webhook(
                                poller.n8n_webhook_test_received_url, 
                                webhook_payload, 
                                is_test=True
                            )
                            if test_webhook_success:
                                logger.info(f"Test webhook successful for record {record_id}, updating to pending")
                                status_update_success = poller.update_status([record_id], 'pending')
                                if not status_update_success:
                                    logger.error(f"Failed to update record {record_id} to pending status after successful test webhook")
                        
                        # If test webhook not configured or failed, try main webhook
                        if not test_webhook_success:
                            if poller.n8n_webhook_received_url:
                                logger.info(f"Attempting main webhook for record {record_id}")
                                if poller.call_webhook(poller.n8n_webhook_received_url, webhook_payload):
                                    logger.info(f"Main webhook successful for record {record_id}, updating to pending")
                                    status_update_success = poller.update_status([record_id], 'pending')
                                    if not status_update_success:
                                        logger.error(f"Failed to update record {record_id} to pending status after successful main webhook")
                                else:
                                    logger.warning(f"Main webhook failed for record {record_id}, status will remain submitted")
                            else:
                                logger.warning("No webhooks configured, record will remain in submitted status")

                approved_records = poller.get_approved_records(processed_storage)
                if approved_records:
                    logger.info(f"Processing {len(approved_records)} approved records")
                    successful_records = manager.add_users(approved_records, processed_storage, poller)
                    
                    if successful_records:
                        for record_id in successful_records:
                            # Find the matching approved record to get its details
                            approved_record = next((r for r in approved_records if r['record_id'] == record_id), None)
                            if approved_record:
                                webhook_payload = {
                                    "telegramID": approved_record['telegram_id'],
                                    "telegramUsername": approved_record['telegram_username'],
                                    "recordId": record_id
                                }
                                
                                webhook_success = False
                                if poller.n8n_webhook_test_accepted_url:
                                    webhook_success = poller.call_webhook(
                                        poller.n8n_webhook_test_accepted_url, 
                                        webhook_payload, 
                                        is_test=True
                                    )
                                
                                if not webhook_success:
                                    poller.call_webhook(poller.n8n_webhook_accepted_url, webhook_payload)

                        if poller.update_status(successful_records, 'telegram'):
                            logger.info(f"Successfully processed {len(successful_records)} approved records")
                        else:
                            logger.error("Failed to update status for approved records")

                refused_records = poller.get_refused_records(processed_storage)
                if refused_records:
                    logger.info(f"Processing {len(refused_records)} refused records")
                    successful_records = manager.remove_users(refused_records, processed_storage)
                    
                    if successful_records:
                        if poller.update_status(successful_records, 'removed'):
                            logger.info(f"Successfully processed {len(successful_records)} refused records")
                        else:
                            logger.error("Failed to update status for refused records")
                
                time.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                logger.error(traceback.format_exc())
                time.sleep(poll_interval)
                
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        manager.close()

if __name__ == "__main__":
    main()
