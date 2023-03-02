from datetime import datetime
import random

from flask import (
    Blueprint,
    render_template,
    request,
    redirect, url_for, send_file
)
from flask_login import login_required
from ordercentral.utilities import *
from ordercentral.models import *
from ordercentral import db

order = Blueprint("order", __name__, url_prefix='/order')


def calculate_total(id):
    record = db.session.query(Orders).filter(Orders.id == id).first()
    order_total = db.session.query(func.sum(OrderLineItem.saleprice)).filter(OrderLineItem.orderfk == id).scalar()
    if order_total is None:
        record.total = 0
    else:
        record.total = order_total
    db.session.commit()


@order.route("/init")
@login_required
def order_init():
    ordernum = 0
    newrecid = 0
    exists = True
    while exists:
        ordernum = int(str(datetime.now().year) + "" + (str(random.randint(1, 9999))))
        exists = bool(db.session.query(Orders.id).filter(Orders.ordernum == ordernum).first())

    newrec = Orders(
        ordernum=ordernum
    )
    db.session.add(newrec)
    db.session.commit()
    db.session.refresh(newrec)
    newrecid = newrec.id
    return redirect(url_for('order.order_new', id=newrecid))


@order.route("/new/<id>", methods=['GET', 'POST'])
@login_required
def order_new(id):
    calculate_total(id)
    states = [r.state for r in db.session.query(USZip.state).order_by(USZip.state).distinct()]
    record = db.session.query(Orders).filter(Orders.id == id).first()
    items = db.session.query(OrderLineItem).filter(OrderLineItem.orderfk == id).all()
    if request.method == "POST":
        data = request.form.to_dict()

        # Persons
        # Check to see if the email address exists in the db
        exists = bool(db.session.query(People).filter(People.email == data['email']).first())
        if not exists:
            # if not in db, add the person to the db
            newperson = People(
                fname=data['fname'],
                lname=data['lname'],
                mailing_address=data['mailing_address'],
                mailing_city=data['mailing_city'],
                mailing_state=data['mailing_state'],
                mailing_zipcode=data['mailing_zipcode'],
                phone=format_phone(data['phone']),
                email=data['email']
            )
            db.session.add(newperson)
            db.session.commit()
            db.session.refresh(newperson)
            personid = newperson.id
        else:
            # if the record does exist in the db, edit the values form the form
            record = db.session.query(People).filter(People.email == data['email']).first()
            record.fname = data['fname']
            record.lname = data['lname']
            record.mailing_address = data['mailing_address']
            record.mailing_city = data['mailing_city']
            record.mailing_state = data['mailing_state']
            record.mailing_zipcode = data['mailing_zipcode']
            record.phone = format_phone(data['phone'])
            record.email = data['email']
            db.session.commit()

            personid = record.id

        # Order update personfk
        order_record = db.session.query(Orders).filter(Orders.id == id).first()
        order_record.personfk = personid
        db.session.commit()

        return redirect(url_for('order.order_new', id=id))

    content = {"user": User, "states": states, "record": record,
               "items": items, }
    return render_template("orders/orders_new.html", **content)
