import calendar
import datetime
from calendar import day_name, month_name
from bazaar import db
from bazaar.models import *
import usaddress


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
