import calendar
import datetime
import re
from calendar import day_name, month_name
from dateutil.rrule import MONTHLY, MO, TU, WE, TH, FR, SA, SU, rrule

import phonenumbers
import usaddress

from bazaar.models import *


def last_specified_day_of_month(month, year, day_of_week):
    day_ = (datetime.datetime(year, month, 1).replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    while True:
        day_ -= datetime.timedelta(days=1)
        if day_.weekday() == day_of_week:
            break
    return day_


def nth_day_of_month(month, day_of_week, week_num='last', year=datetime.datetime.now().year, ):
    my_year = int(year)

    months = dict(zip(month_name, range(13)))
    month = month.title()
    my_month = months[month]

    weeks = dict(zip(['First', 'Second', 'Third', 'Fourth', 'Last', 'Every'], range(1, 6, 1)))
    week = week_num.title()
    if week == 6:
        my_week = 1
    else:
        my_week = weeks[week]

    days = dict(zip(day_name, range(7)))
    day = day_of_week.title()
    my_day = days[day]

    if week_num == "last":
        date = last_specified_day_of_month(my_month, my_year, my_week)
        return date
    else:
        first_possible_day = {1: 1, 2: 8, 3: 15, 4: 22, 5: 29}[my_week]
        d = datetime.date(my_year, my_month, first_possible_day)
        w = d.weekday()
        if w != my_day:
            d = d.replace(day=(first_possible_day + (my_day - w) % 7))
        return d


def convertDateTextToBooleanFields():
    for record in db.session.query(MasterList).all():

        if record.dates_text is not None:
            dates_text = record.dates_text.title()
            event_name = record.event_name.title()

            for day in calendar.day_name:
                if day in dates_text:
                    setattr(record, day.lower(), True)
                    db.session.commit()
                    print(getattr(record, day.lower()))
                elif day in event_name:
                    setattr(record, day.lower(), True)
                    db.session.commit()
                    print(getattr(record, day.lower()))

            for month in calendar.month_name:
                if month in dates_text:
                    setattr(record, month.lower(), True)
                    db.session.commit()
                elif month in event_name:
                    setattr(record, month.lower(), True)
                    db.session.commit()


def parse_addy(full_address):
    addy = usaddress.tag(full_address)
    print(addy)
    if 'Ambiguous' not in addy:
        addressfields = []
        parsed_address = []
        for item in addy[0]:
            if item == "PlaceName":
                pass
            elif item == 'StateName':
                pass
            elif item == 'ZipCode':
                pass
            else:
                addressfields.append(item)

        for field in addressfields:
            parsed_address.append(addy[0][field])

        address_dic = {'address': ' '.join(parsed_address),
                       'city': addy[0]['PlaceName'],
                       'state': addy[0]['StateName'],
                       'zip': addy[0]['ZipCode'],
                       'full': f"{' '.join(parsed_address)} {addy[0]['PlaceName']}, {addy[0]['StateName']} {addy[0]['ZipCode']}"}

        return address_dic
    else:
        address_dic = {'address': None,
                       'city': None,
                       'state': None,
                       'zip': None,
                       'full': None
                       }

        return address_dic


def get_types():
    from sqlalchemy import inspect
    inst = inspect(MasterList)
    attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
    typelist = []
    for name in attr_names:
        if "type" in name:
            typelist.append(name.replace("type_", ""))
    return typelist


def format_phone(number):
    phonematchstring = r"(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
    if re.match(phonematchstring, number) is not None:
        return phonenumbers.format_number(phonenumbers.parse(number, "US"),
                                          phonenumbers.PhoneNumberFormat.NATIONAL)
    else:
        return None


def tick_all_types():
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


def next_touch_update(recordid):
    nexttouchdays = 0
    weekday = datetime.datetime.now().weekday()

    record = Booking.query.filter(Booking.eventid == recordid).first()

    match record.days_remaining:
        case num if num > 181:
            nexttouchdays = 15
        case num if num in range(91, 180):
            nexttouchdays = 10
        case num if num in range(15, 90):
            nexttouchdays = 7
        case num if num in range(8, 14):
            nexttouchdays = 3
        case num if num in range(1, 7):
            nexttouchdays = 2
        case _:
            nexttouchdays = 0

    # Calculate the number of workdays (no weekends) for next touch
    record.next_touch = datetime.datetime.now() + datetime.timedelta(days=nexttouchdays)
    db.session.commit()


def get_types_masterlist(tbl=MasterList):
    from sqlalchemy import inspect
    inst = inspect(tbl)
    attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
    typelist = []
    for name in attr_names:
        if "type" in name:
            typelist.append(name.replace("type_", ""))
    return typelist


def tempfunc():
    for record in db.session.query(Booking).filter(Booking.active == True).all():
        record.days_remaining = calc_days_remaining(record.info_datestart)
        db.session.commit()
        next_touch_update(record.eventid)


def calc_days_remaining(event_start_date):
    days_remaining = (event_start_date - datetime.date.today()).days
    return days_remaining


def next_business_day(start_day=datetime.date.today()):
    import holidays
    HOLIDAYS = holidays.US()
    ONE_DAY = datetime.timedelta(days=1)
    temp_day = start_day
    next_day = temp_day + ONE_DAY
    while next_day.weekday() in [5, 6] or next_day in HOLIDAYS:
        next_day += ONE_DAY
    temp_day = next_day
    return temp_day


def get_nth_week(recordid, year=datetime.date.today().year):
    record = db.session.query(MasterList).filter(MasterList.id == recordid).first()

    months = dict(zip(month_name, range(13)))
    days = dict(zip(day_name, ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]))
    weeks = dict(zip(['First', 'Second', 'Third', 'Fourth', 'Last'], range(1, 5, 1)))

    monthlist = []
    for key, value in zip(months.keys(), months.values()):
        if value != 0:
            if getattr(record, key.lower()):
                monthlist.append(value)

    daylist = []
    for key, value in zip(days.keys(), days.values()):
        if value != 0:
            if getattr(record, key.lower()):
                daylist.append(value)

    weeklist = []
    for key, value in zip(weeks.keys(), weeks.values()):
        if value != 0:
            if getattr(record, key.lower()):
                weeklist.append(value)

    datelist = []
    for month in monthlist:
        for day in daylist:
            for week in weeklist:
                date = list(rrule(MONTHLY,
                                  byweekday=eval(day + '({})'.format(int(week))),
                                  dtstart=datetime.datetime(year, month, 1),
                                  until=datetime.datetime(year, month, calendar.monthrange(year, month)[1])
                                  ))[0]
                datelist.append(date)

    return {"min": min(datelist), "max": max(datelist), "all": datelist}
