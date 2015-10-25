
import re
import random
from halibot import HalModule

class Quote(HalModule):

	quotes = []

	def init(self):
		self.path = self.config['quotes-path']
		print('using quotes path:', self.path)

		with open(self.path, 'r') as f:
			self.quotes = [x.rstrip() for x in f.readlines()]

	def quote(self, msg, pattern):
		if len(pattern) > 0:
			try:
				expr = re.compile(pattern)
			except re.error, e:
				self.reply(msg, 'Invalid pattern: ' + e.message)
				return
				
			ls = [q for q in self.quotes if re.search(expr, q)]
		else:
			ls = self.quotes

		if len(ls) > 0:
			msg['body'] = random.choice(ls)
			self.send(msg)
		else:
			msg['body'] = 'No quotes found with that pattern :('
			self.send(msg)

	def quoteadd(self, msg, quote):
		self.quotes.append(quote)

		with open(self.path, 'a') as f:
			print(quote, file=f)

		msg['body'] = 'Added :)'
		self.send(msg)

	def receive(self, msg):
		ls = msg['body'].split(' ')
		cmd = ls[0]
		arg = ' '.join(ls[1:]).strip()

		if cmd == '!quote':
			self.quote(msg, arg)
		if cmd == '!quoteadd':
			self.quoteadd(msg, arg)

