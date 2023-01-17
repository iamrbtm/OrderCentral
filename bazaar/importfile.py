import re
from datetime import datetime
import usaddress
import pandas as pd
import requests
import urllib.parse

from bazaar.utilities import *
from bazaar import db
from bazaar.models import *


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
            if addresses_from_db.updated >= import_row['updated']:
                return addresses_from_db.id
            else:
                if addresses_from_db.name != import_row['address']:
                    addresses_from_db.name = import_row['address']
                if addresses_from_db.address != address:
                    addresses_from_db.address = address
                if addresses_from_db.city != city:
                    addresses_from_db.city = city
                if addresses_from_db.state != state:
                    addresses_from_db.state = state
                if addresses_from_db.zipcode != zip:
                    addresses_from_db.zipcode = zip

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
        else:
            # if in db, check to see if there are any changes
            if promoter_in_db.name != import_row['promotor']:
                promoter_in_db.name = import_row['promotor']

    for index, row in df.iterrows():
        venueid = write_venue()
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
    # noinspection SpellCheckingInspection
    apikey = 'AIzaSyD1qqEWZryfyghgr1IvjnsTEcyKw3-NqXg'
    promoter_name = row['promotor']

    def get_venue_lat_long(row):
        address = parse_addy(row)
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address['full']) + '?format=json'

        response = requests.get(url).json()

        with open('resp.json', 'w') as file:
            file.write(response.text)
            print(response.text)

        return response[0]["lat"], response[0]["lon"]

    def get_address(name):
        address = get_venue_lat_long(row)

        # TODO: Place request for near by places using the lat and long of the venue

    get_address(promoter_name)
    promoter_from_db = db.session.query(Promoter).filter(Promoter.name == promoter_name).first()

    if len(promoter_from_db) != 0:
        return promoter_from_db.id
    else:
        newpromotor = Promoter(
            name=row['promotor']
        )
        db.session.add(newpromotor)
        db.session.commit()
        db.session.refresh(newpromotor)
        return newpromotor.id


def parse_addy(full_address):
    addy = usaddress.tag(full_address)

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


def main():
    file = '/Users/rbtm2006/Dudefish Printing/Bazaars/Program/festivalnet_dot_com.csv'
    df = load_file(file)

    drop_unused_columns(df)
    rename_columns(df)
    fix_import(df)
    import_file(df)

    df.to_csv('test.csv', encoding='utf-8', index=False)
