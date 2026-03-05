# Autoseller

A Discord autoseller bot and Flask web dashboard for selling digital products automatically using **PayPal invoices**.  
The system allows Discord servers to list products, generate PayPal invoices for buyers, and automatically deliver files after payment confirmation.

This repository contains:

- `bot.py` → Discord autoseller bot
- `website.py` → Flask dashboard for managing products and viewing earnings

---

## Features

### Discord Bot
- Create and manage products
- Generate PayPal invoices automatically
- Create private order ticket channels
- Deliver digital products after payment confirmation
- Track transactions and earnings per server
- User and role-based admin permissions

### Web Dashboard
- Login using Discord server ID + password
- Upload product files
- View earnings and transactions
- View product list
- Basic license/upgrade purchase system

---

## Requirements

- Python **3.8+**
- Discord Bot Token
- PayPal REST API credentials
- SQLite (included with Python)

### Python Packages

Install required dependencies:

```bash
pip install discord.py Flask SQLAlchemy paypalrestsdk
```

---

## Project Structure

```
max-tan/
│
├── bot.py
├── website.py
├── Servers/
│   ├── <guild_id>.sqlite3
│   └── <guild_id>/
│       ├── product1.zip
│       └── product2.txt
└── templates/
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── earnings.html
    ├── products.html
    └── upgrade.html
```

Each Discord server has its own database and file storage folder.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/max-tan.git
cd max-tan
```

### 2. Create required folder

```bash
mkdir Servers
```

### 3. Configure Discord Bot

Open **bot.py** and set:

```python
token = "YOUR_DISCORD_BOT_TOKEN"
prefix = "$"
currency = "USD"
```

---

### 4. Run the bot

```bash
python bot.py
```

Invite the bot to your Discord server with permissions:

- Manage Channels
- Send Messages
- Attach Files

When the bot joins a server it automatically:

- Creates a database: `Servers/<guild_id>.sqlite3`
- Creates a folder: `Servers/<guild_id>/`
- Grants the server owner admin permission in the bot

---

## Configure Server Settings

Run these commands in Discord as the **server owner**:

```
$setting password set <dashboard_password>
$setting paypal_email set <your_paypal_email>
$setting paypal_client_id set <paypal_client_id>
$setting paypal_client_secret set <paypal_client_secret>
$setting first_name set <first_name>
$setting last_name set <last_name>
$setting business_name set <business_name>
$setting currency set USD
```

---

## Upload Product Files

Product files must be located at:

```
Servers/<guild_id>/<filename>
```

You can upload them using:

- The web dashboard `/products`
- Manual file upload to the server folder

---

## Create Products

Example command:

```
$createproduct My_Product 10 product.zip My digital item
```

Notes:

- Use `_` instead of spaces when typing product names.
- Price must be a number only.

List products:

```
$productlist
```

Delete product:

```
$deleteproduct <product name>
```

---

## Purchase Flow

1. Buyer runs:

```
$buy buyer@email.com Product Name
```

2. Bot creates a private ticket channel:

```
order-#
```

3. Bot generates and sends a PayPal invoice.

4. After payment, buyer runs:

```
$confirm
```

5. If invoice is **PAID**, the bot:

- Sends the product file
- Logs the transaction
- Marks order as paid

---

## Running the Web Dashboard

Start the Flask website:

```bash
python website.py
```

Open in browser:

```
http://127.0.0.1:5000/login/
```

Login with:

- **Server ID** = your Discord guild ID
- **Password** = value set using `$setting password`

---

## Dashboard Pages

| Page | Description |
|-----|-------------|
| `/dashboard/` | Earnings overview |
| `/products/` | Product list + file uploads |
| `/earnings/` | Transaction history |
| `/upgrade/` | License upgrade system |

---

## Commands

### General

```
$help
$buy <PayPal Email> <Product Name>
$confirm
$productlist
$close
$cancelorder
```

### Administration

```
$userperms add/remove @user
$roleperms add/remove @role
$setting <setting> set <value>
$createproduct <name> <price> <filename> <description>
$deleteproduct <name>
```

---

## PayPal Modes

- `bot.py` uses **live mode**
- `website.py` upgrade system uses **sandbox mode**

Make sure credentials match the mode you intend to use.

---

## Security Notes

This project is a prototype and should be improved before production use.

---

