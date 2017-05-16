import telebot
import sqlite3 as sqlite
import re
import config as cfg
from peewee import *
import bot_strings as bs
from telebot import types
from datetime import datetime, date, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

botname = '@design_order_bot'
token = '374519038:AAFhDPFU0NMPC46_e08QOqyOz97YhK06rbQ'
db_name = 'design_order_bot'
bot = telebot.TeleBot(cfg.token)
months = {1:'Январь', 2:'Февраль', 3:'Март', 4:'Апрель', 5:'Май', 6:'Июнь', 7:'Июль', 8:'Август', 9:'Сентябрь', 10:'Октябрь', 11:'Ноябрь', 12:'Декабрь'}
weekdays = {1:'Понедельник', 2:'Вторник', 3:'Среда', 4:'Четверг', 5:'Пятница', 6:'Суббота', 7:'Воскресенье'}

db = SqliteDatabase('bot.db')

duplicate = [268653382, 5844335]
dispatch = ['Bistriy_Design@mail.ru']


class User(Model):
	user_id = IntegerField(unique = True, primary_key = True)
	username = CharField(null=True)
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

@bot.message_handler(commands = ['reboot'])
def reboot(message):
	#user = User.select().where(User.user_id == message.chat.id).get()
	try:
		user = User.get(User.user_id == message.chat.id)
		user.delete_instance()
	except:
		print("Error")

@bot.message_handler(commands = ['start'])
def start(message):
	try:
		user = User.get(User.user_id == message.chat.id)
	except:
		user = User.create(user_id = message.chat.id, username = message.chat.username, step = 1)
	route(message.chat.id, message, 1)


def greeting(message):
	username = message.from_user.username
	sender_id = message.chat.id
	user = User.select().where(User.user_id == sender_id).get()
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	back_button = types.KeyboardButton(bs.back)
	markup.add(back_button)
	bot.send_message(message.chat.id, bs.greeting.format(username), reply_markup=markup)
	user.step += 1
	user.save()

def deadline(sender_id, message):
	user = User.select().where(User.user_id == sender_id).get()
	user.task = message.text
	user.step += 1
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
	user.deadline = final_date
	user.step += 1
	user.save()
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	budget_min_button = types.KeyboardButton(bs.budget_min)
	budget_avg_button = types.KeyboardButton(bs.budget_avg)
	budget_big_button = types.KeyboardButton(bs.budget_big)
	budget_max_button = types.KeyboardButton(bs.budget_max)
	back_button = types.KeyboardButton(bs.back)
	markup.add(budget_min_button, budget_avg_button, budget_big_button, budget_max_button, back_button)
	bot.send_message(sender_id, bs.budget, reply_markup=markup)

def email(sender_id, message):
	user = User.select().where(User.user_id == sender_id).get()
	if message.text == '1':
		message.text = bs.budget_min
	if message.text == '2':
		message.text = bs.budget_avg
	if message.text == '3':
		message.text = bs.budget_big
	if message.text == '4':
		message.text = bs.budget_max
	user.budget = message.text
	user.step += 1
	user.save()
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	back_button = types.KeyboardButton(bs.back)
	markup.add(back_button)
	bot.send_message(sender_id, bs.email, reply_markup=markup)

def mobile(sender_id, message):
	user = User.select().where(User.user_id == sender_id).get()
	message.text = message.text.strip()
	if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", message.text):
		user.email = message.text
		user.step += 1
		user.save()
	else:
		bot.send_message(sender_id, bs.email_error)
		return False
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	back_button = types.KeyboardButton(bs.back)
	markup.add(back_button)
	bot.send_message(sender_id, bs.mobile, reply_markup=markup)

def rules(sender_id, message):
	user = User.select().where(User.user_id == sender_id).get()
	if re.match(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', message.text):
		user.mobile = message.text
		user.step += 1
		user.save()
	else:
		bot.send_message(sender_id, bs.mobile_error)
		return False
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	agreement_button = types.KeyboardButton(bs.agreement)
	back_button = types.KeyboardButton(bs.back)
	markup.add(agreement_button)
	markup.add(back_button)
	bot.send_message(sender_id, bs.rules, reply_markup=markup, parse_mode="Markdown")

def final(sender_id, message):
	user = User.select().where(User.user_id == sender_id).get()
	if message.text != bs.agreement:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		back_button = types.KeyboardButton(bs.back)
		markup.add(back_button)
		bot.send_message(sender_id, bs.rules)
	else:
		order = '''
		Имя: {0}
		{1}
		Дедлайн: {2}
		Бюджет: {3}
		E-mail: {4}
		тел: {5}
		'''.format(user.username, user.task, user.deadline, user.budget, user.email, user.mobile)

		dispatch.append(user.email)
		for i in dispatch:
			send_email(i, order)
		for i in duplicate:
			bot.send_message(i, order)	
		bot.send_message(sender_id, bs.thanks)
		user.delete_instance()	

		'''markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		new_order_button = types.KeyboardButton(bs.new_order)
		markup.add(new_order_button)
		bot.send_message(sender_id, bs.new_order, reply_markup=markup, parse_mode="Markdown")'''


def send_email(address, text):
	fromaddr = "bistriy.design@mail.ru"
	toaddr = address
	mypass = "qazwsx123"
	 
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = bs.design_order
	 
	body = text
	msg.attach(MIMEText(body, 'plain'))
	 
	server = smtplib.SMTP('smtp.mail.ru', 587)
	server.starttls()
	server.login(fromaddr, mypass)
	text = msg.as_string()
	try:
		server.sendmail(fromaddr, toaddr, text)
	except:
		print("Mail send error")
	server.quit()


@bot.message_handler(content_types=['text'])
def reply(message):
	sender_id = message.chat.id
	user = User.select().where(User.user_id == sender_id).get()
	step = user.step
	print("Step "+str(step))
	if message.text == bs.back:
		if step > 1:
			step -= 2
		user.step = step
		user.save()
		route(sender_id, message, step)
		return True
	if message.text == bs.new_order:
		reboot(message)
		return True
	route(sender_id, message, step)

def route(sender_id, message, step):
	if step == 0 or step == 1 :
		greeting(message)
	if step == 2:
		deadline(sender_id, message)
	if step == 3:
		budget(sender_id, message)
	if step == 4:
		email(sender_id, message)
	if step == 5:
		mobile(sender_id, message)
	if step == 6:
		rules(sender_id, message)
	if step == 7:
		final(sender_id, message)


	


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
