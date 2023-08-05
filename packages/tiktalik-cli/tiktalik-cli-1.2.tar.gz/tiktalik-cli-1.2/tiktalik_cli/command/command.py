# Copyright (c) 2013 Techstorage sp. z o.o.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in 
# the Software without restriction, including without limitation the rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
# the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from tiktalik.computing import ComputingConnection
from tiktalik.loadbalancer import HTTPBalancerConnection
from .. import auth

class CommandError(Exception):
	pass

class CommandAborted(Exception):
	pass

class Command(object):
	def __init__(self, args, keyid, secret, connection_cls):
		self.args = args
		self.conn = connection_cls(keyid, secret)

	@classmethod
	def add_parser(cls, parser, subparser):
		return None

	def execute(self):
		raise NotImplementedError()

	def yesno(self, message, abort=True):
		print message

		answer = None
		while answer not in ("yes", "no"):
			answer = raw_input("Please answer 'yes' or 'no' > ")

		if answer == "yes":
			return True

		if abort:
			raise CommandAborted()
		else:
			return False

class ComputingCommand(Command):
	def __init__(self, args, keyid, secret):
		super(ComputingCommand, self).__init__(args, keyid, secret, ComputingConnection)


class HTTPBalancerCommand(Command):
	def __init__(self, args, keyid, secret):
		super(HTTPBalancerCommand, self).__init__(args, keyid, secret, HTTPBalancerConnection)
