import os
from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)

userlist =  sc.api_call(
  "users.list")
print "asdf"