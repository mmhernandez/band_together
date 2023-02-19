from flask_app import app   
from flask import session, render_template, redirect, request
from flask_app.models import band, user

@app.route("/new/sighting")
def new_band():
    if "id" in session:
        user_info = user.User.get_by_id({"id": session["id"]})
        return render_template("new_band.html", user=user_info)
    return redirect("/")

@app.route("/band/add", methods=["POST"])
def insert_band():
    if "id" in session:
        if "name" in session:
                session.pop("name")
        if "genre" in session:
            session.pop("genre")
        if "city" in session:
                session.pop("city")
        band_data = {
            "name": request.form["name"],
            "genre": request.form["genre"],
            "city": request.form["city"],
            "creator": session["id"]
        }
        if band.Band.validate_band(request.form):
            band.Band.insert_band(band_data)
            if "name" in session:
                session.pop("name")
            if "genre" in session:
                session.pop("genre")
            if "city" in session:
                session.pop("city")
            return redirect("/dashboard")
        else:
            session["name"] = band_data["name"]
            session["genre"] = band_data["genre"]
            session["city"] = band_data["city"]
            return redirect("/new/sighting")
    return redirect("/")

@app.route("/edit/<int:id>")
def edit_band(id):
    if "id" in session:
        if "name" in session:
                session.pop("name")
        if "genre" in session:
                session.pop("genre")
        if "city" in session:
                session.pop("city")
        user_info = user.User.get_by_id({"id": session["id"]})
        band_info = band.Band.get_by_id({"id": id})
        return render_template("edit_band.html", user=user_info, band=band_info)
    return render_template("/")

@app.route("/band/update/<int:id>", methods=["POST"])
def update_band(id):
    if "id" in session:
        band_data = {
            "id": id,
            "name": request.form["name"],
            "genre": request.form["genre"],
            "city": request.form["city"],
            "creator": session["id"]
        }
        if band.Band.validate_band(band_data):
            band.Band.update_band(band_data)
            if "name" in session:
                session.pop("name")
            if "genre" in session:
                session.pop("genre")
            if "city" in session:
                session.pop("city")
            return redirect("/dashboard")
        else:
            session["name"] = band_data["name"]
            session["genre"] = band_data["genre"]
            session["city"] = band_data["city"]
            return redirect(f"/edit/{id}")
    return redirect("/")

@app.route("/delete/<int:id>")
def delete_band(id):
    if "id" in session:
        band.Band.delete_band({"id": id})
        return redirect("/dashboard")
    return redirect("/")

@app.route("/mybands")
def my_bands():
    if "id" in session:
        user_info = user.User.get_one_with_bands({"id": session["id"]})
        user_joined_bands = user.User.get_one_with_joined_bands({"id": session["id"]})
        return render_template("my_bands.html", user=user_info, user_joined_bands=user_joined_bands)
    return redirect("/")

@app.route("/join/<int:id>")
def add_band_join(id):
    if "id" in session:
        join_data = {
            "band_id": id,
            "user_id": session["id"]
        }
        band.Band.add_join(join_data)
        return redirect("/dashboard")
    return redirect("/")

@app.route("/quit/<int:id>")
def remove_band_join(id):
    print(f'id = {id}')
    if "id" in session:
        join_data = {
            "band_id": id,
            "user_id": session["id"]
        }
        band.Band.delete_band_join(join_data)
        return redirect("/mybands")
    return redirect("/")