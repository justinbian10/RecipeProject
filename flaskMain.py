import os
from flask import Flask, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, func
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/Users/justinbian/Desktop/RecipeProject/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@localhost/recipes'
db = SQLAlchemy(app)

class MainRecipe(db.Model):
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100))
    servings = db.Column(db.Integer)
    cook_days = db.Column(db.Integer, nullable=False)
    cook_hours = db.Column(db.Integer, nullable=False)
    cook_minutes = db.Column(db.Integer, nullable=False)
    food_type = db.Column(db.String(200))
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    pictures = db.relationship('Pictures', backref='recipe')


    def __init__(self, recipe_name, servings, cook_days, cook_hours, cook_minutes, food_type, description, ingredients, instructions):
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
        self.description = description
        self.ingredients = ingredients
        self.instructions = instructions

class Pictures(db.Model):
    picture_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('main_recipe.recipe_id'))
    picture1 = db.Column(db.String(100))

    def __init__(self, recipe_id, pictures):
        self.recipe_id = recipe_id
        self.picture1 = pictures[0]

db.create_all()
db.session.commit()

allRecipes = []
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
    recipe.update({'recipe-name' : request.form['recipe-name'], 'servings' : request.form['servings'], 'food-type' : request.form['food-type'], 'cook-days' : request.form['cook-days'], 'cook-hours': request.form['cook-hours'], 'cook-mins' : request.form['cook-mins'], 'descriptions' : request.form['descriptions'], 'ingredients' : request.form['ingredients'], 'instructions': request.form['instructions']})
    tempRecipe = MainRecipe(recipe.get('recipe-name'), recipe.get('servings'), recipe.get('cook-days'), recipe.get('cook-hours'), recipe.get('cook-mins'), recipe.get('food-type'), recipe.get('descriptions'), recipe.get('ingredients'), recipe.get('instructions'))
    db.session.add(tempRecipe)
    db.session.flush()
    pics = []
    f = request.files.getlist('pictures[]')
    for file in f:
        filename = secure_filename(file.filename)
        if filename != '':
            pics.append(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    while len(pics) < 10:
        pics.append('')
    tempPicture = Pictures(tempRecipe.recipe_id, pics)
    db.session.add(tempPicture)
    db.session.commit()

@app.route('/uploads/<filename>/')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if (len(request.args) == 0):
        allRecipes = MainRecipe.query.all()
    else:
        nameQuery = ()
        servingQuery = ()
        typeQuery = ()
        timeQuery = ()
        allRecipes = MainRecipe.query.all()
        for var in request.args:
            if var[0:4] == 'name':
                nameQuery = nameQuery + (func.lower(MainRecipe.recipe_name).contains(func.lower(request.args.get(var))),)
            elif var[0:4] == 'type':
                typeQuery = typeQuery + (MainRecipe.food_type == request.args.get(var),)
            elif var[0:4] == 'time':
                timeVals = request.args.get(var).split('-')
                print(timeVals)
                if len(timeVals) == 2:
                    timeQuery = timeQuery + (and_((MainRecipe.cook_days * 24 + MainRecipe.cook_hours + MainRecipe.cook_minutes / 60) >= float(timeVals[0]), (MainRecipe.cook_days * 24 + MainRecipe.cook_hours + MainRecipe.cook_minutes / 60) <= float(timeVals[1])),)
                elif len(timeVals) == 1:
                    timeQuery = timeQuery + ((MainRecipe.cook_days * 24 + MainRecipe.cook_hours + MainRecipe.cook_minutes / 60) >= int(timeVals[0]),)
            elif var[0:4] == 'serv':
                if len(request.args.get(var)) == 1:
                    servingQuery = servingQuery + (MainRecipe.servings == int(request.args.get(var)),)
                else:
                    servingQuery = servingQuery + (MainRecipe.servings >= int(request.args.get(var)[0]),)
                #timeQuery = timeQuery + (MainRecipe.cook_)
        allRecipes = MainRecipe.query.filter(and_(or_(*typeQuery), or_(*nameQuery), or_(*servingQuery), or_(*timeQuery))).all()
        print(allRecipes)
    allPictures = []
    if len(allRecipes) > 0:
        for recipe in allRecipes:
            allPictures.append(Pictures.query.filter(Pictures.recipe_id == recipe.recipe_id).first())
    print(allPictures)
    numRows = int(len(allRecipes) / 5) + 1
    return render_template('search.html', recipes = allRecipes, pictures = allPictures, rows = numRows)



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
