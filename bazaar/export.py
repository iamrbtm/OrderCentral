import os

import vobject
from flask import url_for
from vobject import vcard
import csv


def create_vcard(people):
    allcontacts = vobject.vCard()

    for person in people:
        cardobj = vobject.vCard()

        if person.name:
            try:
                fname, lname = person.name.split(" ")
            except ValueError:
                cardobj.add('fn').value = person.name
            else:
                cardobj.add('n').value = vobject.vcard.Name(family=lname, given=fname)
                cardobj.add('fn').value = person.name
        elif person.promoter.name:
            cardobj.add('fn').value = person.promoter.name
        else:
            cardobj.add('fn').value = person.title

        if person.promoter.address:
            cardobj.add('adr').value = vobject.vcard.Address(street=person.promoter.address, city=person.promoter.city,
                                                             region=person.promoter.state, code=person.promoter.zipcode,
                                                             country='USA')
            cardobj.adr.type_param = 'Work'

        if person.promoter.name:
            cardobj.add('org').value = [person.promoter.name]

        if person.title:
            cardobj.add('title').value = person.title

        if person.phone:
            cardobj.add('tel').value = person.phone
            cardobj.tel.type_param = 'Work'

        if person.email:
            cardobj.add('email').value = person.email
            cardobj.email.type_param = 'Work'

        if person.promoter.website:
            cardobj.add('url').value = person.promoter.website

        allcontacts.add(cardobj)

    filename = os.path.join(os.path.dirname(__file__), "static", "exports", "contacts.vcf")

    with open(filename, 'w') as file:
        file.write(allcontacts.serialize())
    return filename


def create_csv(people):
    filename = os.path.join(os.path.dirname(__file__), "static", "exports", "contacts.csv")
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Address', 'City', 'State', 'Zip', 'Phone', 'Website', 'Organization', 'Title'])

        for person in people:
            row = [person.name, person.promoter.address, person.promoter.city, person.promoter.state,
                   person.promoter.zipcode, person.phone, person.promoter.website, person.promoter.name,
                   person.title]
            writer.writerow(row)
    return filename
