import numpy as np
import csv
import matplotlib.pyplot as plt
import re

## Just some simple analytics to run on data. Helps to see if matrices from Baum-Welch support elements of our data
## These analytics are my no means comprehensive and are open for addition and modification

def test():
	#y = [0, 1, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0, 1, 2, 2, 3, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 1, 2, 2, 3, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 1, 2, 2, 3, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 1, 2, 2, 3, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 1, 2, 3]
	Ours = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0]
	Theirs = [2, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 3, 3, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 0, 0, 0, 0, 0, 1, 1, 2, 2, 3, 0]
	x = [i for i in range(len(Ours))]
	plt.plot(x,Ours)
	plt.plot(x,Theirs)
	plt.axis([0, x[-1], -5, 8])
	plt.show()

def check_waveform(filepath):
	x, y = [], []
	curx = 0
	cury = 0
	with open("data/" + filepath, 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			try:
				if int(row[2]) == 0:
					cury += 1
				elif int(row[2]) == 1:
					cury -= 1
				elif int(row[2]) == 2:
					cury += 1
				elif int(row[2]) == 3:
					cury -= 1
				curx += 1

				x.append(curx)
				y.append(cury)

			except ValueError:
				pass

	plt.plot(x, y, 'ro')
	plt.plot(x, y)
	plt.show()

def check_raw_waveform(filepath):
	x, y = [], []
	curx = 0
	cury = 0
	with open("data/" + filepath, 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			try:
				cury = float(row[1])
				curx += 1

				x.append(curx)
				y.append(cury)

			except ValueError:
				pass

	plt.plot(x, y)
	plt.axis([0, x[-1], 0, 100])
	plt.show()

def compare_waveform(filepath):
	pattern = re.compile("^[a-z,_,.]*on[a-z,_,.,0-9]*$")

	with open("data/" + filepath, 'r') as file:
		obs_files = file.readlines()
		for obs_filepath in obs_files:
			with open("data/" + obs_filepath.rstrip(), 'r') as obs_file:
				x, y = [], []
				curx = 0
				cury = 0

				reader = csv.reader(obs_file)
				for row in reader:
					try:
						y.append(float(row[1]))
						x.append(curx)
						curx += 1
					except ValueError:
						pass

				if pattern.match(obs_filepath.rstrip()):
					plt.plot(x, y, 'b')
				else:
					plt.plot(x, y, 'r')

	plt.axis([0, 350, 0, 100])
	plt.show()

def start_obs(filepath):
	num0, num1, num2, num3 = 0, 0, 0, 0

	with open("data/" + filepath, 'r') as file:
		obs_files = file.readlines()
		for obs_filepath in obs_files:
			print("Collecting data from ", obs_filepath.rstrip())
			with open("data/" + obs_filepath.rstrip(), 'r') as obs_file:
				reader = csv.reader(obs_file)
				for row in reader:
					try:
						if int(row[2]) == 0:
							num0 += 1
						elif int(row[2]) == 1:
							num1 += 1
						elif int(row[2]) == 2:
							num2 += 1
						elif int(row[2]) == 3:
							num3 += 1

						break

					except ValueError:
						pass

	total = num0 + num1 + num2 + num3

	print("Sequences that start with:")
	print("0: " + str(num0) + ", " + str(num0 / total) + "%")
	print("1: " + str(num1) + ", " + str(num1 / total) + "%")
	print("2: " + str(num2) + ", " + str(num2 / total) + "%")
	print("3: " + str(num3) + ", " + str(num3 / total) + "%")

def three_to_zero(filepath):
	num320, total = 0, 0

	last_was_3 = False
	with open("data/" + filepath, 'r') as file:
		obs_files = file.readlines()
		for obs_filepath in obs_files:
			print("Collecting data from ", obs_filepath.rstrip())
			with open("data/" + obs_filepath.rstrip(), 'r') as obs_file:
				reader = csv.reader(obs_file)
				for row in reader:
					try:
						if last_was_3:
							total += 1
							if int(row[2]) == 0:
								num320 += 1
								last_was_3 = False
							elif int(row[2]) != 3:
								last_was_3 = False
						elif int(row[2]) == 3:
							last_was_3 = True

					except ValueError:
						pass

	print("Transitions from 3: " + str(total))
	print("to 0: " + str(num320) + ", " + str(num320 / total) + "%")








