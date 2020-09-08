import smtplib
from util import Config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


conf = Config()

async def event_signup(event, email):
    subject = "New Event!"
    message = f"You have just created an event called '{event['name']}'!"
    send_email(email, subject, message)

async def event_invitation(event, invites):
    subject = f"Invitation to '{event['name']}''"
    for invite_map in invites:
        message = f"Hello {invite_map['name']}, you have been invited to"
        message += f" '{event['name']}' at '{event['location']}'!"
        send_email(invite_map['email'], subject, message)

def send_email(to_email, subject, message):
    smtp_server = conf.get('email_settings', 'smtp_server')
    smtp_port = conf.get('email_settings', 'smtp_port')
    s = smtplib.SMTP(smtp_server, smtp_port)
    s.ehlo()
    s.starttls()
    email = conf.get('email_settings', 'email_address')
    password = conf.get('email_settings', 'email_password')

    s.login(email, password)


    msg = MIMEMultipart() # create a message

    # setup the parameters of the message
    msg['From']=email
    msg['To']=to_email
    msg['Subject']="subject"
    
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    
    # send the message via the server set up earlier.
    s.send_message(msg)
    s.quit()


if __name__ == "__main__":
    send_email('mrjoew65@gmail.com', 'Hi', 'hi')