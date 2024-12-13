from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.channels import GetParticipantsRequest, EditBannedRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch, ChatBannedRights, InputPeerChannel, InputPeerUser, ChannelParticipantsBots
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, ChatAdminRequiredError
from dotenv import load_dotenv
import os
import sys
import asyncio

# Load environment variables
load_dotenv()

class TelegramGroupManager:
    def __init__(self):
        # Get credentials from environment variables
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.group_id = int(os.getenv("TELGRAM_GROUP_ID"))
        self.group_hash = int(os.getenv("TELEGRAM_GROUP_HASH"))
        
        # Initialize client
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        
    def connect(self):
        """Connect to Telegram and ensure authorization"""
        self.client.connect()
        
        if not self.client.is_user_authorized():
            # Request the code
            self.client.send_code_request(self.phone)
            code = input('Enter the code you received: ')
            self.client.sign_in(self.phone, code)
            
        return True

    async def get_bot_count(self, target_group):
        """Get the current number of bots in the group"""
        try:
            participants = await self.client(GetParticipantsRequest(
                target_group,
                ChannelParticipantsBots(),
                0,
                100,  # Limit to 100 bots
                hash=0
            ))
            return len(participants.users)
        except Exception as e:
            print(f"Error getting bot count: {str(e)}")
            return 0

    async def add_user(self, username):
        """Add a user to the group"""
        print(f"\nAttempting to add @{username}...")
        
        try:
            # Create the target group entity
            target_group = InputPeerChannel(self.group_id, self.group_hash)
            
            # Check if it's a bot being added
            if username.lower().endswith('_bot'):
                # Get current bot count
                bot_count = await self.get_bot_count(target_group)
                print(f"Current number of bots in group: {bot_count}")
                
                if bot_count >= 20:  # Telegram's limit is 20 bots per group
                    print("\nError: Cannot add more bots. Telegram groups are limited to 20 bots.")
                    print("Please remove some bots first using:")
                    print("python3 list_bot_users.py kick")
                    return
            
            # Get user entity
            try:
                user = await self.client.get_input_entity(username)
            except ValueError:
                print(f"Error: Could not find user @{username}")
                print("Make sure the username is correct and the user/bot exists")
                return
            
            if isinstance(user, InputPeerUser):
                # Add the user
                await self.client(InviteToChannelRequest(
                    target_group,
                    [user]
                ))
                print(f"Successfully added @{username}")
            else:
                print(f"Error: @{username} is not a valid user")
                
        except UserPrivacyRestrictedError:
            print(f"Error: @{username}'s privacy settings prevent adding them to groups")
        except PeerFloodError:
            print("Error: Too many requests. Please wait and try again later")
        except ChatAdminRequiredError:
            print("Error: Admin privileges are required to add users to this group")
        except Exception as e:
            error_msg = str(e)
            if "too many bots" in error_msg.lower():
                print("\nError: Cannot add more bots. Telegram groups are limited to 20 bots.")
                print("Please remove some bots first using:")
                print("python3 list_bot_users.py kick")
            else:
                print(f"Error adding @{username}: {error_msg}")

    async def unban_user(self, username):
        """Unban a user from the group"""
        print(f"\nAttempting to unban @{username}...")
        
        try:
            # Create the target group entity
            target_group = InputPeerChannel(self.group_id, self.group_hash)
            
            # Get user entity
            try:
                user = await self.client.get_input_entity(username)
            except ValueError:
                print(f"Error: Could not find user @{username}")
                print("Make sure the username is correct and the user/bot exists")
                return
            
            # Create unrestricted rights
            rights = ChatBannedRights(
                until_date=None,
                view_messages=False,
                send_messages=False,
                send_media=False,
                send_stickers=False,
                send_gifs=False,
                send_games=False,
                send_inline=False,
                embed_links=False
            )
            
            # Unban the user
            await self.client(EditBannedRequest(
                target_group,
                user,
                rights
            ))
            print(f"Successfully unbanned @{username}")
            
        except ChatAdminRequiredError:
            print("Error: Admin privileges are required to unban users in this group")
        except Exception as e:
            print(f"Error unbanning @{username}: {str(e)}")

    async def list_and_remove_bots(self, should_kick=False):
        """List and optionally remove bots from the target group"""
        print("\nInitializing...")
        
        # Create the target group entity
        target_group = InputPeerChannel(self.group_id, self.group_hash)
        print(f"Target group ID: {self.group_id}")
        
        # Get all participants from the group
        print("Fetching group members...")
        try:
            participants = await self.client(GetParticipantsRequest(
                target_group,
                ChannelParticipantsBots(),
                0,
                100,  # Limit to 100 bots
                hash=0
            ))
            
            bots = participants.users
            print(f"Found {len(bots)} bots in the group")
            
            if should_kick:
                # Create ban rights
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
            
            removed_count = 0
            
            # List and optionally remove bots
            for bot in bots:
                print(f"\nBot found in group:")
                print(f"Username: @{bot.username}")
                print(f"First Name: {bot.first_name}")
                print(f"ID: {bot.id}")
                
                if should_kick:
                    try:
                        print(f"Removing bot @{bot.username} from group...")
                        await self.client(EditBannedRequest(
                            target_group,
                            bot,
                            rights
                        ))
                        removed_count += 1
                        print(f"Successfully removed @{bot.username}")
                        # Wait between kicks to avoid flood limits
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"Error removing @{bot.username}: {str(e)}")
                
                print("-" * 50)
            
            if should_kick:
                print(f"\nSummary:")
                print(f"Total bots in group: {len(bots)}")
                print(f"Successfully removed: {removed_count}")
                print(f"Failed to remove: {len(bots) - removed_count}")
                
        except ChatAdminRequiredError:
            print("Error: Admin privileges are required to view/manage bots in this group")
        except Exception as e:
            print(f"Error: {str(e)}")

    def close(self):
        """Close the Telegram client connection"""
        self.client.disconnect()

def print_usage():
    print("\nUsage:")
    print("1. List bots:   python3 list_bot_users.py")
    print("2. Remove bots: python3 list_bot_users.py kick")
    print("3. Unban user:  python3 list_bot_users.py unban @username")
    print("4. Add user:    python3 list_bot_users.py add @username")

def main():
    # Check if required environment variables are set
    required_vars = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_PHONE", 
                    "TELGRAM_GROUP_ID", "TELEGRAM_GROUP_HASH"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        return

    if len(sys.argv) == 1:
        mode = "list"
    elif len(sys.argv) == 2 and sys.argv[1] == "kick":
        mode = "kick"
    elif len(sys.argv) == 3 and sys.argv[1] in ["unban", "add"]:
        mode = sys.argv[1]
        username = sys.argv[2].lstrip('@')  # Remove @ if present
    else:
        print_usage()
        return

    manager = TelegramGroupManager()
    
    try:
        # Connect to Telegram
        if not manager.connect():
            print("Failed to connect to Telegram. Please try again.")
            return
        
        print("Mode:", mode.upper())
        
        # Run the appropriate async function
        with manager.client:
            if mode == "unban":
                manager.client.loop.run_until_complete(manager.unban_user(username))
            elif mode == "add":
                manager.client.loop.run_until_complete(manager.add_user(username))
            else:
                manager.client.loop.run_until_complete(
                    manager.list_and_remove_bots(mode == "kick")
                )
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        manager.close()

if __name__ == "__main__":
    main()
