import os

from flask import redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import date, datetime, timedelta

from helpers import login_required, lookup, str_to_dict, sums
from database_config import app, db, User, Food, Favorite

# Unnecessary to configure application, since that is done in database_config.py

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if request.form.get("action") == "date":
            # Create datetime.date object with date corresponding with the log the user would like to see
            delta = int(request.form.get("delta"))
            new_date = (datetime.strptime(request.form.get("current"), "%B %d, %Y") + timedelta(days=delta)).date()
            
            # Prevent user from trying to access future logs
            if new_date < date.today():
                # Render index.html
                foods = sorted(Food.query.filter_by(date=new_date, user=session["user_id"]).all(), key = lambda food : food.description)
                return render_template("index.html", foods=foods, date=new_date.strftime("%B %d, %Y"), sums=sums(foods))
        
        elif request.form.get("action") == "remove":
            # Remove selected food from log from the given day
            food = str_to_dict(request.form.get("food"))
            db.session.delete(Food.query.filter_by(user=session["user_id"], date=food["date"], description=food["description"]).first())
            db.session.commit()
            print
            current_date = datetime.strptime(request.form.get("date"), "%B %d, %Y").date()
            foods = sorted(Food.query.filter_by(date=current_date, user=session["user_id"]).all(), key = lambda food : food.description)
            return render_template("index.html", foods=foods, date=current_date.strftime("%B %d, %Y"), sums=sums(foods))

    # Query for list of foods logged today by this user
    foods = sorted(Food.query.filter_by(date=date.today(), user=session["user_id"]).all(), key = lambda food : food.description)
    return render_template("index.html", foods=foods, date=date.today().strftime("%B %d, %Y"), sums=sums(foods))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # Verify that a username was entered
        if len(username) == 0 or len(password) == 0:
            return render_template("register.html", error="invalid")
        
        # Verify that username does not already exist
        for existing in User.query.all():
            if username == existing.username:
                return render_template("register.html", error="already exists")
        
        # Verify that said password was entered twice and that passwords match
        if len(confirmation) == 0 or password != confirmation:
            return render_template("register.html", error="confirmation")

        # Add new user's information to database of users
        db.session.add(User(username=username, hash=generate_password_hash(password)))
        db.session.commit()

        # Redirect to index
        return redirect("/")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget current user_id
    session.clear()

    if request.method == "POST":
        # If any part of login form left blank
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("login.html", error="invalid")
        
        # Query all existing users for match with the provided username
        rows = User.query.filter_by(username=request.form.get("username"))

        # Check username and password
        if rows.count() != 1 or not check_password_hash(rows.first().hash, request.form.get("password")):
            return render_template("login.html", error="incorrect")

        # Update user_id
        session["user_id"] = rows.first().id

        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget user_id
    session.clear()

    return redirect("/")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST" and request.form.get("action") == "search":
        # Look up foods matching query
        foods = lookup(request.form.get("query"))

        # Make sure query returned at least one result, and render_template
        if (foods != None):
            return render_template("add.html", foods=foods, results=len(foods), query=request.form.get("query"))
    
    if request.method == "POST" and request.form.get("action") == "favorite":
        food = str_to_dict(request.form.get("food"))
        
        # First check to make sure there is no existing entry for this food and user in Favorite database
        if len(Favorite.query.filter_by(user=session["user_id"], description=food["description"]).all()) == 0:
            # Add food to Favorite database
            db.session.add(Favorite(
                user=session["user_id"],
                description=food["description"],
                brand=food["brand"], 
                calories=food["calories"], 
                carbs=food["carbs"],
                protein=food["protein"],
                fat=food["fat"]
            ))
            db.session.commit()

        # Rerender list of results with the same query
        foods = lookup(request.form.get("query"))
        # No need to check if there are matches to the query; if there weren't, it would be impossible to get to this point
        return render_template("add.html", foods=foods, results=len(foods), query=request.form.get("query"))

    return render_template("add.html", foods=None)

@app.route("/selection", methods=["GET", "POST"])
@login_required
def selection():
    if request.method == "POST":
        food = str_to_dict(request.form.get("food"))
        serving = int(request.form.get("serving"))
        
        existing = Food.query.filter_by(user=session["user_id"], date=date.today(), description=food["description"]).first()

        # Check to see if any entries for this food already exist in today's log 
        if existing is not None:
            # Update existing entry in today's log
            existing.serving += serving
            existing.calories += int(food["calories"]*serving/100)
            existing.carbs += int(food["carbs"]*serving/100)
            existing.protein += int(food["protein"]*serving/100)
            existing.fat += int(food["fat"]*serving/100)
        else:
            # Add selected food to database with serving-size and proper adjustments to macronutrient data
            db.session.add(Food(
                user=session["user_id"],
                date=date.today(),
                description=food["description"], 
                brand=food["brand"], 
                serving=serving, 
                calories=int(food["calories"]*serving/100), 
                carbs=int(food["carbs"]*serving/100),
                protein=int(food["protein"]*serving/100),
                fat=int(food["fat"]*serving/100)
            ))

        # Commit changes
        db.session.commit()

        return redirect("/")

    return render_template("selection.html", food=str_to_dict(request.args.get("food")))

@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    if request.method == "POST":
        # Delete selected food from Favorite database
        db.session.delete(Favorite.query.filter_by(user=session["user_id"], description=str_to_dict(request.form.get("food"))["description"]).first())
        db.session.commit()

    # Render favorites.html
    foods = sorted(Favorite.query.filter_by(user=session["user_id"]).all(), key = lambda food : food.description)
    return render_template("favorites.html", foods=foods, results=len(foods))

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        food = str_to_dict(request.form.get("food"))
        serving = int(request.form.get("serving"))

        # Query database for existing food; it will exist, and there will only be one match
        entry = Food.query.filter_by(user=session["user_id"], date=food["date"], description=food["description"]).first()

        # Scale macronutrient info
        scale = serving / entry.serving
        entry.calories = int(entry.calories * scale)
        entry.carbs = int(entry.carbs * scale)
        entry.protein = int(entry.protein * scale)
        entry.fat = int(entry.fat * scale)

        # Adjust serving size
        entry.serving = serving

        # Commit db changes
        db.session.commit()

        return redirect("/")
    
    food = str_to_dict(request.args.get("food"))
    return render_template("edit.html", food=food)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return e

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
