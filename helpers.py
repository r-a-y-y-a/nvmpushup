from flask import redirect, render_template, session
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def calculator(pushup,situp,run):
    points = 0
    pushthresh = [59,55,51,47,43,39,36,33,30,27,25,24,23,22,21,20,19,18]
    sitthresh = [59,55,51,47,43,39,35,34,33,32,30,28,27,26,25,24,23,21,19,18,17,16,15,14]
    pushcount = 0
    sitcount = 0
    for i in pushthresh:
        if pushup < 15:
            points += 0
            break
        elif pushup == 18:
            points += 6
            break
        elif pushup == 17:
            points += 4
            break
        elif pushup == 16:
            points += 2
            break
        elif pushup == 15:
            points += 1
            break
        elif pushup > i:
            points += (25-pushcount)
            break
        else:
            pushcount += 1
            continue
    for i in sitthresh:
        if situp <= 14:
            points += 0
            break
        if situp > i:
            points += (25-sitcount)
            break
        else:
            sitcount += 1
            continue
    diff = run - 510
    if diff <= 0:
        points += 50
    elif run > 960:
        points += 0
    else:
        conversion = int(diff/10)
        points += (50 - (conversion+1))
    return points
