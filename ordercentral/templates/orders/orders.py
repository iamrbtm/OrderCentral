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
from sqlalchemy import and_

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
    db.session.add(Status(orderfk=newrecid))
    db.session.commit()
    return redirect(url_for('order.order_new', id=newrecid))


@order.route("/change_status/<recordid>", methods=["POST"])
def change_status(recordid):
    record = db.session.query(Orders).filter(Orders.id == recordid).first()
    data = request.form.to_dict()
    match data['status']:
        case 'Confirmed':
            record.status[0].confirmed = True
            record.status[0].prep = False
            record.status[0].print = False
            record.status[0].post = False
            record.status[0].ready2ship = False
            record.status[0].shipped = False
            record.status[0].confirmed_when = datetime.now()
        case 'Pre':
            record.status[0].confirmed = True
            record.status[0].prep = True
            record.status[0].print = False
            record.status[0].post = False
            record.status[0].ready2ship = False
            record.status[0].shipped = False
            record.status[0].prep_when = datetime.now()
        case "Print":
            record.status[0].confirmed = True
            record.status[0].prep = True
            record.status[0].print = True
            record.status[0].post = False
            record.status[0].ready2ship = False
            record.status[0].shipped = False
            record.status[0].print_when = datetime.now()
        case "Post":
            record.status[0].confirmed = True
            record.status[0].prep = True
            record.status[0].print = True
            record.status[0].post = True
            record.status[0].ready2ship = False
            record.status[0].shipped = False
            record.status[0].post_when = datetime.now()
        case "ReadyShip":
            record.status[0].confirmed = True
            record.status[0].prep = True
            record.status[0].print = True
            record.status[0].post = True
            record.status[0].ready2ship = True
            record.status[0].shipped = False
            record.status[0].ready2ship_when = datetime.now()
        case "Shipped":
            record.status[0].confirmed = True
            record.status[0].prep = True
            record.status[0].print = True
            record.status[0].post = True
            record.status[0].ready2ship = True
            record.status[0].shipped = True
            record.status[0].shipped_when = datetime.now()
    db.session.commit()

    send_mail(recordid)
    return redirect(url_for('order.order_new', id=recordid))


@order.route("/new/<id>", methods=['GET', 'POST'])
@login_required
def order_new(id):
    calculate_total(id)
    states = [r.state for r in db.session.query(USZip.state).order_by(USZip.state).distinct()]
    record = db.session.query(Orders).filter(Orders.id == id).first()
    items = db.session.query(OrderLineItem).filter(OrderLineItem.orderfk == id).all()
    active_events = db.session.query(Booking).filter(
        and_(Booking.cl_appsubmission, Booking.cl_appapproved)).all()

    if request.method == "POST":
        data = request.form.to_dict()

        # Persons
        # Check to see if the email address exists in the db
        exists = bool(db.session.query(Peoples).filter(Peoples.email == data['email']).first())
        if not exists:
            # if not in db, add the person to the db
            newperson = Peoples(
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
            record = db.session.query(Peoples).filter(Peoples.email == data['email']).first()
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
               "items": items, "active_events": active_events, }
    return render_template("orders/orders_new.html", **content)


@order.route("/change_event/<recordid>", methods=["POST"])
def change_event(recordid):
    record = db.session.query(Orders).filter(Orders.id == recordid).first()
    data = request.form.to_dict()
    record.eventid = data['event']
    db.session.commit()
    return redirect(url_for('order.order_new', id=recordid))
