from flask import Flask
from flask_mail import Mail, Message
import os

"""
Methods and configuration for send email
"""
app = Flask(__name__)
app.config.from_pyfile(os.path.join("..", "config/app.config"), silent=False)
"""
EMAIL CONFIG
"""
app.config["MAIL_SERVER"] = app.config.get("MAIL_SERVER")
app.config["MAIL_PORT"] = app.config.get("MAIL_PORT")
app.config["MAIL_USERNAME"] = app.config.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = app.config.get("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = app.config.get("MAIL_USE_TLS")
app.config["MAIL_USE_SSL"] = app.config.get("MAIL_USE_SSL")
mail = Mail(app)

"""
Compose positive COVID-19 contact notification email template and sends to customer
"""


def send_possibile_positive_contact(toEmail, toName, datePossibleContact, restaurantName):
    subject = "Possible COVID-19 contact"
    body = (
        "Hi {toName},<br>"
        'you had a possible COVID-19 contact at restaurant "{restaurantName}" in date {datePossibleContact}.<br> '
        "<br>Please contact authority at 911.<br> "
    )
    body = body.replace("{toName}", toName)
    body = body.replace("{restaurantName}", restaurantName)
    body = body.replace("{datePossibleContact}", datePossibleContact)
    sendmail(subject, body, toEmail)


"""
Compose reservation confirm email template and sends to customer
"""


def send_reservation_confirm(
    toEmail, toName, dateReservation, restaurantName, numberSeat
):
    subject = "Reservation confirmed"
    body = (
        "Hi {toName},<br>"
        "we are glad to confirm your table for {numberSeat} people "
        'at restaurant "{restaurantName}" in date {dateReservation}<br> '
        "<br>See you soon!<br> "
    )
    body = body.replace("{toName}", toName)
    body = body.replace("{restaurantName}", restaurantName)
    body = body.replace("{dateReservation}", dateReservation)
    body = body.replace("{numberSeat}", str(numberSeat))
    sendmail(subject, body, toEmail)


"""
Compose reservation notification email template and sends to operator
"""


def send_reservation_notification(
    toEmail,
    toName,
    restaurantName,
    customerName,
    dateReservation,
    tableNumber,
    numberSeat,
):
    subject = "Reservation notification"
    body = (
        "Hi {toName} from {restaurantName},<br>"
        "you have a new reservation:<br>"
        "<ul>"
        "<li>customer name: {customerName}</li>"
        "<li>number of seats: {numberSeat}</li>"
        "<li>date: {dateReservation}</li>"
        "<li>table number: {tableNumber}</li>"
        "</ul>"
        "See you soon! "
    )
    body = body.replace("{toName}", toName)
    body = body.replace("{restaurantName}", restaurantName)
    body = body.replace("{customerName}", customerName)
    body = body.replace("{numberSeat}", str(numberSeat))
    body = body.replace("{dateReservation}", dateReservation)
    body = body.replace("{tableNumber}", str(tableNumber))
    sendmailTest(subject, body, toEmail)


"""
Compose registration confirm email template and sends to user
"""


def send_registration_confirm(toEmail, toName, token):
    subject = "Confirm email"
    body = (
        "Hi {toName},<br>"
        "we are glad to have you in GoOutSafe but you must confirm your email"
        'by click on <a href="http://localhost:5000/confirme_mail?token={token}">this URL<a>.<br>'
        "<br>See you soon! "
    )
    body = body.replace("{toName}", toName)
    body = body.replace("{token}", token)
    sendmail(subject, body, toEmail)


"""
Internal method for send email
"""


def sendmail(subject, body, recipient):
    subject = "[GoOutSafe] " + subject
    msg = Message(
        recipients=[recipient],
        sender="greyteam2020@gmail.com",
        html=body,
        subject=subject,
    )
    mail.send(msg)
    return 0