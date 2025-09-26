from flask import Flask, flash, redirect, render_template, request, session
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey
from wtforms import StringField, SubmitField , PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wtforms.widgets import TextArea
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields import SelectField
from wtforms.fields import FileField
import os
from werkzeug.utils import secure_filename


# Create a Flask Instance
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# create sql alchemy database
db = SQLAlchemy()

# Add Database uri to config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Secret Key
app.config["SECRET_KEY"] = "Hemlig nyckel"

# initalize the databse on the app
db.init_app(app)


# Creat User Model (table)
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Helper class to take data from html request form and convert to wtf flask form
class UserForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    username = StringField("username", validators=[DataRequired()])
    password = StringField("password:", validators=[DataRequired()])


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    title = db.Column(db.String(100))
    ingredients = db.Column(db.Text)
    instruction = db.Column(db.Text)
    portions = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)
    category = db.Column(db.Integer)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(100))  # Path to the image file


# create tables if not exists
with app.app_context():
    db.create_all()


class AddRecipeForm(FlaskForm):
    title = StringField("Receptets namn", validators=[DataRequired()])
    ingredients = StringField(
        "Ingredienser och mått", validators=[DataRequired()], widget=TextArea()
    )
    instruction = StringField(
        "Gör så här:", validators=[DataRequired()], widget=TextArea()
    )
    portions = SelectField(
        "Antal portioner",
        choices=[
            ("", "Antal portioner"),
            ("1", "1"),
            ("2", "2"),
            ("3", "4"),
            ("4", "6"),
            ("5", "8"),
        ],
        validators=[DataRequired()],
    )
    difficulty = SelectField(
        "Svårighetsgrad",
        choices=[
            ("", "Svårighetsgrad:"),
            ("1", "Lätt"),
            ("2", "Medel"),
            ("3", "Svårt"),
        ],
        validators=[DataRequired()],
    )
    category = SelectField(
        "Kategori",
        choices=[
            ("", "Kategori"),
            ("1", "Kyckling"),
            ("2", "Fisk"),
            ("3", "Kött"),
            ("4", "Vegetariskt"),
            ("5", "Veganskt"),
            ("6", "Pasta"),
            ("7", "Pizza"),
        ],
        validators=[DataRequired()],
    )
    image = FileField("Lägg upp en bild på din rätt:", validators=[DataRequired()])
    submit = SubmitField("Lägg upp!")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    # Get the posts from the database
    isAuthorized = session.get("Authorized", default=False)
    recipes = Recipe.query.order_by(Recipe.date_posted.desc()).all()

    for rec in recipes:
        if rec.difficulty == 1:
            rec.difficulty = "Lätt"
        elif rec.difficulty == 2:
            rec.difficulty = "Medel"
        elif rec.difficulty == 3:
            rec.difficulty = "Svårt"

    return render_template("index.html", isAuthorized=isAuthorized, recipes=recipes)


@app.route("/category/<int:category_id>")
def recipes_by_category(category_id):
    # Get recipes filtered by category
    isAuthorized = session.get("Authorized", default=False)
    recipes = Recipe.query.filter_by(category=category_id).order_by(Recipe.date_posted.desc()).all()
    
    # Category mapping
    category_names = {
        1: "Kyckling",
        2: "Fisk", 
        3: "Kött",
        4: "Vegetariskt",
        5: "Veganskt",
        6: "Pasta",
        7: "Pizza"
    }
    
    category_name = category_names.get(category_id, "Okänd kategori")
    
    # Convert difficulty numbers to text
    for rec in recipes:
        if rec.difficulty == 1:
            rec.difficulty = "Lätt"
        elif rec.difficulty == 2:
            rec.difficulty = "Medel"
        elif rec.difficulty == 3:
            rec.difficulty = "Svårt"

    return render_template("index.html", isAuthorized=isAuthorized, recipes=recipes, 
                         category_name=category_name, category_id=category_id)


@app.route("/search", methods=["GET", "POST"])
def search_recipes():
    isAuthorized = session.get("Authorized", default=False)
    
    if request.method == "POST":
        search_query = request.form.get("search", "").strip()
    else:
        search_query = request.args.get("q", "").strip()
    
    if not search_query:
        # If no search query, redirect to home
        return redirect("/")
    
    # Search in recipe titles and ingredients (case-insensitive)
    recipes = Recipe.query.filter(
        db.or_(
            Recipe.title.ilike(f"%{search_query}%"),
            Recipe.ingredients.ilike(f"%{search_query}%")
        )
    ).order_by(Recipe.date_posted.desc()).all()
    
    # Convert difficulty numbers to text
    for rec in recipes:
        if rec.difficulty == 1:
            rec.difficulty = "Lätt"
        elif rec.difficulty == 2:
            rec.difficulty = "Medel"
        elif rec.difficulty == 3:
            rec.difficulty = "Svårt"
    
    return render_template("index.html", isAuthorized=isAuthorized, recipes=recipes, 
                         search_query=search_query, search_results_count=len(recipes))


@app.route("/add", methods=["GET", "POST"])
def add_recipe():
    user_id = session.get("user_id")
    isAuthorized = session.get("Authorized", default=False)
    if not isAuthorized:
        return render_template("index.html")
    else:
        form = AddRecipeForm()
        if request.method == "POST":
            if "image" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["image"]
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                post = Recipe(
                    user_id=user_id,
                    title=form.title.data,
                    ingredients=form.ingredients.data,
                    instruction=form.instruction.data,
                    portions=form.portions.data,
                    difficulty=form.difficulty.data,
                    category=form.category.data,
                    image=os.path.join(app.config["UPLOAD_FOLDER"], filename),
                )

                db.session.add(post)
                db.session.commit()
                flash("Ditt recept är upplagt på hemsidan!")

        return render_template("add_recipe.html", isAuthorized=isAuthorized, form=form)


@app.route("/detail/<int:id>")
def recipe_detail(id):
    isAuthorized = session.get("Authorized", default=False)
    recipe = Recipe.query.get_or_404(id)
    return render_template(
        "recipe_detail.html", isAuthorized=isAuthorized, recipe=recipe
    )


@app.route("/detail/delete/<int:id>")
def delete_recipe(id):
    # Retrieve the logged-in user's ID
    user_id = session.get("user_id")

    # Fetch the recipe to be deleted
    recipe_to_delete = Recipe.query.get_or_404(id)

    try:
        # Check if the logged-in user's ID matches the user ID associated with the recipe
        if recipe_to_delete.user_id == user_id:
            # Delete the recipe if the user IDs match
            db.session.delete(recipe_to_delete)
            db.session.commit()
            flash("Ditt recept har raderats.")
        else:
            # If the user IDs don't match, show an error message
            flash("Du har inte behörighet att radera detta recept.")

        # Redirect to the home page
        return redirect("/")

    except Exception as e:
        # Return an error message if an exception occurs during deletion
        flash("Det gick inte att radera receptet, försök igen!")
        return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    userForm = UserForm()
    if request.method == "POST":
        # convert to fixed flask data
        password_hash = generate_password_hash(userForm.password.data)
        # create user model instance to add to the database
        user = Users(
            name=userForm.name.data,
            user_name=userForm.username.data,
            password=password_hash,
        )

        if user.name is not None and user.user_name is not None:
            # add user to the database
            db.session.add(user)
            db.session.commit()
            flash("Ditt konto har skapats")
            return redirect("/signin")

    else:
        return render_template("sign_up.html", userForm=userForm)


@app.route("/signin", methods=["POST", "GET"])
def sign_in():
    # clear session (Log out)
    session.clear()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Fetch the user from the database by username
        user = Users.query.filter_by(user_name=username).first()
        if user:
            # comparing user's password with entered password
            match = check_password_hash(user.password, password)
            if match == True:
                # start a new session for the user while he is logged in
                session["Authorized"] = True
                session["user_id"] = user.id  # Add user-ID to the session
                session["user_name"] = username
                return redirect("/")
            else:
                # Password is incorrect
                flash("Lösenord matchar inte. Försök igen.")
                return render_template("sign_in.html")
        else:
            # user does not exists
            flash("Felaktiga Inloggningsuppgiter, Försök igen!!!.")
            return render_template("sign_in.html")
    else:
        return render_template("sign_in.html")


@app.route("/re")
def re():
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
