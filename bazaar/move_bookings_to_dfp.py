import pymysql
from bazaar import db
from bazaar.models import *


def transfer_data():
    # Connect to the MySQL database
    connection = pymysql.connect(host='192.96.200.111', user='onlymyli_rbtm2006', password='Braces4me##',
                                 db='onlymyli_print')
    cursor = connection.cursor()

    # Extract data from SQLite database
    bookings = db.session.query(Booking).filter(Booking.active == True).filter(Booking.cl_appapproved == True).all()

    # Loop through the bookings and insert into the events table in MySQL
    for booking in bookings:
        start_date = booking.info_datestart
        end_date = booking.info_dateend
        start_time = booking.info_timestart
        end_time = booking.info_timeend
        location = booking.event.venue.name
        title = booking.event.event_name
        publish = True
        dos_contact_person = 1

    sql = "SELECT COUNT(*) FROM events WHERE title = %s AND location = %s"
    cursor.execute(sql, (title, location))
    result = cursor.fetchone()
    if result[0] > 0:
        event_exists = True

    # Update the event if it exists, otherwise insert it
    if event_exists:
        sql = "UPDATE events SET start_date = %s, end_date = %s, start_time = %s, end_time = %s, location = %s, title = %s , publish = %s, dos_contact_person = %s WHERE title = %s AND location = %s AND start_date = %s AND end_date = %s AND start_time = %s AND end_time = %s"
        cursor.execute(sql, (
            start_date, end_date, start_time, end_time, location, title, publish, dos_contact_person, title, location,
            start_date, end_date,
            start_time, end_time))
    else:
        sql = "INSERT INTO events (start_date, end_date, start_time, end_time, location, title, publish, dos_contact_person) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (start_date, end_date, start_time, end_time, location, title, publish, dos_contact_person))

    # Commit the changes and close the cursor and connection
    connection.commit()
    cursor.close()
    connection.close()
