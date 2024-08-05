# email_utils.py

import smtplib
def send_email(subject, content, to_email):
    HOST = "smtp-mail.outlook.com"
    PORT = 587
    FROM_EMAIL = "Kunigiriraghunath9493@gmail.com"  # Replace with your email address
    PASSWORD = "Kunimicro@1998"

    message = """Subject: Reset Password
    Hello 
    This is your password
    
    Thanks,
    SE_G5_Team"""

    with smtplib.SMTP(HOST, PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, PASSWORD)
        smtp.sendmail(FROM_EMAIL, to_email, message)

