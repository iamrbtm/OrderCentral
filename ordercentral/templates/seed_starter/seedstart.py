from flask_login import login_required
from ordercentral.utilities import *
from ordercentral.models import *
from ordercentral import db
from flask import render_template, Blueprint, request, redirect, url_for
from sqlalchemy import text
import json

seed = Blueprint("seedstart", __name__, url_prefix='/seedstart')


@seed.route("/new/<id>", methods=['GET', 'POST'])
@login_required
def seedstart_order_new(id):
    order = db.session.query(Orders).filter(Orders.id == id).first()
    if request.method == "POST":
        data = request.form.to_dict()
        product = db.session.query(Product).filter(Product.name == data['product']).first()

        new_order_item = OrderLineItem(
            data=json.dumps(data),
            saleprice=product.saleprice,
            orderfk=id,
            productfk=product.id,
        )
        db.session.add(new_order_item)
        db.session.commit()
        return redirect(url_for('order.order_new', id=order.id))

    products = db.session.query(Product).filter(text("name LIKE 'seed%'")).order_by(Product.name).all()
    content = {"order": order, "products": products}
    return render_template("seed_starter/seedstart.html", **content)
