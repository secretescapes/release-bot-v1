import logging
import json

def format_queue(queue):
	i = 1
	text = 'Here is the current status of the queue:\n'
	for item in queue:
		if i == 1:
			text += "*%d. %s*\n" % (i, item['username'])
		else:
			text += "%d. %s\n" % (i, item['username'])
		i+= 1

	if i == 1:
		text = 'The queue is currently empty!'
	return text