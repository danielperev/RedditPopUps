import praw
import prawcore
import csv

#Conditions:
#KEYWORD | SCORE | USER | SETTING
#
#Multiple keywords can be entered as such: keyword, keyword2, keyword3.
#
#Score must be entered with as a value. Default is > than the score entered.
#
#Multiple users can be entered as such: user, user2, user3.
#
#Setting must be set as the sorting type.
#Example: Hot
#or Top, or Rising, or New, or Controversial

with open ('api_info.txt', 'r') as file:
	read = csv.reader(file)

	_user_agent = next(read)
	_client_id = next(read)
	_client_secret = next(read)

reddit = praw.Reddit(user_agent = _user_agent, client_id = _client_id, client_secret = _client_secret)

def keywordCheck(title:str, words:list)->bool:
	for word in words: #checks for word(s) in title regardless of case ("test", "TeSt") -> true
		if not re.search(word, title, re.IGNORECASE): 
			return False
	return True

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

def buildDictionary()->dict:
	popUpDict = {}

	with open('PopUpRead.csv', 'r', newline='') as file:
		read = csv.reader(file)
		next(read) #skip header

		for row in read: #SIMPLY SKIPS DUPLICATES
			if row[0] not in popUpDict:
				popUpDict[row[0]] = [[x.strip() for x in row[1].split(',')], row[2], 
									[x.strip() for x in row[3].split(',')], row[4]]
	return popUpDict

def main():

	#find way to pop up notifications for windows

	checkSubreddits()
	popUpDict = buildDictionary()
	for subreddit in popUpDict:
		print(popUpDict[subreddit])
		for submission in getattr(reddit.subreddit(subreddit), popUpDict[subreddit][3])(limit = 20):
			if popUpDict[subreddit][1] and submission.score > int(popUpDict[subreddit][1]):
				if popUpDict[subreddit][2] and submission.author.name in popUpDict[subreddit][2]:
					if keywordCheck(submission.title, popUpDict[subreddit][0]):
						print("test")

if __name__ == "__main__":
	main()

