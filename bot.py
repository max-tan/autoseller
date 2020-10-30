import discord
from discord.ext import commands
import os
import shutil
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from paypalrestsdk import Invoice, ResourceNotFound
import paypalrestsdk
import json
from zipfile import ZipFile

#VARIABLES

token = ''
prefix = '$'
currency = 'USD'
Base = declarative_base()
bot = commands.Bot(command_prefix=prefix)
bot.remove_command("help")

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

@bot.event
async def on_message(message):
    if message.content == '{}buy'.format(prefix):
        embed=discord.Embed(title="Usage", description="```{}buy <PayPal E-Mail> <Product Name>```".format(prefix), color=0x0000ff)
        embed.add_field(name="Additional Information", value="Will create an order ticket with a message guiding you through the process.", inline=True)
        await message.channel.send(embed=embed)

    #ADMINISTRATOR COMMANDS
    if message.content == '{}userperms'.format(prefix):
        embed=discord.Embed(title="Usage", description="```{}userperms add <@user>``````{}userperms remove <@user>```".format(prefix, prefix), color=0x0000ff)
        embed.add_field(name="Additional Information", value="Will give the inputted user permissions to administrator commands.\nCan only be used by the server administrators.", inline=True)
        await message.channel.send(embed=embed)
    elif message.content == '{}roleperms'.format(prefix):
        embed=discord.Embed(title="Usage", description="```{}roleperms add <@role>``````{}roleperms remove <@role>```".format(prefix, prefix), color=0x0000ff)
        embed.add_field(name="Additional Information", value="Will give the inputted role permissions to administrator commands.\nCan only be used by the server administrators.", inline=True)
        await message.channel.send(embed=embed)
    elif message.content == '{}setting'.format(prefix):
        embed=discord.Embed(title="Usage", description="```{}setting <Setting Name> <Action> <New Value>```".format(prefix, prefix), color=0x0000ff)
        embed.add_field(name="Valid Setting Names", value="```password``````first_name``````last_name``````business_name``````paypal_email``````paypal_client_id``````paypal_client_secret``````currency```", inline=False)
        embed.add_field(name="Valid Actions", value="```set```", inline=True)
        embed.add_field(name="Additional Information", value="Will change the inputted setting to the inputted value.\nCurrency Example: USD, EUR, etc.\nAll valid currencies can be found here: https://bit.ly/35pJtNm\nCan only be used by the server owner.", inline=False)
        await message.channel.send(embed=embed)
    elif message.content == '{}createproduct'.format(prefix):
        embed=discord.Embed(title="Usage", description="```{}createproduct <Product Name> <Price> <Filename> <Description>```".format(prefix), color=0x0000ff)
        embed.add_field(name="Additional Information", value="Will create a product with the inputted product name.\nUse an _ to indicate a space in the Product name along with the Filename.\nThe Price must not include a currency, just a number.\nCan only be used by server administrators.", inline=True)
        await message.channel.send(embed=embed)
    elif message.content == '{}deleteproduct'.format(prefix):
        embed=discord.Embed(title="Usage", description="```{}deleteproduct <Product Name>```".format(prefix), color=0x0000ff)
        embed.add_field(name="Additional Information", value="Will delete the product with the inputted product name.\nCan only be used by server administrators.", inline=True)
        await message.channel.send(embed=embed)

    await bot.process_commands(message)


@bot.command()
async def userperms(ctx, action, member: discord.Member):
    Server(ctx.guild.id)
    if session.query(UserPermission).filter_by(id=ctx.author.id).first() is None:
        for role in session.query(RolePermission).all():
            user = discord.utils.get(ctx.guild.members, id=ctx.author.id)
            if discord.utils.get(ctx.guild.roles, id=role.id) in user.roles:
                perms = True
    else:
        perms = True
        
    try:
        perms
    except:
        perms = False

    if perms or ctx.author == ctx.guild.owner:
        if action == 'add':
            Server(ctx.guild.id)
            try:
                session.add(UserPermission(id=member.id))
                session.commit()
            except:
                embed=discord.Embed(title="Permissions Error", description="{} already has permissions.".format(member.mention), color=0x0000ff)
                await ctx.author.send(embed=embed)
        elif action == 'remove':
            Server(ctx.guild.id)
            try:
                user = session.query(UserPermission).filter_by(id=member.id).first()
                session.delete(user)
                session.commit()
            except:
                embed=discord.Embed(title="Permissions Error", description="{} doesn't has permissions.".format(member.mention), color=0x0000ff)
                await ctx.author.send(embed=embed)
    else:
        embed=discord.Embed(title="Permissions Error", description="You don't have permissions to use that command.\n\n{}".format(member.mention), color=0x0000ff)
        await ctx.author.send(embed=embed)

@bot.command()
async def roleperms(ctx, action, role: discord.Role):
    Server(ctx.guild.id)
    if session.query(UserPermission).filter_by(id=ctx.author.id).first() is None:
        for role in session.query(RolePermission).all():
            user = discord.utils.get(ctx.guild.members, id=ctx.author.id)
            if discord.utils.get(ctx.guild.roles, id=role.id) in user.roles:
                perms = True
    else:
        perms = True
        
    try:
        perms
    except:
        perms = False

    if perms or ctx.author == ctx.guild.owner:
        if action == 'add':
            Server(ctx.guild.id)
            try:
                session.add(RolePermission(id=role.id))
                session.commit()
            except:
                embed=discord.Embed(title="Permissions Error", description="Role {} already has permissions.".format(role.mention), color=0x0000ff)
                await ctx.author.send(embed=embed)
        elif action == 'remove':
            Server(ctx.guild.id)
            try:
                role = session.query(RolePermission).filter_by(id=role.id).first()
                session.delete(role)
                session.commit()
            except:
                embed=discord.Embed(title="Permissions Error", description="Role {} doesn't has permissions.".format(role.mention), color=0x0000ff)
                await ctx.author.send(embed=embed)


@bot.event
async def on_guild_join(guild):
    engine = create_engine('sqlite:///Servers/{}.sqlite3'.format(guild.id), echo=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    id = guild.owner.id
    owner = UserPermission(id=id)
    session.add(owner)
    session.commit()

    license = License(license=0)
    session.add(license)
    session.commit()

    os.mkdir('Servers/{}'.format(guild.id))
    

@bot.command()
async def setting(ctx, setting, action, *, value):
    await ctx.message.delete()
    if ctx.author == ctx.guild.owner:
        if action.lower() == 'set':
            if setting.lower() == 'currency':
                Server(ctx.guild.id)
                if session.query(Currency).first() is None:
                    session.add(Currency(currency=value.upper()))
                    session.commit()
                    embed=discord.Embed(title="Currency", description="The currency has been set to **{}**.".format(value.upper()), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(Currency).first())
                    session.commit()
                    session.add(Currency(currency=value.upper()))
                    session.commit()
                    embed=discord.Embed(title="Currency", description="The currency has been set to **{}**.".format(value.upper()), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            if setting.lower() == 'password':
                Server(ctx.guild.id)
                if session.query(Credentials).first() is None:
                    credentials = Credentials(id=ctx.guild.id, password=value)
                    session.add(credentials)
                    session.commit()
                    embed=discord.Embed(title="Password", description="The password has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(Credentials).first())
                    credentials = Credentials(id=ctx.guild.id, password=value)
                    session.add(credentials)
                    session.commit()
                    embed=discord.Embed(title="Password", description="The password has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            elif setting.lower() == 'paypal_email':
                Server(ctx.guild.id)
                if session.query(PayPalEmail).first() is None:
                    session.add(PayPalEmail(email=value))
                    session.commit()
                    embed=discord.Embed(title="PayPal Email", description="The PayPal Email has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(PayPalEmail).first())
                    session.commit()
                    session.add(PayPalEmail(email=value))
                    session.commit()
                    embed=discord.Embed(title="PayPal Email", description="The PayPal Email has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            elif setting.lower() == 'paypal_client_secret':
                Server(ctx.guild.id)
                if session.query(PayPalClientSecret).first() is None:
                    session.add(PayPalClientSecret(secret=value))
                    session.commit()
                    embed=discord.Embed(title="PayPal Secret", description="The PayPal Secret has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(PayPalClientSecret).first())
                    session.commit()
                    session.add(PayPalClientSecret(secret=value))
                    session.commit()
                    embed=discord.Embed(title="PayPal Secret", description="The PayPal Secret has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            elif setting.lower() == 'paypal_client_id':
                Server(ctx.guild.id)
                if session.query(PayPalClientID).first() is None:
                    session.add(PayPalClientID(id=value))
                    session.commit()
                    embed=discord.Embed(title="PayPal ID", description="The PayPal ID has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(PayPalClientID).first())
                    session.commit()
                    session.add(PayPalClientID(id=value))
                    session.commit()
                    embed=discord.Embed(title="PayPal ID", description="The PayPal ID has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            elif setting.lower() == 'first_name':
                Server(ctx.guild.id)
                if session.query(firstName).first() is None:
                    session.add(firstName(firstName=value))
                    session.commit()
                    embed=discord.Embed(title="First name", description="The First name has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(firstName).first())
                    session.commit()
                    session.add(firstName(firstName=value))
                    session.commit()
                    embed=discord.Embed(title="First name", description="The first name has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            elif setting.lower() == 'last_name':
                Server(ctx.guild.id)
                if session.query(lastName).first() is None:
                    session.add(lastName(lastName=value))
                    session.commit()
                    embed=discord.Embed(title="Last name", description="The last name has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(lastName).first())
                    session.commit()
                    session.add(lastName(lastName=value))
                    session.commit()
                    embed=discord.Embed(title="Last name", description="The last name has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            elif setting.lower() == 'business_name':
                Server(ctx.guild.id)
                if session.query(businessName).first() is None:
                    session.add(businessName(businessName=value))
                    session.commit()
                    embed=discord.Embed(title="Business name", description="The business name has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
                else:
                    session.delete(session.query(businessName).first())
                    session.commit()
                    session.add(businessName(businessName=value))
                    session.commit()
                    embed=discord.Embed(title="Business name", description="The business name has been set to **{}**.".format(value), color=0x0000ff)
                    await ctx.author.send(embed=embed)
            

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="Autoseller", url="https://www.autoseller.cc", description="The Discord Autoseller Bot is the best way to make a passive income using discord!", color=0x0000ff)
    embed.set_thumbnail(url="https://i.imgur.com/c6fIgzV.png")
    embed.add_field(name="| General [2]:", value="```{}buy - Purchase an item``` ```{}confirm - Confirm a payment```".format(prefix, prefix), inline=False)
    embed.add_field(name="| Administration [5]:", value="```{}userperms - Setup user permissions``` ```{}roleperms - Setup role permissions``` ```{}setting - Setup required settings``` ```{}createproduct - Create a product``` ```{}deleteproduct - Delete a product```".format(prefix, prefix, prefix, prefix, prefix), inline=True)
    embed.add_field(name="Product Files", value="To upload product files, head over to https://www.autoseller.cc/login", inline=False)
    embed.set_footer(text="Want to have access to unlimited products? Go to https://www.autoseller.cc")
    await ctx.channel.send(embed=embed)

@bot.command()
async def createproduct(ctx, name, price: int, filename, *, description):
    Server(ctx.guild.id)
    if session.query(UserPermission).filter_by(id=ctx.author.id).first() is None:
        for role in session.query(RolePermission).all():
            user = discord.utils.get(ctx.guild.members, id=ctx.author.id)
            if discord.utils.get(ctx.guild.roles, id=role.id) in user.roles:
                perms = True
    else:
        perms = True
        
    try:
        perms
    except:
        perms = False

    if perms or ctx.author == ctx.guild.owner:
        filename = filename.lower()
        name = name.replace('_',' ')
        filename = filename.replace('_', ' ')
        if not os.path.exists('Servers/{}/{}'.format(ctx.guild.id, filename)):
            embed=discord.Embed(title="Product Error", description="The filename **{}** doesn't exist.\n\n{}".format(filename, ctx.author.mention), color=0x0000ff)
            await ctx.channel.send(embed=embed)
        elif not session.query(Product).filter_by(name=name).first() is None:
            embed=discord.Embed(title="Product Error", description="A Product with that name already exists.\n\n{}".format(ctx.author.mention), color=0x0000ff)
            await ctx.channel.send(embed=embed)
        else:
            Server(ctx.guild.id)
            product = Product(name=name, price=price, filename=filename, description=description)
            session.add(product)
            session.commit()
            embed=discord.Embed(title="Product Created", color=0x0000ff)
            embed.add_field(name="Product Name", value=name, inline=True)
            embed.add_field(name="Price", value="{} {}".format(price, currency), inline=True)
            embed.add_field(name="Filename", value=filename, inline=True)
            embed.add_field(name="Description", value=description, inline=False)
            await ctx.channel.send(embed=embed)

@bot.command()
async def deleteproduct(ctx, *, name):
    Server(ctx.guild.id)
    if session.query(UserPermission).filter_by(id=ctx.author.id).first() is None:
        for role in session.query(RolePermission).all():
            user = discord.utils.get(ctx.guild.members, id=ctx.author.id)
            if discord.utils.get(ctx.guild.roles, id=role.id) in user.roles:
                perms = True
    else:
        perms = True
        
    try:
        perms
    except:
        perms = False
    if perms or ctx.author == ctx.guild.owner:
        if not session.query(Product).filter_by(name=name).first() is None:
            embed=discord.Embed(title="Product Deleted", description="The product **{}** has been deleted.\n\n{}".format(name, ctx.author.mention), color=0x0000ff)
            await ctx.channel.send(embed=embed)
            product = session.query(Product).filter_by(name=name).first()
            session.delete(product)
            session.commit()
        else:
            embed=discord.Embed(title="Product Error", description="The product **{}** could not be found.\n\n{}".format(name, ctx.author.mention), color=0x0000ff)
            await ctx.channel.send(embed=embed)
    else:
        embed=discord.Embed(title="Permissions Error", description="You don't have access to that command.\n\n{}".format(ctx.author.mention), color=0x0000ff)
        await ctx.channel.send(embed=embed)

@bot.command()
async def buy(ctx, pp_email, *, name):
    Server(ctx.guild.id)
    if not session.query(Product).filter_by(name=name) is None:
        await ctx.message.delete()
        Server(ctx.guild.id)
        ticket_channel_name = 'order-{}'.format(session.query(Order).count() + 1)
        channel = await ctx.guild.create_text_channel(str(ticket_channel_name))
        await channel.set_permissions(discord.utils.get(ctx.guild.roles, name="@everyone"), read_messages=False, read_message_history=False)
        await channel.set_permissions(ctx.author, read_messages=True, read_message_history=True, send_messages=True)
        paypal_client_id = session.query(PayPalClientID).first().id
        paypal_client_secret = session.query(PayPalClientSecret).first().secret
        paypal_email = session.query(PayPalEmail).first().email
        first_name = session.query(firstName).first().firstName
        last_name = session.query(lastName).first().lastName
        business_name = session.query(businessName).first().businessName
        price = session.query(Product).filter_by(name=name).first().price
        currency = session.query(Currency).first().currency
        print(paypal_client_id, paypal_client_secret)
        paypalrestsdk.configure({ "mode": 'live', "client_id": paypal_client_id, "client_secret": paypal_client_secret})
        invoice = Invoice({
"merchant_info": {
    "email": paypal_email,
    "first_name": first_name,
    "last_name": last_name,
},
"billing_info": [{"email": pp_email}],
"items": [
    {
        "name": name,
        "quantity": 1,
        "unit_price": {
            "currency": currency,
            "value": float(price)
        }
    }
]
})
        
        if invoice.create():
            print("Invoice[%s] successfully created." % (invoice.id))
            order = Order(buyer=ctx.author.id, product=name, status='unpaid', tid=invoice.id)
            session.add(order)
            session.commit()
        else:
            print(invoice.error)
        invoice = Invoice.find(invoice.id)
        if invoice.send():
            print("Invoice[%s] successfully sent to buyer." % (invoice.id))
        else:
            print(invoice.error)
        embed=discord.Embed(title="Click here to pay your invoice", url='https://paypal.com/invoice/payerView/details/{}'.format(invoice.id), color=0x0000ff)
        embed.add_field(name="Product", value=name, inline=True)
        embed.add_field(name="Price", value="{} {}".format(price, currency), inline=True)
        embed.add_field(name="Payment Method", value="PayPal", inline=True)
        embed.set_footer(text="After paying your invoice, type {}confirm.".format(prefix))
        await channel.send(embed=embed)
    else:
        embed=discord.Embed(title="Product Error", description="The product **{}** does not exist.\n\n{}".format(name, ctx.author.mention), color=0x0000ff)
        await ctx.channel.send(embed=embed)

@bot.command()
async def confirm(ctx):
    try:
        test = ctx.channel.name.split('-')
        int(test[1])
        Server(ctx.guild.id)
        if session.query(Order).filter_by(id=int(test[1])).first().buyer == ctx.author.id:
            order = session.query(Order).filter_by(id=int(test[1])).first()
            if order.status.lower() == 'paid':
                embed=discord.Embed(title="Confirmation Error", description="Your payment has already been confirmed.\n\n{}".format(ctx.author.mention), color=0x0000ff)
                await ctx.channel.send(embed=embed)
            elif order.status.lower() == 'unpaid':
                invoice = Invoice.find(order.tid)
                if invoice['status'] == 'PAID':
                    print("Invoice[%s] has successfully been paid." % (invoice.id))
                    confirmation = True
                else:
                    confirmation = False
                if confirmation == True:
                    embed=discord.Embed(title="Confirmation", description="Your payment has been confirmed.\nEnjoy your product!\n\n{}".format(ctx.author.mention), color=0x0000ff)
                    await ctx.channel.send(embed=embed)
                    filename = session.query(Product).filter_by(name=order.product).first().filename
                    await ctx.channel.send(file=discord.File('Servers/{}/{}'.format(ctx.guild.id, filename)))
                    newOrder = Order(id=order.id, buyer=order.buyer, product=order.id, status='paid', tid=order.tid)
                    session.delete(session.query(Order).filter_by(id=int(test[1])).first())
                    session.commit()
                    session.add(newOrder)
                    session.commit()
                    now = datetime.now()
                    time = now.strftime("%m/%d/%Y, %H:%M:%S")
                    amount = session.query(Product).filter_by(name=order.product).first().price
                    transaction = Transaction(time=time, user=ctx.author.id, product=order.product, amount=amount, tid=invoice.id)
                    session.add(transaction)
                    session.commit()
                else:
                    embed=discord.Embed(title="Confirmation", description="Your payment was not able to be confirmed.\n\n{}".format(ctx.author.mention), color=0x0000ff)
                    await ctx.channel.send(embed=embed)
    except Exception as e:
        print(e)
        embed=discord.Embed(title="Confirmation Error", description="You have not ordered anything.\n\n{}".format(ctx.author.mention), color=0x0000ff)
        await ctx.channel.send(embed=embed)
        
@bot.command()
async def cancelorder(ctx):
    try:
        test = ctx.channel.name.split('-')
        int(test[1])
        order = session.query(Order).filter_by(id=int(test[1])).first()
        embed = discord.Embed(title="Order Cancelled", description="You order has been cancelled.\n\n{}".format(ctx.author.mention), color=0x0000ff)
        await ctx.channel.delete()
        invoice = Invoice.find(order.tid)
        options = {
            "subject": "Past due",
            "note": "Canceling invoice",
            "send_to_merchant": True,
            "send_to_payer": True
        }

        if invoice.cancel(options):
            print("Invoice[%s] has successfully been cancelled." % (invoice.id))
            session.delete(order)
            session.commit()
        else:
            print(invoice.error)
    except:
        embed=discord.Embed(title="Order Error", description="You have not ordered anything.\n\n{}".format(ctx.author.mention), color=0x0000ff)
        await ctx.channel.send(embed=embed)


@bot.command()
async def productlist(ctx):
    Server(ctx.guild.id)
    nameDesc = ''
    priceDesc = ''
    filenameDesc = ''
    for product in session.query(Product).all():
        nameDesc += product.name + '\n'
        priceDesc += str(product.price) + '\n'
        filenameDesc += product.filename + '\n'
    embed=discord.Embed(title="Product List", color=0x0000ff)
    embed.add_field(name="Name", value=nameDesc, inline=True)
    embed.add_field(name="Price", value=priceDesc, inline=True)
    embed.add_field(name="Filename", value=filenameDesc, inline=True)
    await ctx.channel.send(embed=embed)
            

@bot.command()
async def close(ctx):
    try:
        test = ctx.channel.name.split('-')
        int(test[1])
        await ctx.channel.delete()
    except:
        pass

bot.run(token)

