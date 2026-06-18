# Import Flask modules

from flask import Flask, render_template
from flask import request, redirect, session

# Import MySQL connector

import mysql.connector


# Create Flask application

app = Flask(__name__)

# Secret key for session management

app.secret_key = "cyber123"


# ---------------- MySQL Connection ----------------

# Connect Flask with MySQL database

db = mysql.connector.connect(

    host="localhost",

    user="root",

    password="Deepak",

    database="cyberfootprint"

)

# Cursor executes SQL queries

cursor = db.cursor()

print("Connected to MySQL Successfully")


# ---------------- Home Page ----------------

# Opens home.html when user visits "/"

@app.route("/")

def home():

    return render_template("home.html")


# ---------------- Register Page ----------------

# Register new user

@app.route("/register", methods=["GET", "POST"])

def register():

    # If form is submitted

    if request.method == "POST":

        # Get form data

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]


        # Check whether email already exists

        check_sql = """

        SELECT *

        FROM users

        WHERE email=%s

        """

        cursor.execute(

            check_sql,

            (email,)

        )

        user = cursor.fetchone()


        # If email exists

        if user:

            return "Email already exists"


        # Insert new user

        sql = """

        INSERT INTO users

        (

        name,

        email,

        password

        )

        VALUES

        (

        %s,

        %s,

        %s

        )

        """

        values = (

            name,

            email,

            password

        )


        cursor.execute(

            sql,

            values

        )

        db.commit()


        print("User Registered Successfully")


        return redirect("/login")


    return render_template("register.html")


# ---------------- Login Page ----------------

# Login existing user

@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        # Get email and password

        email = request.form["email"]

        password = request.form["password"]


        # Check user in database

        sql = """

        SELECT *

        FROM users

        WHERE email=%s

        AND password=%s

        """

        values = (

            email,

            password

        )


        cursor.execute(

            sql,

            values

        )


        user = cursor.fetchone()


        # Login success

        if user:

            # Store user data in session

            session["user_id"] = user[0]

            session["name"] = user[1]


            return redirect("/dashboard")


        # Login failed

        return "Invalid Email or Password"


    return render_template("login.html")


# ---------------- Dashboard ----------------

# Opens dashboard after login

@app.route("/dashboard")

def dashboard():

    # Check login

    if "user_id" not in session:

        return redirect("/login")


    user_id = session["user_id"]


    # Total analyses

    sql = """

    SELECT COUNT(*)

    FROM risk_history

    WHERE user_id=%s

    """

    cursor.execute(

        sql,

        (user_id,)

    )

    total = cursor.fetchone()[0]


    # Average score

    sql = """

    SELECT AVG(risk_score)

    FROM risk_history

    WHERE user_id=%s

    """

    cursor.execute(

        sql,

        (user_id,)

    )

    avg_score = cursor.fetchone()[0]


    if avg_score is None:

        avg_score = 0


    avg_score = round(avg_score)


    # Highest score

    sql = """

    SELECT MAX(risk_score)

    FROM risk_history

    WHERE user_id=%s

    """

    cursor.execute(

        sql,

        (user_id,)

    )

    highest_score = cursor.fetchone()[0]


    if highest_score is None:

        highest_score = 0


    return render_template(

        "dashboard.html",

        total=total,

        avg_score=avg_score,

        highest_score=highest_score

    )


# ---------------- Analyze Page ----------------

# Analyze cyber footprint

@app.route("/analyze", methods=["GET","POST"])

def analyze():

    if "user_id" not in session:

        return redirect("/login")


    if request.method=="POST":


        instagram = request.form["instagram"]

        facebook = request.form["facebook"]

        linkedin = request.form["linkedin"]

        public_email = request.form["public_email"]

        email = request.form["email"]


        score = 0


        if instagram=="yes":

            score += 25


        if facebook=="yes":

            score += 25


        if linkedin=="yes":

            score += 25


        if public_email=="yes":

            score += 25


        # Risk Level

        if score<=25:

            result="Low Risk"


        elif score<=50:

            result="Medium Risk"


        else:

            result="High Risk"


        # Email Breach Check

        sql = """

        SELECT *

        FROM breached_emails

        WHERE email=%s

        """


        cursor.execute(

            sql,

            (email,)

        )


        breach = cursor.fetchone()


        if breach:

            breach_status="Breached"

            breach_name=breach[2]

            breach_year=breach[3]


        else:

            breach_status="Safe"

            breach_name="None"

            breach_year="-"


        # Save Risk History

        user_id=session["user_id"]


        sql="""

        INSERT INTO risk_history

        (

        user_id,

        risk_score,

        risk_level

        )

        VALUES

        (

        %s,

        %s,

        %s

        )

        """


        values=(

        user_id,

        score,

        result

        )


        cursor.execute(

        sql,

        values

        )


        db.commit()


        # Save Result in Session

        session["risk"]=result

        session["score"]=score

        session["breach_status"]=breach_status

        session["breach_name"]=breach_name

        session["breach_year"]=breach_year


        return redirect("/result")


    return render_template(

        "analyze.html"

    )


# ---------------- Result Page ----------------

# Show cyber risk result

@app.route("/result")

def result():

    if "user_id" not in session:

        return redirect("/login")


    risk = session.get("risk")

    score = session.get("score")

    breach_status=session.get("breach_status")

    breach_name=session.get("breach_name")

    breach_year=session.get("breach_year")


    return render_template(

"result.html",

risk=risk,

score=score,

breach_status=breach_status,

breach_name=breach_name,

breach_year=breach_year

)

@app.route("/history")

def history():

    if "user_id" not in session:

        return redirect("/login")


    user_id = session["user_id"]


    sql = """

    SELECT *

    FROM risk_history

    WHERE user_id=%s

    ORDER BY created_at

    """


    cursor.execute(

        sql,

        (user_id,)

    )


    history = cursor.fetchall()


    scores = []

    dates = []


    for row in history:

        scores.append(

            row[2]

        )

        dates.append(

            row[4].strftime("%d-%b")

        )


    return render_template(

        "history.html",

        history=history,

        scores=scores,

        dates=dates

    )


# ---------------- Logout ----------------

# Clear session and logout

@app.route("/logout")

def logout():

    session.clear()

    return redirect("/")


# ---------------- Run Flask App ----------------

# Start Flask server

if __name__ == "__main__":

    app.run(

        debug=True

    )