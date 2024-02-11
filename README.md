# mastodon-to-bluesky

A simple script to post posts from Mastodon instances to Bluesky.

## Setup

Requires Python 3.10 or later. We assume you have a Mastodon account and a Bluesky account.

1. On your Mastodon instance, create a list. Then, add yourself to the list - on the web interface, you can do this by clicking on "edit list" on your list, then typing your handle into the search box. Save the list's ID, which can be found at the end of the URL when you view the list on the web interface.
    - You can use any list with any amount of people - the script should post all posts from the list to Bluesky. That being said, the script was designed with a single user in mind, so it may not work as expected with multiple users.
2. Still on Mastodon, go into your account settings, then "Development", and create a new application with any name (you can keep the permissions and redirect URI as is). Save the access token.
    - You can narrow down the permissions to read only if you want to be more secure.
3. On Bluesky, go to your account settings, go to "App Passwords", and create a new app password. Save the app password.
    - You can also use your main password for Bluesky, but it's not recommended.
4. Clone this repository and install the requirements with `pip install -r requirements.txt`.
    - It's recommended to use a virtual environment. Popular choices include `venv` or `virtualenv`.
5. Make a file called ".env" in the same directory as the script. Add the following lines to it:
```
BLUESKY_USERNAME="YOUR_BLUESKY_USERNAME"  # replace with your bluesky username/handle
BLUESKY_PASSWORD="YOUR_BLUESKY_APP_PASSWORD"  # replace with your bluesky app password
MASTODON_INSTANCE="YOUR_MASTODON_INSTANCE"  # replace with your mastodon instance - ie mastodon.social
MASTODON_ACCESS_TOKEN="YOUR_MASTODON_ACCESS_TOKEN" # replace with your mastodon access token
MASTODON_LIST_ID="YOUR_MASTODON_LIST_ID"  # replace with your mastodon list id
```
6. Run the script with `python main.py`. New posts from your Mastodon list should now be posted to Bluesky.
    - You can run the script in the background with `nohup python main.py &` or use a process manager like `pm2` or `systemd`.