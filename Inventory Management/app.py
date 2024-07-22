from flask import Flask,render_template,request,redirect,url_for,flash
from models import db, Product, Location, ProductMovement, User
from forms import AddProductForm, LocationForm, MoveProductForm, RegistrationForm, LoginForm
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:swapnilg45@localhost:3307/myinventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
app.config['SECRET_KEY'] = 'swapnilBhai'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))



@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/products')
@login_required
def products():
    product =  Product.query.all()
    return render_template('products.html',product=product)

@app.route('/location')
@login_required
def location():
    location = Location.query.all()
    return render_template('location.html', location=location)

@app.route('/add_product',methods = ['GET','POST'])
@login_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        product_id = form.product_id.data
        name = form.name.data
        qty=form.qty.data
        new_product = Product(product_id=product_id,name=name,qty=qty)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)

@app.route('/add_location', methods=['GET', 'POST'])
@login_required
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        location_id = form.location_id.data
        name = form.name.data
        new_location = Location(location_id=location_id, name=name)
        db.session.add(new_location)
        db.session.commit()
        flash('Location added successfully!', 'success')
        return redirect(url_for('add_location'))  
    return render_template('add_location.html', form=form)

@app.route('/edit_location/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_location(id):
    location = Location.query.get_or_404(id)
    form = LocationForm()
    if form.validate_on_submit():
        location.location_id = form.location_id.data
        location.name = form.name.data
        db.session.commit()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('location'))
    elif request.method == 'GET':
        form.location_id.data = location.location_id
        form.name.data = location.name
    return render_template('edit_location.html', form=form)

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = AddProductForm()
    if form.validate_on_submit():
        product.product_id = form.product_id.data
        product.name = form.name.data
        product.qty=form.qty.data
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    elif request.method == 'GET':
        form.product_id.data = product.product_id
        form.name.data = product.name
    return render_template('edit_Product.html', form=form)

@app.route('/move_product', methods=['GET', 'POST'])
@login_required
def move_product():
    form = MoveProductForm()
    form.product_id.choices = [(p.product_id, p.name) for p in Product.query.all()]
    form.from_location.choices.extend([(l.location_id, l.name) for l in Location.query.all()])
    form.to_location.choices.extend([(l.location_id, l.name) for l in Location.query.all()])
    
    if form.validate_on_submit():
        product_id = form.product_id.data
        from_location = form.from_location.data if form.from_location.data else None
        to_location = form.to_location.data if form.to_location.data else None
        qty = form.qty.data

        # Check for enough quantity in from_location if applicable
        if from_location:
            total_qty_in_from = db.session.query(
                db.func.sum(ProductMovement.qty)
            ).filter_by(product_id=product_id, to_location=from_location).scalar() or 0
            total_qty_out_from = db.session.query(
                db.func.sum(ProductMovement.qty)
            ).filter_by(product_id=product_id, from_location=from_location).scalar() or 0

            if total_qty_in_from - total_qty_out_from < qty:
                flash('Not enough quantity in the from location', 'danger')
                return redirect(url_for('move_product'))
        
        movement = ProductMovement(
            timestamp=datetime.now(),
            from_location=from_location,
            to_location=to_location,
            product_id=product_id,
            qty=qty
        )
        db.session.add(movement)
        db.session.commit()
        flash('Product moved successfully!', 'success')
        return redirect(url_for('move_product'))
    
    return render_template('move_product.html', form=form)

@app.route('/report')
@login_required
def report():
    balances = db.session.query(
        Product.name.label('product_name'),
        Location.name.label('location_name'),
        db.func.sum(ProductMovement.qty).label('quantity')
    ).join(ProductMovement, Product.product_id == ProductMovement.product_id)\
     .join(Location, Location.location_id == ProductMovement.to_location)\
     .group_by(Product.name, Location.name)\
     .all()

    return render_template('report.html', balances=balances)

@app.route('/balance_report')
@login_required
def balance_report():
    balances = db.session.query(
        Product.name.label('product_name'),
        Location.name.label('location_name'),
        (db.func.sum(
            db.case(
                (ProductMovement.to_location == Location.location_id, ProductMovement.qty), 
                else_=0
            )
        ) - db.func.sum(
            db.case(
                (ProductMovement.from_location == Location.location_id, ProductMovement.qty), 
                else_=0
            )
        )).label('quantity')
    ).join(ProductMovement, Product.product_id == ProductMovement.product_id)\
     .join(Location, db.or_(
        Location.location_id == ProductMovement.to_location, 
        Location.location_id == ProductMovement.from_location)
     )\
     .group_by(Product.name, Location.name)\
     .all()

    return render_template('balance_report.html', balances=balances)

@app.route('/movements')
@login_required
def movements():
    # Query to get the product movements
    movements = db.session.query(
        ProductMovement.movement_id,
        Product.name.label('product_name'),
        db.session.query(Location.name).filter(Location.location_id == ProductMovement.from_location).label('from_location'),
        db.session.query(Location.name).filter(Location.location_id == ProductMovement.to_location).label('to_location'),
        ProductMovement.qty,
        ProductMovement.timestamp
    ).join(Product, Product.product_id == ProductMovement.product_id)\
     .all()
    
    return render_template('movements.html', movements=movements)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)