import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    userid = session["user_id"]
    results = []
    rows = db.execute("SELECT * FROM users where id = ?", userid)
    cash = int(rows[0]["cash"])
    stocks = db.execute("SELECT * FROM stock_owners WHERE user_id = ?", userid)
    value = 0
    for stock in stocks:
        response = lookup(stock["stock"])
        totalValue = float(stock["amount"]) * float(response["price"])
        temp = {
            "stock": stock["stock"],
            "amount": stock["amount"],
            "price": response["price"],
            "totalValue": totalValue
        }
        value += totalValue
        results.append(dict(temp))
    total = value + cash
    return render_template("index.html", results =  results, total = total, cash = cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
     # User reached route via GET
    if request.method == "GET":
        return render_template("buy.html")
     # User reached route via POST
    if request.method == "POST":
        stock = request.form.get("symbol")
        shares = int(request.form.get("shares"))
    response = lookup(stock)
    if len(stock) < 1 or response == None:
        return apology("Incorrect Stock/No Input", 406)
    if int(shares) <= 0:
        return apology("0 or negative value, incorrect input", 400)
    userid = session["user_id"]
    rows = db.execute("SELECT * FROM users where id = ?", userid)
    balance = rows[0]["cash"]
    price = response["price"]
    transaction = "purchase"
    finalPrice = float(shares) * price
    # Get the data if user already has shares for this stock
    stockedOwned = db.execute("SELECT * FROM stock_owners where user_id = ? AND stock =?", userid, stock)
    print(stockedOwned)
    if finalPrice > balance:
        return apology("Insufficient funds")
    # Add the transaction as an entry to the table
    db.execute("INSERT INTO transactions (user_id, stock, price, timestamp, amount, transaction_type) values(?, ?, ?, ?, ?, ?)",userid, stock, finalPrice, datetime.datetime.now(), shares, transaction)
    newBalance = balance - finalPrice
    # Sum shares for the same stock
    if len(stockedOwned) > 0 and stockedOwned[0]["amount"] > 0:
        print("Already got stock from this company")
        shares = stockedOwned[0]["amount"] + shares
        # Update the number of shares user have for that stock
        db.execute("UPDATE stock_owners SET amount = ? WHERE user_id = ? AND stock =?", shares, userid, stock)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newBalance, userid)
        return redirect("/")
    # Add a new entry for that user with that stock
    db.execute("INSERT INTO stock_owners (user_id, stock, amount) values(?, ?, ?)",userid, stock, shares)
    # Update the new balance of the user
    db.execute("UPDATE users SET cash = ? WHERE id = ?", newBalance, userid)

    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    userid = session["user_id"]
    results = db.execute("SELECT * FROM transactions WHERE user_id = ?",userid)
    return render_template("history.html", results=results)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template("quote.html")
    if request.method == "POST":
        # Get Stock data from the iexCloud
        response = lookup(request.form.get("symbol"))
        print(response)
        return render_template("quoted.html", response=response)
    else:
        return apology("QUOTE NOT FOUND")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        # Get the input username from the webform
        username = request.form.get("username")
        # Check if the username is already existing in the DB
        row = db.execute("SELECT * FROM users WHERE username = ?", username)
        # If username already exists or it's empty
        if len(row) > 0 or len(username) == 0:
            return apology("Username already exists/empty")
        # Get the pw and the confirmation from the webform
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Check if they are not identical or empty
        if password != confirmation or len(password) < 1 or len(confirmation) < 1:
            return apology("Passwords don't match/empty")
        # Hash the password
        hashedPw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashedPw)
        return redirect("/")


    #(as by clicking a link or via redirect)
    else:
        return apology("Bad request")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    userid = session["user_id"]
    noShares = 0
    # User reached route via GET
    if request.method == "GET":
        stocks = db.execute("SELECT stock FROM stock_owners WHERE user_id =?",userid)
        print(stocks)
        return render_template("sell.html", stocks=stocks)
    # User reached route via POST
    if request.method == "POST":
        stock = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        response = lookup(stock)
        transaction = "sell"
        price = response["price"]
        print(stock)
        rows = db.execute("SELECT * FROM users WHERE id = ?", userid)
        stocks = db.execute("SELECT stock, amount FROM stock_owners WHERE user_id =? and stock = ?",userid, stock)
        ownedShares = stocks[0]["amount"]
        newAmount = ownedShares - shares
        print(f"cash: ", {rows[0]["cash"]})
        newBalance = int(rows[0]["cash"]) + (shares * price)
        if(len(stocks) < 1):
            return apology("You don't own any stocks for this share")
        if ownedShares == 0:
            return apology("You don't have 0 shares for this stock")
        if ownedShares < shares:
            return apology("Insufficient amount of shares!")
        if shares < 1:
            return apology("Transaction doesn't make sense!")
        # Add a new transaction entry for the selling
        db.execute("INSERT INTO transactions (user_id, stock, price, timestamp, amount, transaction_type) values(?, ?, ?, ?, ?, ?)",userid, stock, price, datetime.datetime.now(), shares, transaction)
        # Add a new entry for that user with that stock
        db.execute("UPDATE stock_owners SET amount = ? WHERE user_id =? AND stock = ?",newAmount, userid, stock)
        # Update the new balance of the user
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newBalance, userid)
        # Remove rows if the user sold all his shares
        db.execute("DELETE FROM stock_owners WHERE user_id =? AND amount = ?", userid, noShares)
        print(stocks)
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
