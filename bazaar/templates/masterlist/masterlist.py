from calendar import day_name
from datetime import datetime
from bazaar.models import *
from bazaar.utilities import *
from flask import (
    Blueprint,
    render_template, request, redirect, url_for
)
from flask_login import login_required
from bazaar import db

ml = Blueprint("masterlist", __name__, url_prefix="/masterlist")


def get_types_masterlist():
    from sqlalchemy import inspect
    inst = inspect(MasterList)
    attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
    typelist = []
    for name in attr_names:
        if "type" in name:
            typelist.append(name.replace("type_", ""))
    return typelist


@ml.route("/")
@login_required
def masterlist():
    master = db.session.query(MasterList).all()
    contents = {"user": User, "allrec": master}
    return render_template("masterlist/masterlist.html", **contents)


@ml.route("/details/<id>")
@login_required
def details(id):
    record = db.session.query(MasterList).filter(MasterList.id == id).first()

    # Details for Dates
    # Months
    true_months = []
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']

    for month in [x.lower() for x in months]:
        if getattr(record, month) is True:
            true_months.append(month)

    months_text = ""
    if len(true_months) == 12:
        months_text = ['All Year']
    elif len(true_months) >= 2:
        true_months.insert(len(true_months) - 1, 'and')
        months_text = ", ".join(true_months).title()
    else:
        months_text = "".join(true_months).title()

    # Weeks
    true_weeks = []
    weeks = ['First', 'Second', 'Third', 'Fourth', 'Last']

    for week in [x.lower() for x in weeks]:
        if getattr(record, week) is True:
            true_weeks.append(week)

    weeks_text = ""
    if len(true_weeks) == 5:
        weeks_text = "Every"
    elif len(true_weeks) == 2:
        true_weeks.insert(1, 'and')
        weeks_text = " ".join(true_weeks).title()
    elif len(true_weeks) == 1:
        weeks_text = "".join(true_weeks).title()
    else:
        true_months.insert(len(true_weeks) - 1, 'and')
        weeks_text = ", ".join(true_weeks).title()

    # Days
    true_days = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in [x.lower() for x in days]:
        if getattr(record, day) is True:
            true_days.append(day)

    days_text = ""
    if len(true_days) == 5:
        days_text = "Every day"
    elif len(true_days) >= 2:
        true_days.insert(len(true_days) - 1, 'and')
        days_text = " ".join(true_days).title()
    else:
        days_text = ", ".join(true_days).title()

    # Combine all days, weeks, and months
    full_text = weeks_text + " " + days_text + " of " + months_text

    # List Dates
    # DONE:: figure out how to do this...
    date_list = []
    for month in true_months:
        if month.lower() == 'and':
            pass
        else:
            for week in true_weeks:
                if week.lower() == 'and':
                    pass
                else:
                    for day in true_days:
                        if day.lower() == 'and':
                            pass
                        else:
                            date = nth_day_of_month(month, day, week)
                            date_list.append(date)
    notes = db.session.query(Notes).filter(Notes.masterlistid == id).all()

    types = []
    for type in get_types_masterlist():
        if getattr(record, "type_" + type):
            types.append(type.title())

    contents = {"user": User, "record": record, "full_text": full_text,
                "date_list": date_list, "notes": notes, "types": types}
    return render_template("masterlist/details.html", **contents)


@ml.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_single(id):
    record = db.session.query(MasterList).filter(MasterList.id == id).first()

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    months_values = {"January": record.january, "February": record.february, "March": record.march,
                     "April": record.april, "May": record.may, "June": record.june, "July": record.july,
                     "August": record.august, "September": record.september, "October": record.october,
                     "November": record.november, "December": record.december}

    weeks = ['First', 'Second', 'Third', 'Fourth', 'Last']
    weeks_values = {"First": record.first, "Second": record.second, "Third": record.third, "Fourth": record.fourth,
                    "Last": record.last}

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days_values = {"Monday": record.monday, "Tuesday": record.tuesday, "Wednesday": record.wednesday,
                   "Thursday": record.thursday, "Friday": record.friday, "Saturday": record.saturday,
                   "Sunday": record.sunday}

    types = get_types_masterlist()
    types_values = {}
    for type in types:
        types_values[type] = getattr(record, "type_" + type)

    # DONE: make a dict with the day of the week and true or false

    if request.method == "POST":
        form_data = request.form.to_dict()
        # TODO: see if the venue or promotor is in the database.  if so, edit it, if not, add it

        # Event Information
        record.event_name = form_data['event_name']
        # Venue
        record.venue.name = form_data['name']
        record.venue.address = form_data['address']
        record.venue.city = form_data['city']
        record.venue.state = form_data['state']
        record.venue.zipcode = form_data['zipcode']
        # Promoter
        record.promoter.name = form_data['p_name']
        record.promoter.address = form_data['p_address']
        record.promoter.city = form_data['p_city']
        record.promoter.state = form_data['p_state']
        record.promoter.zipcode = form_data['p_zipcode']
        record.promoter.phone = form_data['p_phone']
        record.promoter.website = form_data['p_website']

        # Months
        for month in [x.lower() for x in months]:
            if month in request.form.getlist('months'):
                setattr(record, month, True)
            else:
                setattr(record, month, False)

        # Weeks
        for week in [x.lower() for x in weeks]:
            if week in request.form.getlist('weeks'):
                setattr(record, week, True)
            else:
                setattr(record, week, False)

        # Days
        for day in [x.lower() for x in days]:
            if day in request.form.getlist('days'):
                setattr(record, day, True)
            else:
                setattr(record, day, False)

        # Types
        for type in types:
            if type in request.form.getlist('type'):
                setattr(record, "type_" + type, True)
            else:
                setattr(record, "type_" + type, False)

        db.session.commit()

        return redirect(url_for('masterlist.details', id=id))

    notes = db.session.query(Notes).filter(Notes.masterlistid == id).all()
    contents = {"user": User, "record": record, "notes": notes,
                "months": months, "days": days, "weeks": weeks,
                "v_days": days_values, "v_months": months_values,
                "v_weeks": weeks_values, "types": types,
                "v_types": types_values}
    return render_template("masterlist/edit_single.html", **contents)


@ml.route("/ticktypes")
@login_required
def tick_types():
    typelist = get_types_masterlist()

    extralist = {'bazaar': ['show'],
                 'holiday': ['christmas', 'santa'],
                 "festival": ['fest'],
                 'market': ['show'],
                 'art': [],
                 'health': [],
                 'flea': []
                 }
    for record in db.session.query(MasterList).all():
        for type in typelist:
            if type in record.event_name.lower():
                setattr(record, "type_" + type, True)
                db.session.commit()
            for extra in extralist[type]:
                if extra in record.event_name.lower():
                    setattr(record, "type_" + type, True)
                    db.session.commit()

    return redirect(url_for('masterlist.masterlist'))


@ml.route("/addperson/<id>", methods=['GET', 'POST'])
@login_required
def addperson(id):
    if request.method == "POST":
        data = request.form.to_dict()
        addperson = People(
            name=data['name'],
            title=data['title'],
            phone=data['phone'],
            fax=data['fax'],
            email=data['email'],
            promoterfk=id
        )
        db.session.add(addperson)
        db.session.commit()
    return redirect(url_for('masterlist.details', id=id))
