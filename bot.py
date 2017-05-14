import telebot
import sqlite3 as sqlite
import re
import pickle
import config as cfg
from peewee import *
import bot_strings as bs

botname = '@design_order_bot'
token = '374519038:AAFhDPFU0NMPC46_e08QOqyOz97YhK06rbQ'
db_name = 'design_order_bot'
bot = telebot.TeleBot(cfg.token)

db = SqliteDatabase('bot.db')

class User(Model):
	user_id = IntegerField(unique = True, primary_key = True)
	username = CharField()
	step = IntegerField()
	task = TextField()
	deadline = CharField()
	budget = CharField()
	email = CharField()
	mobile = CharField()

	class Meta:
		database = db

current_stage = 0

@bot.message_handler(commands = ['start'])
def greeting(message):
	username = message.from_user.username
	user = User.create(username = message.chat.id, step = 1)
	bot.send_message(message.chat.id, bs.greeting.format(username))


@bot.message_handler(content_types=['text'])
def reply(message):
	bot.send_message(message.chat.id, message)

def init_db():
	conn = sqlite.connect(config.db_name)
	curr = conn.cursor()
	query = '''
	CREATE TABLE IF NOT EXISTS users(
		`id` INTEGER PRIMARY KEY NOT NULL,
		`username` VARCHAR(32),
		`stage` INTEGER,
		`task` TEXT,
		`dealine` TEXT,
		`budget` TEXT,
		`email` TEXT,
		`mobile` TEXT
	)'''
	curr.execute(query)
	conn.commit()
	conn.close()

def update_user(id, stage, task, deadline, budget, email, mobile):
	conn = sqlite.connect(config.db_name)
	curr = conn.cursor()
	query = '''
	ШТЫУК
	)'''
	curr.execute(query)
	conn.commit()
	conn.close()


if __name__ == '__main__':
	bot.polling(none_stop=True)
