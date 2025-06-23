import praw
import json
import os
import re
import hashlib
import time
import getpass  # For secure password input

print("Hi, This is our reddit crawler.")

# Request API credentials securely
print("\n=== Reddit API Credentials ===")
client_id = input("Enter your Reddit client ID: ")
client_secret = input("Enter your Reddit client secret: ")
username = input("Enter your Reddit username: ")
password = getpass.getpass("Enter your Reddit password (input will be hidden): ")
user_agent = input("Enter your user agent (e.g., 'reddit_crawler by u/username'): ")

# Initialize Reddit API connection
try:
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        password=password,
        user_agent=user_agent,
        username=username
    )
    print("Successfully authenticated with Reddit API!")
except Exception as e:
    print(f"Error authenticating with Reddit API: {e}")
    exit(1)

name_of_file = input("Enter a filename to save the resulting data in: ")
if not name_of_file.endswith(".json"):
    name_of_file += ".json"

Subreddit_count = int(input("How many subreddits do u want your data from: "))
subreddits = []
for i in range(Subreddit_count):
    temp = input(f"Enter name of sub #{i+1}: ")
    subreddits.append(temp)

num_of_posts_wanted = int(input("Around how many posts do you want from each subreddit? "))

# Rest of your code remains the same
# ...   
