import os
import textwrap
from datetime import datetime
from functools import wraps
from os.path import join, dirname

import telebot
from dotenv import load_dotenv
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy


def get_from_env(key):
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    return os.environ.get(key)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_from_env("DB_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

bot_token = get_from_env("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(bot_token)
bot.remove_webhook()
server_url = f"{get_from_env("SERVER_URL")}/webhook"
bot.set_webhook(url=server_url)


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
    status = db.Column(db.String())


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
        status = Status(id=user_id,
                        status=None)

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


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
