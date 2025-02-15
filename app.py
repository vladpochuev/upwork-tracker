import os
import textwrap
from datetime import datetime
from functools import wraps
from os.path import join, dirname

import telebot
from dotenv import load_dotenv
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import insert
from telebot import types


def get_from_env(key):
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    return os.environ.get(key)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_from_env("DB_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

bot_token = get_from_env("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(bot_token)
bot.remove_webhook()
server_url = f"{get_from_env("SERVER_URL")}/webhook"
bot.set_webhook(url=server_url)

ADD_TOPIC_STATUS = "ADD_TOPIC_STATUS"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    username = db.Column(db.String())
    language_code = db.Column(db.String())
    registered_at = db.Column(db.DateTime, nullable=False)

    status = db.relationship("Status")


class Status(db.Model):
    __tablename__ = "status"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    name = db.Column(db.String())


class Topic(db.Model):
    __tablename__ = "topics"

    topic_name = db.Column(db.String(), primary_key=True)
    value = db.Column(db.String())


user_topics = db.Table("users_topics",
                       db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
                       db.Column("topic_name", db.String(), db.ForeignKey("topics.topic_name"), primary_key=True))


def context_required(func):
    @wraps(func)
    def wrapper(message):
        if not current_app:
            with app.app_context():
                return func(message)
        return func(message)

    return wrapper


@app.route("/webhook", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return {"ok": True}


def get_status(user_id):
    with app.app_context():
        return db.session.query(Status).filter_by(id=user_id).first().name


@bot.message_handler(func=lambda message: get_status(message.from_user.id) == ADD_TOPIC_STATUS)
def add_topic_status_handler(message):
    topic = message.text.strip()

    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Yes", callback_data="ADD_TOPIC_YES_" + topic)
    btn_no = types.InlineKeyboardButton("No", callback_data="ADD_TOPIC_NO")

    markup.add(btn_yes, btn_no)
    bot.send_message(message.from_user.id, f"Do you want to add new topic \"{topic}\"?", reply_markup=markup)


def clear_status(user_id):
    status = db.session.query(Status).filter_by(id=user_id).first()
    status.name = None
    db.session.commit()


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("ADD_TOPIC_YES"))
@context_required
def add_topic_yes_callback(callback):
    user_id = callback.from_user.id
    topic_name = callback.data[len("ADD_TOPIC_YES_"):]

    if not db.session.query(Topic).filter_by(topic_name=topic_name).first():
        topic = Topic(topic_name=topic_name)
        db.session.add(topic)
        db.session.commit()

    if db.session.query(user_topics).filter_by(user_id=user_id, topic_name=topic_name).first():
        bot.edit_message_text(text=f"Topic \"{topic_name}\" is already tracked.",
                              chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id)
        clear_status(user_id)
        return

    users_topic = insert(user_topics).values(user_id=user_id, topic_name=topic_name)
    db.session.execute(users_topic)
    db.session.commit()

    clear_status(user_id)

    bot.edit_message_text(text=f"Topic \"{topic_name}\" was successfully added to the tracked ones.",
                          chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("ADD_TOPIC_NO"))
@context_required
def add_topic_no_callback(callback):
    user_id = callback.from_user.id

    status = db.session.query(Status).filter_by(id=user_id).first()
    status.name = None
    db.session.commit()

    bot.edit_message_text(text="Topic addition has been canceled",
                          chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id)


@bot.message_handler(commands=["start"])
@context_required
def start_command(message):
    user_id = message.from_user.id
    if not db.session.query(User).filter_by(id=user_id).first():
        user = User(id=user_id,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    username=message.from_user.username,
                    language_code=message.from_user.language_code,
                    registered_at=datetime.now())
        status = Status(id=user_id, name=None)

        db.session.add(user)
        db.session.add(status)
        db.session.commit()

    bot.send_message(message.chat.id, textwrap.dedent(f"""
        Hello, {message.from_user.first_name}.

        This bot is designed to help you receive notifications about new UpWork jobs.
        To start using the bot, add any topic to your list using the /addtopic command.
        To learn more about bots functionality, use the /help command.
    """), parse_mode="html")
    return {"ok": True}


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(message.chat.id, textwrap.dedent(f"""
        This bot is designed to help you receive notifications about new UpWork jobs.
        To start using the bot, add any topic to your list using the /addtopic command.
    
        <b>List of commands</b>
        /addtopic - add a new topic
        /removetopic - remove an existing topic
    """), parse_mode="html")


@bot.message_handler(commands=["addtopic"])
@context_required
def add_topic_command(message):
    status = db.session.query(Status).filter_by(id=message.from_user.id).first()
    status.name = ADD_TOPIC_STATUS
    db.session.commit()

    bot.send_message(message.chat.id, "Please enter the topic you would like to track")


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
