from wtforms import StringField, Form, validators


class MyForm(Form):
    first_name = StringField('First Name', validators=[validators.input_required()])
    last_name  = StringField('Last Name', validators=[validators.optional()])
