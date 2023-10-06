
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, calculator

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    if session['user_id']:
        callsign = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]['callsign']
        return render_template("index.html", callsign = callsign)
    else:
        return redirect('/login')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("callsign"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE callsign = ?", request.form.get("callsign"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        callsign = request.form.get("callsign")
        coy = request.form.get("coy")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not callsign or not password or not confirm or not coy:
            return apology("Bro you don't know how to fill out form isit?")
        elif password != confirm:
            return apology("Bro help abit eh, password also can type wrongly.")
        elif "\'" in callsign or "\"" in callsign:
            return apology("Bro take out the quotation mark.")
        elif int(coy) not in [1,2,3,4,5,6]:
            return apology("Testing me isit? Give me your coy number la.")
        else:
            hashpass = generate_password_hash(password)
        row = db.execute("SELECT count(callsign) FROM users WHERE callsign = ?", callsign)
        if row[0]['count(callsign)'] > 0:
            return apology("Eh this one register already la. PUSHUP.")
        else:
            db.execute("INSERT INTO users (callsign,company,password) VALUES (?,?,?)", callsign, coy, hashpass)
            return redirect("/")

@app.route("/record", methods=["GET", "POST"])
@login_required
def record():
    if request.method == 'GET':
        return render_template("record.html")
    elif request.method == 'POST':
        callsign = db.execute("SELECT * FROM users WHERE id = ?",session['user_id'])[0]['callsign']
        yymmdd = request.form.get('yymmdd')
        pushup = int(request.form.get('pushup'))
        situp = int(request.form.get('situp'))
        mins = int(request.form.get('mins'))
        secs = int(request.form.get('secs'))
        checker = db.execute("SELECT COUNT(id) FROM ippt WHERE yymmdd = ? AND sessionid = ?",yymmdd,session['user_id'])[0]['COUNT(id)']
        if checker > 0:
            return apology("Eh, either is you submit twice, or your budddy submit for you already.")
        if int(yymmdd) < 0 or pushup < 0 or situp < 0 or mins < 0 or secs < 0:
            return apology("Eh, give me actual numbers can?")
        if not yymmdd or len(yymmdd) != 6 or yymmdd.isdigit() == False:
            return apology("Bro, give a proper date can?")
        if not pushup or not situp or not mins or not secs:
            return apology("Bro, fill out all the fields can?")
        time = (60 * mins) + secs
        points = calculator(pushup,situp,time)
        if points <= 50:
            grade = 'FAIL'
        elif points <= 74:
            grade = 'PASS'
        elif points <= 89:
            grade = 'SILVER'
        else:
            grade = 'GOLD'
        db.execute("INSERT INTO ippt (sessionid,yymmdd,pushup,situps,mins,secs,points,grade) VALUES (?,?,?,?,?,?,?,?)",session['user_id'],yymmdd,pushup,situp,mins,secs,points,grade)
        count = db.execute("SELECT COUNT(id) FROM latest WHERE id = ?",session['user_id'])[0]["COUNT(id)"]
        if int(count) > 0:
            db.execute("UPDATE latest SET callsign = ?, pushup = ?, situp = ?, mins = ?, secs = ?, points = ?, grade = ? WHERE id = ?",callsign,pushup,situp,mins,secs,points,grade,session['user_id'])
        else:
            db.execute("INSERT INTO latest (id, callsign,pushup,situp,mins,secs,points,grade) VALUES (?,?,?,?,?,?,?,?)", session['user_id'], callsign, pushup, situp,mins,secs,points,grade)
        return redirect('/')


@app.route("/leaderboard", methods = ['GET'])
@login_required
def leaderboard():
    row = db.execute("SELECT * FROM latest WHERE id IN (SELECT id FROM users WHERE company = (SELECT company FROM users WHERE id = ?)) ORDER BY points DESC, callsign DESC",session['user_id'])
    return render_template('leaderboard.html', row = row)

@app.route("/progress", methods = ['GET'])
@login_required
def progress():
    row = db.execute("SELECT * FROM ippt WHERE sessionid = ? ORDER BY yymmdd DESC", session['user_id'])
    return render_template('progress.html', row=row)