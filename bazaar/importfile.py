import re
from datetime import datetime
import pandas as pd

from bazaar.utilities import *
from bazaar import db
from bazaar.models import *


def fix_import(df):
    def image_add_pre(index, row, df):
        new_img = f"https://festivalnet.com{row['image-src']}"
        df.at[index, 'image-src'] = new_img

    def attendance(index, row, df):
        att = row['attendance'].splitlines()
        if att[0].isdigit():
            new_att = re.sub('[^0-9]', '', att[0])
        else:
            new_att = ''

        df.at[index, 'attendance'] = new_att

    def exibitors(index, row, df):
        exb = row['exibitors'].splitlines()
        if exb[0].isdigit():
            new_exb = int(re.sub('[^0-9]', '', exb[0]))
        else:
            new_exb = ''

        df.at[index, 'exibitors'] = new_exb

    def update_col(index, row, df):
        df.at[index, 'updated'] = row['updated'].replace('Updated ', '')

    def rename_columns(df):
        df.rename(columns={"get_more_details-href": "website"}, inplace=True)

    def drop_unused_columns(df):
        df.drop('showrating', axis=1, inplace=True)
        df.drop('web-scraper-order', axis=1, inplace=True)
        df.drop('web-scraper-start-url', axis=1, inplace=True)
        df.drop('get_more_details', axis=1, inplace=True)
        df.drop('pages', axis=1, inplace=True)

    rename_columns(df)
    drop_unused_columns(df)

    for index, row in df.iterrows():
        attendance(index, row, df)
        exibitors(index, row, df)
        update_col(index, row, df)
        image_add_pre(index, row, df)
    return df


def import_file(df):
    def write_venue(import_row):

        addy = parse_addy(import_row['fulladdress'])

        address = addy['address']
        city = addy['city']
        state = addy['state']
        zip = addy['zip']

        # check for duplicates in database
        addresses_from_db = db.session.query(Venue).filter(Venue.address == address).filter(Venue.city == city).filter(
            Venue.state == state).filter(Venue.zipcode == zip).all()

        if len(addresses_from_db) == 0:
            # if not in db, add it
            newvenue = Venue(
                name=import_row['address'],
                address=address,
                city=city,
                state=state,
                zipcode=zip,
            )
            db.session.add(newvenue)
            db.session.commit()
            db.session.refresh(newvenue)
            return newvenue.id
        else:
            # if in db, check to see if there are any changes
            if datetime.datetime.combine(addresses_from_db[0].venue_event[0].updated,
                                         datetime.datetime.min.time()) >= datetime.datetime.strptime(row['updated'],
                                                                                                     "%m/%d/%Y"):
                return addresses_from_db[0].id
            else:
                if addresses_from_db[0].name != import_row['address']:
                    addresses_from_db[0].name = import_row['address']
                if addresses_from_db[0].address != address:
                    addresses_from_db[0].address = address
                if addresses_from_db[0].city != city:
                    addresses_from_db[0].city = city
                if addresses_from_db[0].state != state:
                    addresses_from_db[0].state = state
                if addresses_from_db[0].zipcode != zip:
                    addresses_from_db[0].zipcode = zip

    def write_promoter(import_row):

        # check for duplicates in database
        promoter_in_db = db.session.query(Promoter).filter(Promoter.name == import_row['promotor']).all()

        if len(promoter_in_db) == 0:
            # if not in db, add it
            new_promoter = Promoter(
                name=import_row['promotor']
            )
            db.session.add(new_promoter)
            db.session.commit()
            db.session.refresh(new_promoter)
            return new_promoter.id
        # else:
        #     # if in db, check to see if there are any changes
        #     if promoter_in_db.name != import_row['promotor']:
        #         promoter_in_db.name = import_row['promotor']

    def write_event(row, venueid, promoterid):
        # write the data to the database
        rec = MasterList(
            event_name=row['name'],
            updated=datetime.datetime.strptime(row['updated'], "%m/%d/%Y"),
            imagesrc=row['image-src'],
            attendance=row['attendance'],
            exibitors=row['exibitors'],
            website=row['website'],
            venuefk=venueid,
            promoterfk=promoterid,
            dates_text=row['dates']
        )
        db.session.add(rec)
        db.session.commit()
        db.session.refresh(rec)
        return rec.id

    for index, row in df.iterrows():
        venueid = write_venue(row)
        promoterid = write_promoter(row)

        event_in_db = db.session.query(MasterList).filter(MasterList.event_name == row['name']).all()
        if len(event_in_db) == 0:
            eventid = write_event(row, venueid, promoterid)
            print(eventid)
        else:
            if datetime.datetime.combine(event_in_db[0].updated,
                                         datetime.datetime.min.time()) != datetime.datetime.strptime(row['updated'],
                                                                                                     "%m/%d/%Y"):
                # check each element to see what has changed
                # TODO: check each element to see what has changed... if something changes write the changes to the database
                if event_in_db[0].event_name != row['name']:
                    event_in_db[0].event_name = row['name']
                if event_in_db[0].updated != row['updated']:
                    event_in_db[0].updated = datetime.datetime.strptime(row['updated'], "%m/%d/%Y")
                if event_in_db[0].imagesrc != row['image-src']:
                    event_in_db[0].imagesrc = row['image-src']
                if event_in_db[0].attendance != row['attendance']:
                    event_in_db[0].attendance = row['attendance']
                if event_in_db[0].exibitors != row['exibitors']:
                    event_in_db[0].exibitors = row['exibitors']
                if event_in_db[0].website != row['website']:
                    event_in_db[0].website = row['website']

                event_in_db[0].venuefk = venueid
                event_in_db[0].promoterfk = promoterid

                db.session.commit()
    convertDateTextToBooleanFields()


def main():
    file = 'festivalnet_dot_com.csv'
    df = pd.read_csv(file, encoding='utf8')

    fix_import(df)
    import_file(df)

    df.to_csv('test.csv', encoding='utf-8', index=False)
