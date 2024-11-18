from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def get_hash_for_group(channel_username: str = "SimbaCasaDev"):
    """Get the access hash for a specific channel username"""
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
        print(f"\nSearching for channel: {channel_username}")
        
        try:
            entity = client.get_entity(channel_username)
            print("\nFound channel!")
            print(f"Title: {entity.title}")
            print(f"ID: {entity.id}")
            print(f"Access Hash: {entity.access_hash}")
            return entity.access_hash
        except ValueError:
            print(f"\nNo channel found with username {channel_username}")
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        client.disconnect()

def main():
    channel_username = "SimbaCasaDev"
    if len(sys.argv) > 1:
        channel_username = sys.argv[1]
    
    access_hash = get_hash_for_group(channel_username)
    
    if access_hash is not None:
        print("\nTo use this hash, add it to your .env file:")
        print(f"TELEGRAM_GROUP_HASH={access_hash}")

if __name__ == "__main__":
    main()