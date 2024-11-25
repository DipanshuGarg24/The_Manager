from telegram import Update, InlineQueryResultArticle, InputTextMessageContent,InlineKeyboardMarkup,InlineKeyboardButton,\
    ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, ContextTypes, MessageHandler, filters, \
    InlineQueryHandler, CallbackQueryHandler
# from telegram.ext import Updater, CommandHandler

import nest_asyncio
import asyncio
import os
from metaDataManager import *


# Allows nesting of asyncio event loops
nest_asyncio.apply()

API_TOKEN = '7771920988:AAFctEc-EZ7jCsxgnmTeSDvR5vj4N_uFiRw'  # Replace with your bot's API token
CHANNEL_ID = '-1002483574835'  # Replace with your actual channel ID

# crdir -  current directory

# -------------------
crdir = "root"
# --------------------
file_storage = {}
#manager :)
managers = {}
# manager = MetadataManager()

async def start(update: Update, context: CallbackContext) -> None:

    user = update.message.from_user  # Get the user information
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name or ''  # Handle case where last name is not provided
    name = first_name+" "+last_name
    
    managers[user_id] = MetadataManager()
    manager = managers[user_id]
    # set the active user :)
    # and get the number of channels that are connected
    msg1 = f'''
        Hi {name}
    
I am Your Channel File Manager 
        
Currently You are not connected with any Group , please connect any Group to start managaing the files :)
command /help to know about the commands and the steps to use the bot properly
        
Thanks
    '''
    grpdata = manager.SetActiveUser(user_id)
    msg2 = f'''
        Hi {name}
        
I am Your Group File Manager
        
You are connected with {manager.group_count} Groups
    '''

    keyboard = []
        # [InlineKeyboardButton("Say Hi", callback_data='hi')],
        # [InlineKeyboardButton("Check Status", callback_data='status')]
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)

    if manager.group_count == 0:
        await update.message.reply_text(msg1)
    else:
        for i in grpdata:
            keyboard.append([InlineKeyboardButton(i[1], callback_data=f'select_{i[0]}_{i[1]}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
        msg2+= "\n Click to select the Group \n use /help command to know about commands and the steps to use the bot properly :) "
        await update.message.reply_text(msg2,reply_markup=reply_markup)

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user = update.message.from_user  # Get the user information
    query = update.callback_query
    manager = managers[query.from_user.id]
    await query.answer()
    # print("hello what happen :) ")
    # Simulate command invocation
    x = query.data
    x = x.split("_")
    if x[0] == "select":
        # here i will run the select command simple :) 
        await query.message.reply_text(manager.selectGroup(x[1],x[2]))
    else:
        pass
        # await check_status(query, context)

async def help(update: Update,context:CallbackContext) ->None:
    '''if there is any requirement of the help then this command will run'''
    msg = """
    /command1 : usecase1 
    /command2 : usecase2
    /command3 : usecase3
    /command4 : usecase4
    /command5 : usecase5
    """
    await update.message.reply_text(msg)


async def forward_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager = managers[update.message.from_user.id]
    if update.message.document:
        # Ask the user for the file name
        if update.message.document != None:
            print(update.message.document.file_name)
        else:
            await update.message.reply_text("PLease send the files as the document/file ")
            return
        
        document = update.message.document
        # send the file to the group :) 
        try:
            sent_message = await context.bot.send_document(
                chat_id= manager.GROUP_ID,
                document=document.file_id,
                caption=document.file_name
            )
            # adding into the filsystem
            if manager.add_file(document.file_name,"file",sent_message.message_id,False):
                await update.message.reply_text(f'File has been stored with the name "{document.file_name}"!\n')
            else:
                await update.message.reply_text("file already exits in the directory :)")

        except Exception as e:
            await update.message.reply_text(e)
    elif update.message.media_group_id:  # Multiple documents as a media group
        for doc in update.message.media_group:
            print(doc.filename)

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chat has been cleared! (Note: Old messages can't be deleted)")
    await start(update, context)  # Optionally restart the conversation

async def access_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager = managers[update.message.from_user.id]
    file_name = ' '.join(context.args)  # Get the file name from the command arguments
    id = manager.search_file(file_name)
    if id != -1:
        # Forward the file from the channel to the user
        # Extract the message ID from the link
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=manager.GROUP_ID,
            message_id=id
        )
        # await update.message.reply_text(f'Here is your file: {file_link}')
    else:
        await update.message.reply_text('File not found. Please check the name and try again.')

async def genrate_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager = managers[update.message.from_user.id]
    file_name = ' '.join(context.args)  # Get the file name from the command arguments
    message_id = manager.search_file(file_name)
    if id != -1:
        # Forward the file from the channel to the user
        # Extract the message ID from the link
        try:
        # Get the message ID from user input
            chat_id = manager.GROUP_ID
            # Fetch the message using the message ID
            message = context.bot.get_message(chat_id, message_id)

            # Check if the message contains a file/document
            if not message.document:
                await update.message.reply_text("No file found in the specified message.")
                return

            # Extract the file ID
            file_id = message.document.file_id
            # Get the file path using file_id
            file_info = context.bot.get_file(file_id)
            file_path = file_info.file_path

            # Generate the direct download link
            download_link = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

            # Send the download link back to the user
            await update.message.reply_text(f"Download your file here: {download_link}")

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}")

        # await update.message.reply_text(f'Here is your file: {file_link}')
    else:
        await update.message.reply_text('File not found. Please check the name and try again.')


async def read_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_name = ' '.join(context.args)  # Get the file name from the command arguments
    manager = managers[update.message.from_user.id]
    if file_name in file_storage:
        # Retrieve the file_id from storage
        file_id = file_storage[file_name][0]
        file_link = file_storage[file_name][1]
        message_id = file_link.split('/')[-1]

        try:
            # Download the file using its file_id
            file = await context.bot.get_file(file_id)

            # Define the local path to save the file
            local_file_path = f"./{file_name}"

            # Download the file locally
            await file.download_to_drive(local_file_path)

            # Read and send the content of the file
            try:
                with open(local_file_path, 'r') as f:
                    content = f.read()
                    await update.message.reply_text(f"Contents of '{file_name}':\n\n{content}")
            except Exception as read_error:
                await update.message.reply_text(f"Error reading the file '{file_name}': {str(read_error)}")

            # Optionally, remove the local file after reading it
            os.remove(local_file_path)

        except Exception as e:
            await update.message.reply_text(f"Error accessing the file: {str(e)}")

    else:
        await update.message.reply_text('File not found. Please check the name and try again.')

async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager = managers[update.message.from_user.id]
    file_name = ' '.join(context.args)  # Get the file name from the command arguments
    if file_name in file_storage:
        # Get the file link from the storage
        file_link = file_storage[file_name][1]
        message_id = int(file_link.split('/')[-1])  # Extract the message ID from the link

        try:
            # Delete the message containing the file from the channel
            await context.bot.delete_message(
                chat_id=manager.GROUP_ID,
                message_id=message_id
            )
            await update.message.reply_text(f'File "{file_name}" has been deleted successfully.')
        except Exception as e:
            await update.message.reply_text(f"Error deleting the file: {str(e)}")
    else:
        await update.message.reply_text('File not found. Please check the name and try again.')

async def register(update: Update, context: CallbackContext) -> None:
    """register the channel to the bot to monitoring"""
    # fetch the channel id and the message :)
    # manager = managers[update.message.from_user.id]
    print(update)
    group_id = update.message.chat.id
    try:
        x = MetadataManager.AddGroup(
                    update.message.chat.title,
                    update.message.from_user.id,
                    group_id)
        if x == 1:
            await update.message.reply_text("Group is Successfully registered :) ")
        elif x == 2:
            await update.message.reply_text("Group is already Registered :)")
    except Exception as e:
        print("Unable to Register the Channel")
        print(f"Exception error : {e}")

async def make_dir(update:Update, context:ContextTypes.DEFAULT_TYPE):
    dirname = ' '.join(context.args)
    manager = managers[update.message.from_user.id]
    #  then simple call the 
    if manager.mkdir(dirname):
        await update.message.reply_text("Directory is successfully created :) ")
    else:
        await update.message.reply_text("Directory with this name already exits :)")

async def change_dir(update:Update, context:ContextTypes.DEFAULT_TYPE):
    #  add the functionality to make the directory in the file system :) 
    dirname = ' '.join(context.args)
    manager = managers[update.message.from_user.id]
    #  then simple call the 
    if manager.cdir(dirname):
        await update.message.reply_text(f"Cur Dir : {manager.GROUP_N}:{manager.path}")
    else:
        await update.message.reply_text("Invalid Path :(")

async def listfile(update:Update, context:ContextTypes.DEFAULT_TYPE):
    #  add the functionality to make the directory in the file system :) 
    manager = managers[update.message.from_user.id]
    if context.args == None:
        dirname = ""
    else:
        dirname = ' '.join(context.args)
    #  then simple call the 
    x =manager.ls(dirname)
    
    if x != []:
        # msg = ""
        keyboard = []  # Initialize the keyboard list
        for i in x:
            # Set the icon based on the type (dir or file)
            icon = "📂" if i[1] == "dir" else "📄"
            # Append each file/directory as a button
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{icon} {i[0]}",  # Display the icon and name
                    callback_data="pass"  # Placeholder callback data
                )
            ])

        # Create an InlineKeyboardMarkup object
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the message with the inline keyboard
        await update.message.reply_text(
            "List:",  # Message text
            reply_markup=reply_markup  # Attach the inline keyboard
        )
        # z = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        # await update.messsage.reply_text("List : ",reply_markup=reply_markup)
    else:
        await update.message.reply_text("Directory is Empty :)")

async def remove_file(update:Update, context:ContextTypes.DEFAULT_TYPE):
    #  add the functionality to make the directory in the file system :) 
    manager = managers[update.message.from_user.id]
    dirname = ' '.join(context.args)
    #  then simple call the 
    if manager.rm(dirname):
        await update.message.reply_text(f"Deletion succesfull :)")
    else:
        await update.message.reply_text("Invalid Dir/File")

async def change_dir(update:Update, context:ContextTypes.DEFAULT_TYPE):
    manager = managers[update.message.from_user.id]
    await update.message.reply_text(f"Cur Dir : {manager.GROUP_N}:{manager.path}")
        
async def main():
    application = ApplicationBuilder().token(API_TOKEN).build()

    # Private chat-only commands
    private_filter = filters.ChatType.PRIVATE
    application.add_handler(CommandHandler("start", start, filters=private_filter))
    application.add_handler(CommandHandler("clear", clear_chat, filters=private_filter))
    application.add_handler(CommandHandler("help", help, filters=private_filter))
    application.add_handler(CommandHandler("get", access_file, filters=private_filter))
    application.add_handler(CommandHandler("cd", change_dir, filters=private_filter))
    application.add_handler(CommandHandler("mkdir", make_dir, filters=private_filter))
    application.add_handler(CommandHandler("ls", listfile, filters=private_filter))
    application.add_handler(CommandHandler("rm",remove_file, filters=private_filter))
    application.add_handler(CommandHandler("share",genrate_download, filters=private_filter))
    application.add_handler(CommandHandler("pwd",change_dir, filters=private_filter))
    # File upload handler (in private chat)
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO & private_filter, forward_file))

    # Filename receiving handler (in private chat)
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & private_filter, receive_filename))

    # Group-only command
    group_filter = filters.ChatType.GROUP
    application.add_handler(CommandHandler("register", register, filters=group_filter))
    application.add_handler(CallbackQueryHandler(handle_callbacks))
    # Start polling updates from Telegram
    await application.run_polling()


# Run the bot in an interactive environment
if __name__ == '__main__':
    asyncio.run(main())
