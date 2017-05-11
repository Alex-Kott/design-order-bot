import telebot
import sqlite3 as sqlite
import re
import pickle
import config as cfg

botname = '@design_order_bot'
token = '374519038:AAFhDPFU0NMPC46_e08QOqyOz97YhK06rbQ'
db_name = 'design_order_bot'
bot = telebot.TeleBot(cfg.token)

current_stage = 0

@bot.message_handler(commands = ['start'])
def greeting(message):
	username = message.from_user.username
	greeting = '''
		{}, Вас приветствует компания Быстрый Дизайн!
	Напишите, какой дизайн Вы хотите заказать?
	'''.format(username)
	bot.send_message(message.chat.id, greeting)


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


if __name__ == '__main__':
	bot.polling(none_stop=True)
