
import re, random, sys, traceback, os
from halibot import HalModule

class Quote(HalModule):

	# Configuration defaults
	remove_votes = 3
	can_remove = True
	max_history = 5

	def init(self):
		self.quotes = []
		self.path = self.config.get('quotes-path')
		self.remove_votes = self.config.get('remote-votes', self.remove_votes)
		self.can_remove = self.config.get('can-remove', self.can_remove)
		self.max_history = self.config.get('max-history', self.max_history)
		print('using quotes path:', self.path, file=sys.stderr)

		if self.path is not None:
			try:
				with open(self.path, 'r') as f:
					self.quotes.extend([x.rstrip() for x in f if x.rstrip()])
			except (IOError, OSError):
				print("Couldn't open quotes file:", file=sys.stderr)
				traceback.print_exc()

		self.rand_quotes = {}  # pattern -> shuffled lists
		self.rem_vote_map = {}  # quote -> set(usernames)

	def quote(self, pattern=""):
		if pattern not in self.rand_quotes:
			if len(pattern) > 0:
				try:
					expr = re.compile(pattern)
				except re.error as e:
					return 'Invalid pattern: {}'.format(e)

				ls = [q for q in self.quotes if expr.search(q)]
			else:
				ls = self.quotes[:]

			if not ls:
				return 'No quotes found with that pattern :('

			random.shuffle(ls)

			if len(self.rand_quotes) >= self.max_history:
				for i in range(len(self.rand_quotes) - self.max_history + 1):
					del self.rand_quotes[random.choice(list(self.rand_quotes.keys()))]  # XXX LRU?

			self.rand_quotes[pattern] = ls

		ls = self.rand_quotes[pattern]
		quote = ls.pop()
		if not ls:
			del self.rand_quotes[pattern]

		return quote

	def quoteadd(self, quote):
		self.quotes.append(quote)

		if self.path is not None:
			try:
				with open(self.path, 'a') as f:
					print(quote, file=f)
			except (IOError, OSError) as e:
				return "Couldn't add quote! I'll remember it for now, though :) ({})".format(e)

		return 'Added :)'

	def quotedel(self, pattern, nick):
		if not self.can_remove:
			return "I'm sorry, Dave. I'm afraid I can't do that..."

		if not pattern:
			return 'Please tell me which quote to remove :)'

		try:
			expr = re.compile(pattern)
		except re.error as e:
			return 'Invalid pattern: {}'.format(e)

		ls = [q for q in self.quotes if expr.search(q)]
		if not ls:
			return 'No quotes found with that pattern :('
		if len(ls) > 1:
			return 'That refers to more than one quote--be more specific?'

		quote = ls[0]

		vote_set = self.rem_vote_map.setdefault(quote, set())
		vote_set.add(nick)  # TODO prevent vote fraud better

		if len(vote_set) < self.remove_votes:
			return 'Need {} more votes to approve! :)'.format(
				self.remove_votes - len(vote_set),
			)
		else:
			self.quotes.remove(quote)
			if self.path is not None:
				try:
					with open(self.path, 'w') as f:
						f.writelines([q + os.linesep for q in self.quotes])
				except (IOError, OSError) as e:
					return "Couldn't remove quote! I'll forget it for now, though :) ({})".format(e)
			return 'Removed :)'

	def receive(self, msg):
		ls = msg.body.split(' ')
		cmd = ls[0]
		arg = ' '.join(ls[1:]).strip()

		if cmd == '!quote':
			self.reply(msg, body=self.quote(pattern=arg))
		elif cmd == '!quoteadd':
			self.reply(msg, body=self.quoteadd(arg))
		elif cmd == '!quotedel':
			self.reply(msg, body=self.quotedel(arg, msg.author))
