from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask import session as Session
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import smtplib, ssl
from paypalrestsdk import Invoice, ResourceNotFound
import paypalrestsdk

app = Flask(__name__)
Base = declarative_base()

#API STARTS HERE

def Server(id):
    global session, engine
    engine = create_engine('sqlite:///Servers/{}.sqlite3'.format(id), echo=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
            
class License(Base):
    __tablename__ = 'license'

    license = Column('license', Integer, primary_key=True)

class Credentials(Base):
    __tablename__ = 'credentials'

    id = Column('id', Integer, primary_key=True)
    password = Column('password', String)

class PayPalEmail(Base):
    __tablename__ = 'paypal_email'

    email = Column('email', String, primary_key=True)

class PayPalClientSecret(Base):
    __tablename__ = 'paypal_client_secret'

    secret = Column('secret', String, primary_key=True)

class PayPalClientID(Base):
    __tablename__ = 'paypal_client_id'

    id = Column('id', String, primary_key=True)

class UserPermission(Base):
    __tablename__ = 'user_permission'

    id = Column('user_id', Integer, primary_key=True)

class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = Column('role_id', Integer, primary_key=True)

class Product(Base):
    __tablename__ = 'products'

    name = Column('name', String, primary_key=True)
    price = Column('price', Integer)
    filename = Column('filename', String)
    description = Column('description', String)

class Order(Base):
    __tablename__ = 'orders'

    id = Column('id', Integer, unique=True, primary_key=True)
    buyer = Column('user_id', Integer)
    product = Column('product', String)
    status = Column('status', String)
    tid = Column('tid', String)

class firstName(Base):
    __tablename__ = 'first_name'

    firstName = Column('firstName', String, primary_key=True)

class lastName(Base):
    __tablename__ = 'last_name'

    lastName = Column('lastName', String, primary_key=True)

class businessName(Base):
    __tablename__ = 'business_name'

    businessName = Column('businessName', String, primary_key=True)

class Currency(Base):
    __tablename__ = 'currency'

    currency = Column('currency', String, primary_key=True)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column('id', Integer, unique=True, primary_key=True)
    time = Column('time', String)
    user = Column('user_id', Integer)
    product = Column('product', String)
    amount = Column('amount', Integer)
    tid = Column('tid', String)
    

#API ENDS HERE
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/')
def login():
    try:
        Session['user']
    except KeyError:
        return render_template('login.html')
        
    if Session['user'] is None:
        return render_template('login.html')
    else:
        return redirect(url_for('dashboard'))

@app.route('/login/', methods=['POST', 'GET'])
def loginData():
    if request.method == 'POST':
        Session.pop('user', None)
        
        serverID = request.form['serverID']
        password = request.form['password']

        Server(serverID)
        if password == session.query(Credentials).first().password:
            Session['user'] = serverID
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if not Session['user'] is None:
        Session.pop('user', None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/dashboard/')
def dashboard():
    if not Session['user'] is None:
        Server(Session['user'])
        total = 0
        try:
            for i in session.query(Transaction).all():
                total += i.amount
        except:
            pass
        total = str(total) + ' ' + session.query(Currency).first().currency

        recent1 = session.query(Transaction).all()[-1]
        recent2 = session.query(Transaction).all()[-2]
        recent3 = session.query(Transaction).all()[-3]
        return render_template('dashboard.html', id=Session['user'], earnings=total, recent1=recent1, recent2=recent2, recent3=recent3)
    else:
        return redirect(url_for('login'))
    

@app.route('/', methods=['POST', 'GET'])
def formData():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "W"  
    password = ''
    receiver_email = ""
    message = """
    Contact Form Inquiry

    First name: {}
    Last name: {}
    Email: {}
    Subject: {}
    Message: {}
    """.format(firstName, lastName, email, subject, message)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    flash('Message has been sent.')
    return render_template('index.html')

@app.route('/earnings/')
def earnings():
    if not Session['user'] is None:
        Server(Session['user'])
        total = 0
        try:
            for i in session.query(Transaction).all():
                total += i.amount
        except:
            pass
        total = str(total) + ' ' + session.query(Currency).first().currency
        return render_template('earnings.html', products=session.query(Transaction).all(), id=Session['user'], earnings=total)
    else:
        return redirect(url_for('login'))

@app.route('/products/')
def products():
    if not Session['user'] is None:
        Server(Session['user'])
        total = 0
        try:
            for i in session.query(Transaction).all():
                total += i.amount
        except:
            pass
        total = str(total) + ' ' + session.query(Currency).first().currency
        return render_template('products.html', products=session.query(Product).all(), id=Session['user'], earnings=total)
    else:
        return redirect(url_for('login'))

@app.route('/products/', methods=['POST', 'GET'])
def fileUpload():
    if not Session['user'] is None:
        Server(Session['user'])
        file = request.files['file']
        try:
            file.save('Servers/{}/{}'.format(Session['user'], file.filename))
        except:
            flash('No file was selected')
            return redirect(url_for('products'))
        flash('File uploaded to Database')
        return redirect(url_for('products'))
    else:
        return redirect(url_for('login'))

@app.route('/settings')
def settings():
    return redirect(url_for('dashboard'))

@app.route('/upgrade/')
def upgrade():
    if not Session['user'] is None:
        Server(Session['user'])
        license = session.query(License).first().license
        return render_template('upgrade.html', license=license)

@app.route('/upgrade/', methods=['POST', 'GET'])
def upgradeData():
    Server(Session['user'])
    role = request.form['role'].capitalize()
    if role == 'Premium':
        price = 5
    elif role == 'Ultimate':
        price = 15
    paypalrestsdk.configure({ "mode": 'sandbox', "client_id": '', "client_secret": 'W'})
    invoice = Invoice({
"merchant_info": {
    "email": '',
    "first_name": '',
    "last_name": '',
},
"billing_info": [{"email": request.form['paypal_email']}],
"items": [
    {
        "name": role,
        "quantity": 1,
        "unit_price": {
            "currency": 'USD',
            "value": price
        }
    }
]
})
        
    if invoice.create():
        print("Invoice[%s] successfully created." % (invoice.id))
    else:
        print(invoice.error)
    invoice = Invoice.find(invoice.id)
    if invoice.send():
        print("Invoice[%s] successfully sent to buyer." % (invoice.id))
        file = open('invoices.txt', 'a')
        file.write('{}={}={}\n'.format(Session['user'], invoice.id, price))
        file.close()
    else:
        print(invoice.error)
    flash('Invoice has been sent to your email, once you have paid the invoice, press the confirm button below.')
    license = session.query(License).first().license
    return render_template('upgrade.html', confirmation=True, license=license)

@app.route('/upgrade/')
def upgradeDataCheck():
    Server(Session['user'])
    file = open('invoices.txt', 'r')
    data = file.readlines()
    file.close()
    data = [i.replace('\n','') for i in data]
    data = [i.split('=') for i in data]
    for i in data:
        if (i[0] == Session['user']) and (Invoice.find(i[1]).status.lower() == 'paid') and (Invoice.find(i[1])['items']['unit_price']['value'] == int(i[2])):
            return 'Paid'

        
if __name__ == '__main__':
    app.secret_key = 'the random string'
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    app.run()
