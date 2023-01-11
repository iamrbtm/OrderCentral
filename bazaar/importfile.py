import calendar
import re
from datetime import datetime
import usaddress
import pandas as pd

from bazaar.models import *
from bazaar.utilities import *


def load_file(file):
    return pd.read_csv(file)


def rename_columns(df):
    df.rename(columns={"get_more_details-href": "website"}, inplace=True)


def fix_import(df):
    for index, row in df.iterrows():
        attendance(index, row, df)
        exibitors(index, row, df)
        update_col(index, row, df)
        image_add_pre(index, row, df)
    return df


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


def drop_unused_columns(df):
    df.drop('showrating', axis=1, inplace=True)
    df.drop('web-scraper-order', axis=1, inplace=True)
    df.drop('web-scraper-start-url', axis=1, inplace=True)
    df.drop('get_more_details', axis=1, inplace=True)
    df.drop('pages', axis=1, inplace=True)


def import_file(df):
    for index, row in df.iterrows():
        venueid = write_venue(row)
        promoterid = write_promoter(row)

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

    convertDateTextToBooleanFields()


def write_promoter(row):
    promoter_from_db = db.session.query(Promoter).filter(Promoter.name == row['promotor']).all()
    if len(promoter_from_db) != 0:
        return promoter_from_db[0].id
    else:
        newpromotor = Promoter(
            name=row['promotor']
        )
        db.session.add(newpromotor)
        db.session.commit()
        db.session.refresh(newpromotor)
        return newpromotor.id


def check_for_dup_venue(address, city, state, zip):
    addresses_from_db = db.session.query(Venue).filter(Venue.address == address).filter(Venue.city == city).filter(
        Venue.state == state).filter(Venue.zipcode == zip).all()
    if len(addresses_from_db) == 0:
        return False
    else:
        return True


def get_venue_id(address, city, state, zip):
    addresses_from_db = db.session.query(Venue).filter(Venue.address == address).filter(Venue.city == city).filter(
        Venue.state == state).filter(Venue.zipcode == zip).first()
    return addresses_from_db.id


def write_venue(row):
    addy = usaddress.tag(row['fulladdress'])

    if 'Ambiguous' not in addy:
        addressfields = []
        address = []
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
            address.append(addy[0][field])

        newaddress = ' '.join(address)
        city = addy[0]['PlaceName']
        state = addy[0]['StateName']
        zip = addy[0]['ZipCode']

        if check_for_dup_venue(newaddress, city, state, zip):
            venueid = get_venue_id(newaddress, city, state, zip)
            return venueid
        else:
            newvenue = Venue(
                name=row['address'],
                address=newaddress,
                city=city,
                state=state,
                zipcode=zip,
            )
            db.session.add(newvenue)
            db.session.commit()
            db.session.refresh(newvenue)
            return newvenue.id
    else:
        newvenue = Venue(
            name=row['address'],
            city=row['city'],
            state=row['state'],
            zipcode=row['zip'],
        )
        db.session.add(newvenue)
        db.session.commit()
        db.session.refresh(newvenue)
        return newvenue.id


def main():
    file = '/Users/rbtm2006/Dudefish Printing/Bazaars/Program/festivalnet_dot_com.csv'
    df = load_file(file)

    drop_unused_columns(df)
    rename_columns(df)
    fix_import(df)
    import_file(df)

    df.to_csv('test.csv', encoding='utf-8', index=False)
