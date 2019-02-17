
import os
from twilio.rest import Client

sid = os.getenv("TWILIO_SID")
token = os.getenv("TWILIO_TOKEN")
client = Client(sid, token)

# List of tuples 
# Tuples are arranged like so
# (FromNumber, ToNumber)
waiting_list = []

def init_msg(to_number, class_number):
    message = client.messages \
                .create(
                     body="Welcome to BigThoughts! Please send your V# and Full Name so we can get you in the system first :)",
                     from_=class_number,
                     to=to_number
                )

def parse_signature(from_number, to_number, body):
    personal_info = body.split(' ')

    # It's gotta be three things
    if len(personal_info) != 3:
        return True
    
    # It's gotta start with a V
    if personal_info[0][0] not in ["V", "v"]:
        return True

    #############################
    # Send into to the database 
    #############################
    register_student(from_number, to_number, *personal_info)

    return False

def parsing_failure(student_number, class_number, body):
    message = client.messages \
                .create(
                     body="We were unable to understand your message: " + body,
                     from_=class_number,
                     to=student_number
                )

def send_to_student(student_number, class_number, msg):
    message = client.messages \
            .create(
                    body=msg,
                    from_=class_number,
                    to=student_number
            )