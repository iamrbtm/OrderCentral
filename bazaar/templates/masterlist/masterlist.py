from flask import (
    Blueprint,
    render_template, request, redirect, url_for
)
from flask_login import login_required

import bazaar
from bazaar.utilities import *

ml = Blueprint("masterlist", __name__, url_prefix="/masterlist")


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
                            date = bazaar.utilities.nth_day_of_month(month, day, week)
                            date_list.append(date)
    notes = db.session.query(Notes).filter(Notes.masterlistid == id).all()

    types = []
    for type in get_types_masterlist():
        if getattr(record, "type_" + type):
            types.append(type.title())

    persons = db.session.query(People).filter(People.promoterfk == id).all()

    contents = {"user": User, "record": record, "full_text": full_text,
                "date_list": date_list, "notes": notes, "types": types,
                "persons": persons}
    return render_template("masterlist/details.html", **contents)


@ml.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def masterlist_edit(id):
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
        record.promoter.phone = bazaar.utilities.format_phone(form_data['p_phone'])
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
    return render_template("masterlist/masterlist_edit.html", **contents)


@ml.route("/newevent", methods=["GET", "POST"])
@login_required
def masterlist_add():
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    weeks = ['First', 'Second', 'Third', 'Fourth', 'Last']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    types = get_types_masterlist()

    if request.method == "POST":
        data = request.form.to_dict()
        form_months = request.form.getlist('months')
        form_weeks = request.form.getlist('weeks')
        form_days = request.form.getlist('days')
        form_types = request.form.getlist("type")

        # Venue
        newVenue = Venue(
            name=data['v_name'],
            address=data['v_address'],
            city=data['v_city'],
            state=data['v_state'],
            zipcode=data['v_zipcode'],
            phone=bazaar.utilities.format_phone(data['v_phone']),
            website=data['v_website'],
        )
        db.session.add(newVenue)
        db.session.commit()
        db.session.refresh(newVenue)
        # Promoter
        newPromoter = Promoter(
            name=data['p_name'],
            address=data['p_address'],
            city=data['p_city'],
            state=data['p_state'],
            zipcode=data['p_zipcode'],
            phone=bazaar.utilities.format_phone(data['p_phone']),
            website=data['p_website'],
        )
        db.session.add(newPromoter)
        db.session.commit()
        db.session.refresh(newPromoter)

        # Event
        newEvent = MasterList(
            event_name=data['event_name'],
            website=data['event_website'],
            venuefk=newVenue.id,
            promoterfk=newPromoter.id,
            updated=datetime.date.today()
        )
        db.session.add(newEvent)
        db.session.commit()
        db.session.refresh(newEvent)

        # get event record
        record = db.session.query(MasterList).filter(MasterList.id == newEvent.id).first()

        # months
        for month in [x.lower() for x in months]:
            if month in [x.lower() for x in form_months]:
                setattr(record, month, True)
            else:
                setattr(record, month, False)
            db.session.commit()

        # days
        for day in [x.lower() for x in days]:
            if day in [x.lower() for x in form_days]:
                setattr(record, day, True)
            else:
                setattr(record, day, False)
            db.session.commit()

        # weeks
        for week in [x.lower() for x in weeks]:
            if week in [x.lower() for x in form_weeks]:
                setattr(record, week, True)
            else:
                setattr(record, week, False)
            db.session.commit()

        # types
        for type in [x.lower() for x in types]:
            if type in [x.lower() for x in form_types]:
                setattr(record, "type_" + type, True)
            else:
                setattr(record, "type_" + type, False)
            db.session.commit()

        return redirect(url_for('masterlist.masterlist_home', type="all"))

    contents = {"user": User, "months": months, "weeks": weeks, "days": days, "types": types}
    return render_template("masterlist/masterlist_add.html", **contents)


@ml.route("/ticktypes")
@login_required
def tick_types():
    tick_all_types()
    return redirect(url_for('masterlist.masterlist_home', type="all"))


@ml.route("/addperson/<id>", methods=['GET', 'POST'])
@login_required
def person_add(id):
    if request.method == "POST":
        data = request.form.to_dict()
        addperson = People(
            name=data['name'],
            title=data['title'],
            phone=bazaar.utilities.format_phone(data['phone']),
            fax=bazaar.utilities.format_phone(data['fax']),
            email=data['email'],
            promoterfk=id
        )
        db.session.add(addperson)
        db.session.commit()
    return redirect(url_for('masterlist.details', id=id))


@ml.route("/editperson/<personid>/<recordid>", methods=['GET', 'POST'])
@login_required
def person_edit(personid, recordid):
    person = db.session.query(People).filter(People.id == personid).first()
    if request.method == "POST":
        data = request.form.to_dict()
        person.name = data['name']
        person.phone = format_phone(data['phone'])
        person.fax = format_phone(data['fax'])
        person.title = data['title']
        person.email = data['email']
        db.session.commit()
        return redirect(request.referrer)
    return redirect(url_for('masterlist.details', id=recordid))


@ml.route("/deleteperson/<personid>/<recordid>", methods=['GET', 'POST'])
@login_required
def person_delete(personid, recordid):
    People.query.filter(People.id == personid).delete()
    db.session.commit()
    return redirect(url_for('masterlist.details', id=recordid))


@ml.route("/noteadd/<recordid>", methods=['GET', 'POST'])
@login_required
def note_add(recordid):
    if request.method == "POST":
        newnote = Notes(
            masterlistid=recordid,
            note=request.form['note']
        )
        db.session.add(newnote)
        db.session.commit()
    return redirect(url_for('masterlist.details', id=id))


@ml.route("/list/<type>")
@login_required
def masterlist_home(type):
    types = get_types_masterlist()

    match type:
        case "bazaar":
            records = db.session.query(MasterList).filter(MasterList.type_bazaar == True).all()
        case "art":
            records = db.session.query(MasterList).filter(MasterList.type_art == True).all()
        case "holiday":
            records = db.session.query(MasterList).filter(MasterList.type_holiday == True).all()
        case "festival":
            records = db.session.query(MasterList).filter(MasterList.type_festival == True).all()
        case "flea":
            records = db.session.query(MasterList).filter(MasterList.type_flea == True).all()
        case "health":
            records = db.session.query(MasterList).filter(MasterList.type_health == True).all()
        case "market":
            records = db.session.query(MasterList).filter(MasterList.type_market == True).all()
        case _:
            records = db.session.query(MasterList).all()

    activities = [rec.eventid for rec in db.session.query(Booking).filter(Booking.active == True).all()]
    contents = {"user": User, "records": records, "types": types, "actives": activities}
    return render_template("masterlist/masterlist.html", **contents)
