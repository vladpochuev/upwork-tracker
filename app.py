import os
from os.path import join, dirname

import telebot
from dotenv import load_dotenv
from flask import Flask, request
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
    user_name = db.Column(db.String())
    language_code = db.Column(db.String())
    registered_at = db.Column(db.DateTime, nullable=False)


class Topic(db.Model):
    __tablename__ = "topics"

    topic_name = db.Column(db.String(), primary_key=True)
    value = db.Column(db.String())


user_topics = db.Table("users_topics",
                       db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
                       db.Column("topic_name", db.String(), db.ForeignKey("topics.topic_name"), primary_key=True))


@app.route("/webhook", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return {"ok": True}


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id, "Start command")
    return {"ok": True}


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
