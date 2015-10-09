
import re
import random
from halmodule import HalModule

class Quote(HalModule):

	quotes = []

	def init(self):
		self.path = self.config['quotes-path']
		print('using quotes path:', self.path)

		with open(self.path, 'r') as f:
			self.quotes = [x.rstrip() for x in f.readlines()]

	def quote(self, msg, pattern):
		if len(pattern) > 0:
			expr = re.compile(pattern)
			ls = [q for q in self.quotes if re.match(expr, q)]
		else:
			ls = self.quotes

		if len(ls) > 0:
			self.reply(msg, random.choice(ls))
		else:
			self.reply(msg, 'No quotes found with that pattern :(')

	def quoteadd(self, msg, quote):
		self.quotes.append(quote)

		with open(self.path, 'a') as f:
			print(quote, file=f)

		self.reply(msg, 'Added! :)')

	def receive(self, msg):
		ls = msg['body'].split(' ')
		cmd = ls[0]
		arg = ' '.join(ls[1:]).strip()

		if cmd == '!quote':
			self.quote(msg, arg)
		if cmd == '!quoteadd':
			self.quoteadd(msg, arg)

