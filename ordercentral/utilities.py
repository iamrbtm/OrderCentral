import re
from ordercentral import mail, db
from ordercentral.models import *
import phonenumbers
from flask import render_template
from flask_mail import Message


def format_phone(number):
    phonematchstring = r"(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
    if re.match(phonematchstring, number) is not None:
        return phonenumbers.format_number(phonenumbers.parse(number, "US"),
                                          phonenumbers.PhoneNumberFormat.NATIONAL)
    else:
        return None


def send_mail(ordernum):
    record = db.session.query(Orders).filter(Orders.id == ordernum).first()

    if record.status[0].shipped:
        pass
    elif record.status[0].ready2ship:
        pass
    elif record.status[0].post:
        pass
    elif record.status[0].print:
        pass
    elif record.status[0].prep:
        pass
    elif record.status[0].confirmed:
        subject = f"Your order ({record.ordernum}) has been confirmed"
        body = render_template("emails/confirmation.html", record=record)

    msg = Message()
    msg.sender = ('Dudefish Printing', 'customer_service@dudefishprinting.com')
    msg.recipients = [record.person.email]
    msg.subject = subject
    msg.html = body
    mail.send(msg)
