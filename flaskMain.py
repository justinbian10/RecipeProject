import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/home/bustin/Desktop/web_dev_projects/Recipe_Project/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@localhost/recipes'
db = SQLAlchemy(app)

class MainRecipe(db.Model):
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100))
    servings = db.Column(db.Integer)
    cook_days = db.Column(db.Integer)
    cook_hours = db.Column(db.Integer)
    cook_minutes = db.Column(db.Integer)
    food_type = db.Column(db.String(200))
    ingredients = db.Column(db.Text)
    instructions = db.Column(db.Text)
    pictures = db.relationship('Pictures', backref='recipe')


    def __init__(self, recipe_name, servings, cook_days, cook_hours, cook_minutes, food_type, ingredients, instructions):
        self.recipe_name = recipe_name
        if (servings == ''):
            self.servings = None
        else:
            self.servings = int(servings)
        if (cook_days == ''):
            self.cook_days = None
        else:
            self.cook_days = int(cook_days)
        if (cook_hours == ''):
            self.cook_hours = None
        else:
            self.cook_hours = int(cook_hours)
        if (cook_minutes == ''):
            self.cook_minutes = None
        else:
            self.cook_minutes = int(cook_minutes)
        self.food_type = food_type
        self.ingredients = ingredients
        self.instructions = instructions

    def __repr__(self):
        return '<User %r>' % self.username

class Pictures(db.Model):
    picture_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('main_recipe.recipe_id'))
    picture1 = db.Column(db.String(100))

db.create_all()
db.session.commit()

recipe1 = MainRecipe('sdf', 1, 3, 3, 3, 'fef', 'efef', 'sdasdk')
db.session.add(recipe1)
db.session.commit()


recipe = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    elif request.method == 'POST':
        addRecipeValues(request)
        return recipe

def addRecipeValues(request):
    recipe.update({'recipe-name' : request.form['recipe-name'], 'servings' : request.form['servings'], 'food-type' : request.form['food-type'], 'cook-days' : request.form['cook-days'], 'cook-hours': request.form['cook-hours'], 'cook-mins' : request.form['cook-mins'], 'ingredients' : request.form['ingredients'], 'instructions': request.form['instructions']})
    tempRecipe = MainRecipe(recipe.get('recipe-name'), recipe.get('servings'), recipe.get('cook-days'), recipe.get('cook-hours'), recipe.get('cook-mins'), recipe.get('food-type'), recipe.get('ingredients'), recipe.get('instructions'))
    db.session.add(tempRecipe)
    db.session.commit()
    f = request.files.getlist('pictures[]')
    for file in f:
        filename = secure_filename(file.filename)
        if filename != '':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
