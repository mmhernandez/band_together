from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models import user, band

@app.route("/")
def login_register():
    return render_template("login_registration.html")

@app.route("/register", methods=["POST"])
def register_user():
    registration_data = {
        "first_name": request.form["fname"],
        "last_name": request.form["lname"],
        "email": request.form["email"],
        "password": request.form["password"],
        "confirm_password": request.form["confirm_password"]
    }

    if user.User.validate_registration(registration_data):
        session.clear()
        session["id"] = user.User.insert(registration_data)
        return redirect("/dashboard")
    else:
        session["fname"] = registration_data["first_name"]
        session["lname"] = registration_data["last_name"]
        session["em"] = registration_data["email"]
        return redirect("/")

@app.route("/login", methods=["POST"])
def login_user():
    login_info = {
        "email": request.form["email"],
        "password": request.form["password"]
    }
    if user.User.validate_login(login_info):
        user_info = user.User.get_by_email(login_info)
        session["id"] = user_info.id
        return redirect("/dashboard")
    else: 
        return redirect("/")

@app.route("/dashboard")
def display():
    if "id" in session:
        band_list = band.Band.get_all_with_creator(session["id"])
        user_joined_bands = user.User.get_one_with_joined_bands({"id": session["id"]})
        return render_template("dashboard.html", user=user_joined_bands, my_bands=band_list)
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")