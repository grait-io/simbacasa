from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def get_hash_for_group(channel_identifier: str = "SimbaCasaDev", channel_id: int = None):
    """Get the access hash for a specific channel by username or ID"""
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")
    
    client = TelegramClient(phone, api_id, api_hash)
    
    try:
        client.connect()
        
        if not client.is_user_authorized():
            phone_code_hash = client.send_code_request(phone).phone_code_hash
            try:
                code = input('Enter the code you received: ')
                client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            except PhoneCodeInvalidError:
                print("Invalid code entered.")
                return None
            except SessionPasswordNeededError:
                password = input('Enter your 2FA password: ')
                client.sign_in(password=password)
        
        print("Successfully connected to Telegram!")
        
        try:
            # Try to get entity by ID first if provided
            if channel_id:
                print(f"\nSearching for channel by ID: {channel_id}")
                entity = client.get_entity(channel_id)
            else:
                print(f"\nSearching for channel by username: {channel_identifier}")
                entity = client.get_entity(channel_identifier)
            
            print("\nFound channel!")
            print(f"Title: {entity.title}")
            print(f"ID: {entity.id}")
            print(f"Access Hash: {entity.access_hash}")
            
            # Print full configuration for .env
            print("\nAdd these lines to your .env file:")
            print(f"TELGRAM_GROUP_ID={entity.id}")
            print(f"TELEGRAM_GROUP_HASH={entity.access_hash}")
            
            return entity.access_hash
        except ValueError as e:
            print(f"\nError finding channel: {str(e)}")
            print("\nAvailable groups:")
            print("=" * 80)
            print(f"{'Title':<30} {'ID':<15} {'Access Hash':<20} {'Members':<10}")
            print("-" * 80)
            
            dialogs = client.get_dialogs()
            for dialog in dialogs:
                if hasattr(dialog.entity, 'megagroup') and dialog.entity.megagroup:
                    title = str(dialog.title)
                    if len(title) > 30:
                        title = title[:27] + "..."
                    print(f"{title:<30} {dialog.entity.id:<15} {dialog.entity.access_hash:<20} {getattr(dialog.entity, 'participants_count', 'N/A'):<10}")
            
            print("=" * 80)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        client.disconnect()

def main():
    channel_identifier = "SimbaCasaDev"
    channel_id = None
    
    if len(sys.argv) > 1:
        # Check if the argument is a number (ID) or string (username)
        try:
            channel_id = int(sys.argv[1])
            channel_identifier = None
        except ValueError:
            channel_identifier = sys.argv[1]
            channel_id = None
    
    access_hash = get_hash_for_group(channel_identifier, channel_id)

if __name__ == "__main__":
    main()
