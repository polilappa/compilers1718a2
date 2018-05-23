import plex



class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass



class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """

	def _init_(self):
		self.st = {}
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		letter = plex.Range("AZaz")
		digit = plex.Range("09")
		identifier = letter+ plex.Rep(letter|digit)
		telestes = plex.Str('=')
		parenthesi = plex.Any('()')

		keyword = plex.Str('print')
		AndOrOp = plex.Str('and','or')
		NotOp = plex.Str('not')
		
		BoolTrue = plex.NoCase(plex.Str('true','t','1'))
		BoolFalse = plex.NoCase(plex.Str('false','f','0'))

		space = plex.Any(" \t\n")

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(keyword,plex.TEXT),
			(space,plex.IGNORE),
			(NotOp,plex.TEXT),
			(AndOrOp,plex.TEXT),
			(BoolTrue,'TRUE'),
			(BoolFalse,'FALSE'),
			(parenthesi,plex.TEXT),
			(identifier,'IDENTIFIER'),
			(telestes,plex.TEXT)
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		


	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.Stmt_list()




	def Stmt_list(self):
		if self.la == 'IDENTIFIER' or self.la == 'print':
			self.Stmt()
			self.Stmt_list()
		elif self.la is	None:
			return
		else:
			raise ParseError('waiting for identifier or print')
			


	def Stmt(self):
		if self.la == 'IDENTIFIER':
				self.match('IDENTIFIER')
				self.match('=')
				self.Expr()
		elif self.la == 'print':		
				self.match('print')
				self.Expr()
		else:
				raise ParseError('waiting for identifier or print')
	def Expr(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la =='FALSE':
				self.Term()
				self.Term_tail()
		else:
				raise ParseError('waiting for ( or IDENTIFIER or true-false')

	def Term_tail(self):
		if self.la == 'and' or self.la == 'or':
				self.AndOrOp()
				self.Term()
				self.Term_tail()
		elif self.la =='IDENTIFIER' or self.la =='print' or self.la ==')' or self.la is None:
				return 
		else:
				raise ParseError('waiting for and-or')

	def Term(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la == 'FALSE':
				self.Factor()
				self.Factor_tail()
		else:
				raise ParseError('waiting for ( or IDENTIFIER or true-false')

	def Factor_tail(self):
		if self.la == 'not':
				self.NotOp()
				self.Factor()
				self.Factor_tail()
		elif self.la =='and' or self.la=='or' or self.la =='print' or self.la =='IDENTIFIER' or self.la == ')' or self.la is None:
				return
		else:
				raise ParseError('waiting not')

	def Factor(self):
		if self.la =='(':
				self.match('(')
				self.expr()
				self.match(')')
		elif self.la =='IDENTIFIER':
				self.match('IDENTIFIER')
		elif self.la == 'TRUE':
				self.match('TRUE')
		elif self.la == 'FALSE':
				self.match('FALSE')
		else:
				raise ParseError('error waiting for identifier, true-false')	
	def AndOrOp(self):
		if self.la == 'and':
				self.match('and')
		elif self.la == 'or':
				self.match('or')
		else:
				raise ParseError('waiting and-or')
	def multop(self):
		if self.la == 'not':
				self.match('not')
		else:
				raise ParseError('waiting not')


# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open('test1.txt') as fp:
	try:
		parser.parse(fp)
	except ParseError as perr:
		print(perr)
