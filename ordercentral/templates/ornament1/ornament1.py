from flask_login import login_required
from ordercentral.utilities import *
from ordercentral.models import *
from ordercentral import db
from flask import render_template, Blueprint, request, redirect, url_for
import json

orn1 = Blueprint("ornament1", __name__, url_prefix='/ornament1')


@orn1.route("/new/<id>", methods=['GET', 'POST'])
@login_required
def ornament1_order_new(id):
    order = db.session.query(Orders).filter(Orders.id == id).first()
    if request.method == "POST":
        data = request.form.to_dict()
        product = db.session.query(Product).filter(Product.id == 1).first()
        new_order_item = OrderLineItem(
            data=json.dumps(data),
            saleprice=product.cost,
            orderfk=id,
            productfk=1,
        )
        db.session.add(new_order_item)
        db.session.commit()
        return redirect(url_for('order.order_new', id=order.id))
    content = {"order": order}
    return render_template("ornament1/ornament1.html", **content)
