
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

	def quote(self, pattern=""):
		if len(pattern) > 0:
			try:
				expr = re.compile(pattern)
			except re.error as e:
				return 'Invalid pattern: ' + str(e)
				
			ls = [q for q in self.quotes if re.search(expr, q)]
		else:
			ls = self.quotes

		if len(ls) > 0:
			return random.choice(ls)
		else:
			return 'No quotes found with that pattern :('

	def quoteadd(self, quote):
		self.quotes.append(quote)

		with open(self.path, 'a') as f:
			print(quote, file=f)

		return 'Added :)'

	def receive(self, msg):
		ls = msg.body.split(' ')
		cmd = ls[0]
		arg = ' '.join(ls[1:]).strip()

		if cmd == '!quote':
			self.reply(msg, body=self.quote(pattern=arg))
		if cmd == '!quoteadd':
			self.reply(msg, body=self.quoteadd(arg))

