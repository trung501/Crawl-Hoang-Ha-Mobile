import logging
from typing import Optional, Tuple
import time
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Chat, ChatMember, ChatMemberUpdated, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

info={}
index=-1
cauhoi=[]
traLoiDung=[]
daTraLoi=[]
def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            # This may not be really needed in practice because most clients will automatically
            # send a /start command after the user unblocks the bot, and start_private_chat()
            # will add the user to "user_ids".
            # We're including this here for the sake of the example.
            logger.info("%s unblocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    else:
        if not was_member and is_member:
            logger.info("%s added the bot to the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).discard(chat.id)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text=f"""Today we have a little game for everyone \nwe have added you to the group to play \ngames on telegram and on the current screen \nwill show the content of the group's reply messages\nthere are 12 questions related to the present perfect tense, each question will have 15 seconds to answer and each time a question is finished, the number of people who answered correctly will appear. At the end of the game whoever answers the most questions correctly wins\nThe syntax to answer the question is virgule /a + Answer\n Example: /a B"""
    await update.effective_message.reply_text(text)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows which chats the bot is in"""
    name= str(update.effective_user.first_name)
    # get content
    content = update.message.text
    content = content.replace("/a ", "").strip()
    # get user id
    user_id = update.message.from_user.id
    # get user name
    user_name = update.message.from_user.username
    print("content: ", content)
    print("user_id: ", user_id)
    print("user_name: ", user_name)
    print("name: ", name)
    if user_id in daTraLoi:
        await update.effective_message.reply_text(f"{name} chỉ được trả lời một lần thôi, tham .")
        return
    daTraLoi.append(user_id)
    if user_id not in info:
        info[user_id]={"name":name,"number":0}
    if content.strip().lower() == cauhoi[index]["dapan"].lower():
        info[user_id]["number"]+=1
        traLoiDung.append(user_id)
        print(info[user_id]["name"] , info[user_id]["number"])
    # await update.effective_message.reply_text(f"Ok {name}, your answer is {content}")

def get_quesion():
    global index,cauhoi
    if index > len(cauhoi)-1:
        message = "Het cau hoi"
    else:
        message = "Quesion: "+cauhoi[index]["cauhoi"]+"\n"
        message += "A: "+cauhoi[index]["A"]+"\n"
        message += "B: "+cauhoi[index]["B"]+"\n"
        message += "C: "+cauhoi[index]["C"]+"\n"
        message += "D: "+cauhoi[index]["D"]+"\n"
    return message

async def next_quesion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global index,traLoiDung,daTraLoi
    traLoiDung=[]
    daTraLoi=[]
    user_id = update.message.from_user.id
    if user_id == 1016719068:
        index+=1
        await update.effective_message.reply_text(get_quesion())
    else:
        await update.effective_message.reply_text("You not permission")

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer=f"Question: {cauhoi[index]['cauhoi']}\n"
    answer+=f"Answer: {cauhoi[index]['dapan']}\n"
    answer+=f"Number of people answered correctly: {len(traLoiDung)}\n"
    answer+=f"List of people who answered correctly: \n"
    for i in traLoiDung:
        answer+=f"{info[i]['name']}\n"
    await update.effective_message.reply_text(answer)
    
async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global info
    # sort info by number
    info = dict(sorted(info.items(), key=lambda item: item[1]["number"],reverse=True))
    # write finish
    message="Finish\nCongratulation  everyone\nList top:\n"
    for user in info:
        message+=f"{info[user]['name']}: {info[user]['number']} point \n"
    await update.effective_message.reply_text(message)







async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets new users in chats and announces when someone leaves"""
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        await update.effective_chat.send_message(
            f"{member_name} was added by {cause_name}. Welcome!",
            parse_mode=ParseMode.HTML,
        )
    elif was_member and not is_member:
        await update.effective_chat.send_message(
            f"{member_name} is no longer with us. Thanks a lot, {cause_name} ...",
            parse_mode=ParseMode.HTML,
        )


async def start_private_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and records that they started a chat with the bot if it's a private chat.
    Since no `my_chat_member` update is issued when a user starts a private chat with the bot
    for the first time, we have to track it explicitly here.
    """
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    if chat.type != Chat.PRIVATE or chat.id in context.bot_data.get("user_ids", set()):
        return

    logger.info("%s started a private chat with the bot", user_name)
    context.bot_data.setdefault("user_ids", set()).add(chat.id)

    await update.effective_message.reply_text(
        f"Welcome {user_name}. Use /show_chats to see what chats I'm in."
    )




def main() -> None:
    cauhoi.append({"cauhoi":"When ____________ the school?","dapan":"C","A":"have you joined","B":"did you joined","C":"did you join","D":"have you ever joined"})
    cauhoi.append({"cauhoi":"_____________ in England?","dapan":"B","A":"Did you ever worked","B":"Have you ever worked","C":"Worked you","D":"Didn't you have worked"})
    cauhoi.append({"cauhoi":"That's the best speech _________","dapan":"D","A":"I never heard","B":"I didn't hear","C":"I used to hear","D":"I've ever heard"})
    cauhoi.append({"cauhoi":"He's the most difficult housemate _____________________","dapan":"C","A":"I never dealt with.","B":"I never had to deal with.","C":"I've ever had to deal with.","D":"I've never had to deal with"})
    cauhoi.append({"cauhoi":"______ to him last week.","dapan":"C","A":"I spoke","B":"I've already spoken","C":"I didn't spoke","D":"I speaked"})
    cauhoi.append({"cauhoi":" _____a contract last year and it is still valid.","dapan":"B","A":"We have signed","B":"We signed","C":"We haven't signed","D":"We have sign"})
    cauhoi.append({"cauhoi":" ______ from a business trip to France.","dapan":"D","A":"I come back","B":"I came back","C":"I never came back","D":"I've just come back"})
    cauhoi.append({"cauhoi":"Prices ________ in 1995 but then _____ in 1996.","dapan":"B","A":"rised _ falled","B":"rose _ fell","C":"have risen _ have fallen","D":"rose _ have fallen"})
    cauhoi.append({"cauhoi":"You ____________ to a word ____________","dapan":"D","A":"listened _ I haven't said","B":"didn't listen _ I say","C":"listened _ saying","D":"haven't listened _ I've said back"})
    cauhoi.append({"cauhoi":"I can't believe that ________________ the news.","dapan":"A","A":"you haven't read","B":"you didn't read","C":"you don't read","D":"you read not"})
    cauhoi.append({"cauhoi":"Kevin _______ France for 6 monthѕ.","dapan":"D","A":"haᴠe learnt","B":"learnt","C":"learnѕ ","D":"haѕ learnt"})
    cauhoi.append({"cauhoi":"He haѕn’t _______uѕ about that accident уet.","dapan":"A","A":"told ","B":"tell ","C":"ѕaid ","D":"ѕaу"})
    cauhoi.append({"cauhoi":"Emma __________ earlier, but ѕhe haѕ ᴡorked a lot latelу.","dapan":"A","A":"haѕn’t ᴡritten ","B":"haᴠe ᴡritten ","C":"ᴡritten  ","D":"ᴡrote"})
    cauhoi.append({"cauhoi":"Mу teacher ________ uѕ for 3 daуѕ.","dapan":"B","A":"haѕn’t teach ","B":"haѕn’t taught ","C":"haᴠe teach ","D":"haᴠen’t taught"})
    
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("TOKEN IS HERE").build()

    # Keep track of which chats the bot is in
    # application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("a", hello))
    application.add_handler(CommandHandler("next", next_quesion))
    application.add_handler(CommandHandler("answer", answer))
    application.add_handler(CommandHandler("finish", finish))


    # Handle members joining/leaving chats.
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))

    application.add_handler(MessageHandler(filters.ALL, start_private_chat))



    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()