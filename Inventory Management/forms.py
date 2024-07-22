from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField, IntegerField, PasswordField
from wtforms.validators import DataRequired,ValidationError, Email, EqualTo, ValidationError
from models import Product, Location, User

class AddProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    qty = IntegerField('qty', validators=[DataRequired()])
    submit = SubmitField('Add Product')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired()])
    name = StringField('Location Name', validators=[DataRequired()])
    submit = SubmitField('Add Location')



class MoveProductForm(FlaskForm):
    product_id = SelectField('Product', validators=[DataRequired()], coerce=str)
    from_location = SelectField('From Location', coerce=str, choices=[('', 'None')])
    to_location = SelectField('To Location', coerce=str, choices=[('', 'None')])
    qty = IntegerField('Quantity', validators=[DataRequired()])

    submit = SubmitField('Move Product')

    def validate_product_id(self, field):
        product = Product.query.get(field.data)
        if not product:
            raise ValidationError('Selected product does not exist.')

    def validate_from_location(self, field):
        if field.data:
            location = Location.query.get(field.data)
            if not location:
                raise ValidationError('Selected from location does not exist.')

    def validate_to_location(self, field):
        if field.data:
            location = Location.query.get(field.data)
            if not location:
                raise ValidationError('Selected to location does not exist.')

    def validate_qty(self, field):
        if field.data <= 0:
            raise ValidationError('Quantity must be a positive integer.')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')