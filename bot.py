import telebot
import sqlite3 as sqlite
import re
import config as cfg
from peewee import *
import bot_strings as bs
from telebot import types
from datetime import datetime, date, time

botname = '@design_order_bot'
token = '374519038:AAFhDPFU0NMPC46_e08QOqyOz97YhK06rbQ'
db_name = 'design_order_bot'
bot = telebot.TeleBot(cfg.token)
months = {1:'Январь', 2:'Февраль', 3:'Март', 4:'Апрель', 5:'Май', 6:'Июнь', 7:'Июль', 8:'Август', 9:'Сентябрь', 10:'Октябрь', 11:'Ноябрь', 12:'Декабрь'}
weekdays = {1:'Понедельник', 2:'Вторник', 3:'Среда', 4:'Четверг', 5:'Пятница', 6:'Суббота', 7:'Воскресенье'}

db = SqliteDatabase('bot.db')


class User(Model):
	user_id = IntegerField(unique = True, primary_key = True)
	username = CharField()
	step = IntegerField()
	task = TextField(null=True)
	deadline = CharField(null=True)
	budget = CharField(default=0)
	email = CharField(null=True)
	mobile = CharField(null=True)

	class Meta:
		database = db

@bot.message_handler(commands = ['init'])
def init(message):
	db.connect()
	db.create_table(User)
	user = User.create(user_id = message.chat.id, username = message.chat.username, step = 1)


current_stage = 0

@bot.message_handler(commands = ['start'])
def greeting(message):
	username = message.from_user.username
	sender_id = message.chat.id
	user = User.select().where(User.user_id == sender_id).get()
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	bot.send_message(sender_id, bs.budget, reply_markup=markup)
	bot.send_message(message.chat.id, bs.greeting.format(username))
	user.step = 2
	user.save()

def deadline(sender_id, message):
	user = User.select().where(User.user_id == sender_id).get()
	user.task = message.text
	user.step = 3
	user.save()
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	back_button = types.KeyboardButton(bs.back)
	markup.add(back_button)
	bot.send_message(sender_id, bs.deadline, reply_markup=markup)

def budget(sender_id, message):
	user = User.select().where(User.user_id == sender_id).get()
	if not re.match(r'\d{1,2}\s+\d{1,2}', message.text):
		bot.send_message(sender_id, bs.deadline_error)
		return True
	date = message.text
	day = int((re.search(r'^\d+', date)).group(0))
	month = int((re.search(r'\d+$', date)).group(0))
	if int(day) > 31 or int(day) < 1:
		bot.send_message(sender_id, bs.day_error)
		return False
	if int(month) > 12 or int(month) < 1:
		bot.send_message(sender_id, bs.month_error)
		return False
	dt = datetime.now()
	final_date = str(day)+' {0} ({1})'.format(months[month], weekdays[dt.isoweekday()])
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	budget_min_button = types.KeyboardButton(bs.budget_min)
	budget_avg_button = types.KeyboardButton(bs.budget_avg)
	budget_big_button = types.KeyboardButton(bs.budget_big)
	budget_max_button = types.KeyboardButton(bs.budget_max)
	back_button = types.KeyboardButton(bs.back)
	markup.add(budget_min_button, budget_avg_button, budget_big_button, budget_max_button, back_button)
	bot.send_message(sender_id, bs.budget, reply_markup=markup)

def email(sender_id, message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	back_button = types.KeyboardButton(bs.back)
	markup.add(back_button)
	bot.send_message(sender_id, bs.email, reply_markup=markup)

def mobile(sender_id, message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	back_button = types.KeyboardButton(bs.back)
	markup.add(back_button)
	bot.send_message(sender_id, bs.mobile, reply_markup=markup)

def rules(sender_id, message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	agreement_button = types.KeyboardButton(bs.agreement)
	back_button = types.KeyboardButton(bs.back)
	markup.add(back_button)
	bot.send_message(sender_id, bs.rules, reply_markup=markup)

@bot.message_handler(content_types=['text'])
def reply(message):
	sender_id = message.chat.id
	user = User.select().where(User.user_id == sender_id).get()
	step = user.step
	if message.text == bs.back:
		if step != 0:
			step = step-1
		user.step = step
		user.save()
		route(sender_id, message, step)
		return True
	route(sender_id, message, step)

def route(sender_id, message, step):
	if step == 1 :
		greeting(message)
	if step == 2:
		deadline(sender_id, message)
	if step == 3:
		budget(sender_id, message)
	if step == 4:
		email(sender_id, message)
	if step == 5:
		mobile(sender_id, message)
	


"""
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
	
	curr.execute(query)
	conn.commit()
	conn.close()"""


if __name__ == '__main__':
	bot.polling(none_stop=True)
