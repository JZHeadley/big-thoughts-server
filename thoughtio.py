
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

def parse_signature(from_number, to_number, body):
    personal_info = body.split(' ')

    if len(personal_info) != 3:
        return True
    
    if personal_info[0][0] not in ["V", "v"]:
        return True

    # Send into to the database
    
    return False

def send_to_student(student_number, class_number, msg):
    message = client.messages \
            create(
                    body=msg,
                    from_=class_number,
                    to=student_number
            )