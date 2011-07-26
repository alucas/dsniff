import sys

def printRed(string):
	sys.stdout.write("\033[31m{}\033[0m".format(string))

def printBlue(string):
	sys.stdout.write("\033[34m{}\033[0m".format(string))

def printGreen(string):
	sys.stdout.write("\033[32m{}\033[0m".format(string))
