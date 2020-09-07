import praw
import prawcore
import csv
import re
import webbrowser
from win10toast import ToastNotifier
from intervals import IntInterval

#USAGE INSTRUCTIONS:
#-------------------------------
#Conditions:
#KEYWORD | SCORE | USER | SETTING
#
#Multiple keywords can be entered as such: keyword, keyword2, keyword3.
#
#Score must be entered as an interval. Such as [x, y] or (x, y) or [x, y) and vice-versa. 
#Submissions with scores that are in the interval will be notified. 
#
#Multiple users can be entered as such: user, user2, user3.
#
#Setting must be set as the sorting type. Default is set to hot.
#Example: hot
#or top, or rising, or new, or controversial
#--------------------------------

with open ('api_info.txt', 'r') as file:
	read = csv.reader(file)

	_user_agent = next(read)[0]
	_client_id = next(read)[0]
	_client_secret = next(read)[0]

reddit = praw.Reddit(user_agent = _user_agent, client_id = _client_id, client_secret = _client_secret)

#Simply open the url of the notification.
def open_browser_tab(url):
    webbrowser.open(url, new=0)

#Checks for keywords in title
def keywordCheck(title:str, words:list)->bool:
	for word in words: #checks for word(s) in title regardless of case ("test", "TeSt") -> true
		if not re.search(word, title, re.IGNORECASE): 
			return False
	return True

#Checks if subreddits the user entered are proper
def checkSubreddits():
	with open('PopUpRead.csv', 'r', newline='') as file:
		read = csv.reader(file)
		next(read) #skip header

		for row in read:
			try:
				reddit.subreddits.search_by_name(row[0], exact=True)
			except prawcore.exceptions.NotFound:
				print("Error: subreddit \"" + row[0] + "\" does not exist!")
				break

#Builds dictionary with subreddits as keys and
#with all of the conditions as values in an array
#{subreddit: [[cond1], cond2, [cond3], cond4]}
def buildDictionary()->dict:
	popUpDict = {}

	with open('PopUpRead.csv', 'r', newline='') as file:
		read = csv.reader(file)
		next(read) #skip header

		for row in read: #skips duplicates
			if row[0] not in popUpDict:
				popUpDict[row[0]] = [[x.strip() for x in row[1].split(',') if x], IntInterval.from_string(row[2]), 
									[x.strip() for x in row[3].split(',') if x], row[4]]
				if '' == row[2]:
					popUpDict[row[0]][1] = '0'
				if '' == row[4]:
					popUpDict[row[0]][3] = 'hot'
	return popUpDict

def main():
	checkSubreddits()
	popUpDict = buildDictionary()
	notify = ToastNotifier()

	for subreddit in popUpDict:
		for submission in getattr(reddit.subreddit(subreddit), popUpDict[subreddit][3])(limit = 20):
			counter=0
			if submission.score in popUpDict[subreddit][1]:
				counter+=1
			if submission.author.name in popUpDict[subreddit][2] or not popUpDict[subreddit][2]:
				counter+=1
			if keywordCheck(submission.title, popUpDict[subreddit][0]) or not popUpDict[subreddit][0]:
				counter+=1

			#The callback_on_click method argument was taken from "Charnelx" here: 
			#https://github.com/jithurjacob/Windows-10-Toast-Notifications/pull/38
			#This makes it so that when you click the notification it activates the specified method.
			if counter == len(popUpDict[subreddit])-1:
				notify.show_toast(subreddit, submission.title+ " : " + submission.url, 
					icon_path=None, duration=3, callback_on_click = lambda: open_browser_tab(submission.url))

if __name__ == "__main__":
	main()