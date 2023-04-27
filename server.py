from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import *
from forms.user import *
from forms.market import MarketForm
from forms.cart import CartForm
from data.cart import Cart
from data.market import Market
from forms.wallet import WalletForm
from data.wallet import Wallet

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'mykey_secret_key'


def main():
    db_session.global_init("db/shop.db")
    app.run()


@app.route('/', methods=['GET', 'POST'])
def home():
    db_sess = db_session.create_session()
    products = db_sess.query(Market)
    if current_user.is_authenticated:
        wallet = (db_sess.query(Wallet).filter(Wallet.user_id == current_user.id).first())
        balance = wallet.balance
    else:
        balance = 0
    return render_template('index.html', products=products, balance=balance)


@app.route('/cart')
@login_required
def cart():
    db_sess = db_session.create_session()
    _cart = db_sess.query(Cart).filter(Cart.user_id == current_user.id)
    cheque = 0
    wallet = (db_sess.query(Wallet).filter(Wallet.user_id == current_user.id).first())
    balance = wallet.balance
    for i in _cart:
        cheque += int(i.price) * int(i.value)
    return render_template('cart.html', _cart=_cart, cheque=cheque, balance=balance)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    logout_user()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            admin_key=form.admin_key.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        wallet = Wallet(
            balance=0,
            user_id=user.id
        )
        db_sess.add(wallet)
        db_sess.commit()

        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/market', methods=['GET', 'POST'])
@login_required
def add_products():
    form = MarketForm()
    flag = True
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        market = Market()
        for i in db_sess.query(Market):
            if str(i.product_name) == str(form.product_name.data) and str(i.description) == str(
                    form.description.data) and str(i.price) == str(form.price.data):
                db_sess.delete(i)
                i.value = str(int(i.value) + int(form.value.data))
                db_sess.merge(i)
                db_sess.commit()
                flag = False
        if flag:
            market.product_name = form.product_name.data
            market.description = form.description.data
            market.price = form.price.data
            market.value = form.value.data
            db_sess.merge(market)
            db_sess.commit()
    return render_template('market.html', title='Добавление товара',
                           form=form)


@app.route('/add_to_cart/<int:id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Market).filter(Market.id == id).first()
    if product:
        cart = Cart()
        cart.product_name = product.product_name
        cart.description = product.description
        cart.price = product.price
        cart.value = 1
        current_user.cart.append(cart)
        db_sess.merge(current_user)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/change_value/<int:id>', methods=['GET', 'POST'])
@login_required
def change_value(id):
    form = CartForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        cart = db_sess.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).first()
        if cart:
            form.value.data = cart.value
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cart = db_sess.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).first()
        if cart:
            if form.value.data < 0:
                form.value.data = 0
            cart.value = form.value.data
            db_sess.commit()
            return redirect('/cart')
        else:
            abort(404)
    return render_template('value_edit.html', form=form)


@app.route('/add_money', methods=['GET', 'POST'])
@login_required
def add_money():
    form = WalletForm()
    db_sess = db_session.create_session()
    wallet = (db_sess.query(Wallet).filter(Wallet.user_id == current_user.id).first())
    balance = wallet.balance
    if request.method == "GET":
        if wallet:
            form.value.data = wallet.balance
        else:
            abort(404)
    if form.validate_on_submit():
        if wallet:
            if (form.value.data) < 0:
                    form.value.data = 0
            wallet.balance += int(form.value.data)
            db_sess.commit()
            return redirect('/')
    return render_template('add_money.html', form=form, balance=balance)


@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    db_sess = db_session.create_session()
    product = db_sess.query(Cart).filter(Cart.user_id == current_user.id)
    wallet = db_sess.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    balance = wallet.balance
    if product:
        full_price = 0
        for i in product:
            for j in db_sess.query(Market):
                if str(j.product_name) == str(i.product_name) and str(j.price) == str(i.price) and str(j.description) \
                        == str(i.description):
                    y = j.value
                    full_price += (int(i.price) * int(i.value))
                    if not y:
                        y = 0
                    else:
                        y = int(y)
                    x = y - int(i.value)
                    if x >= 0:
                        j.value = str(x)
                        db_sess.delete(i)
                        db_sess.commit()
                    else:
                        db_sess.delete(i)
                        db_sess.commit()
                        return render_template('/cart.html',
                                               message=f'Количество товара: "{j.product_name}" в корзине превышает,'
                                                       f'количество товара: "{j.product_name}"  на складе.',
                                               balance=balance, cheque=0)
        print(full_price)
        if full_price > balance:
            return render_template('/cart.html',
                                   message='Недостаточно денег. Пополните баланс',
                                   balance=balance)
        else:
            balance -= full_price
            wallet = db_sess.query(Wallet).filter(Wallet.user_id == current_user.id).first()
            wallet.balance = balance
        db_sess.commit()
    else:
        abort(404)
    return render_template('/cart.html', balance=balance, cheque=0)


if __name__ == '__main__':
    main()
