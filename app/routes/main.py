from flask import Blueprint, render_template
from flask_login import login_required # type: ignore
from app.decorators import roles_required
from app import db
from app.models import Product
import random

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    active_products = db.session.query(Product).filter_by(is_active=True).all()
    random_products = random.sample(active_products, min(4, len(active_products)))
    return render_template('index.html', random_products=random_products)

@main_bp.route('/our-products')
def our_products():
    products = db.session.query(Product).filter_by(is_active=True).all()
    return render_template('our-products.html', products=products)

@main_bp.route('/internal')
@login_required
@roles_required('admin', 'chef', 'seller')
def internal():
    return render_template('internal/index.html')