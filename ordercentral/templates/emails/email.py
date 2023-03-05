from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect, url_for, send_file
)
from flask_login import login_required
from flask_mail import Message
from ordercentral.utilities import *
from ordercentral.models import *
from ordercentral import db

def send_mail(subject, status, recipients):
    if status == 'Confirmed':
        #PUT BODY OF EMAIL FOR CONFIRMATION HERE

    msg = Message(
        subject=subject,
        body=body,
        sender= ('Dudefish Printing', 'customer_service@dudefishprinting.com'),
        recipients= recipients
    )