
import os
import twilio

sid = os.getenv("TWILIO_SID")
token = os.getenv("TWILIO_TOKEN")
client = Client(account_sid, auth_token)

# List of tuples 
# Tuples are arranged like so
# (ToNumber, FromNumber)
waiting_list = []

def init_mesg(to, class_number):
    message = client.messages \
                create(
                     body="Welcome to BigThoughts! Please send your V# and Full Name",
                     from_=class_number,
                     to=to
                 )
