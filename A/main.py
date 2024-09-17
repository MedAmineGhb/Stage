from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '42X7-QTY9-A9P1'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'api'

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], name=user[1], password=user[2])
    return None

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        conf_password = request.form.get('conf_password')

        if not name or not password or not conf_password:
            flash("Veuillez remplir touts les champs !", "error")
        elif password != conf_password:
            flash("Les mots de passe ne correspondent pas!", "error")
        else:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM users WHERE name = %s', (name,))
            user = cursor.fetchone()

            if user:
                flash("Cet utilisateur existe déjà !", "error")
            else:
                hashed_pass = generate_password_hash(password)
                cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (name, hashed_pass))
                mysql.connection.commit()
                cursor.close()
                flash("Inscription réussie. Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for('login'))

    return render_template('inscription.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE name = %s', (name,))
        user = cursor.fetchone()
        cursor.close()

        if user is None:
            return "error: L'utilisateur n'existe pas", 400  
        else:
            stored_password = user[2]
            if check_password_hash(stored_password, password):
                user_obj = User(id=user[0], name=user[1], password=user[2])
                login_user(user_obj)  
                
                return redirect(url_for('dashboard')) 
            else:
                return "error: Nom d’utilisateur ou mot de passe incorrect", 400

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        action = request.form.get('action')
        recipe_id = request.form.get('recipe_id')
        # Handle form submission actions here if needed

    query = request.args.get('query')  # Get the search query from the URL
    if query:
        cursor.execute("""
            SELECT receips.Rid, receips.Title, receips.Contant, Categories.Categorie_name
            FROM receips
            JOIN Categories ON receips.Cid = Categories.Cid
            WHERE receips.Id = %s AND (receips.Title LIKE %s OR receips.Contant LIKE %s)
        """, (current_user.id, f'%{query}%', f'%{query}%'))
    else:
        cursor.execute("""
            SELECT receips.Rid, receips.Title, receips.Contant, Categories.Categorie_name
            FROM receips
            JOIN Categories ON receips.Cid = Categories.Cid
            WHERE receips.Id = %s
        """, (current_user.id,))
    
    recipes = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', recipes=recipes)


@app.route('/manage_recipes', methods=['GET', 'POST'])
@login_required
def manage_recipes():
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        action = request.form.get('action')
        recipe_id = request.form.get('recipe_id')

        if action == 'Add':
            cursor.execute("INSERT INTO receips (Title, Contant, Id, Cid) VALUES (%s, %s, %s, (SELECT Cid FROM Categories WHERE Categorie_name = %s))",
                           (title, description, current_user.id, category))
            mysql.connection.commit()
            flash("Recipe added successfully!")
        elif action == 'Update':
            cursor.execute("UPDATE receips SET Title = %s, Contant = %s, Cid = (SELECT Cid FROM Categories WHERE Categorie_name = %s) WHERE Rid = %s",
                           (title, description, category, recipe_id))
            mysql.connection.commit()
            flash("Recipe updated successfully!")
        elif action == 'Delete':
            cursor.execute("DELETE FROM receips WHERE Rid = %s", (recipe_id,))
            mysql.connection.commit()
            flash("Recipe deleted successfully!")
        cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT receips.Rid, receips.Title, receips.Contant, Categories.Categorie_name FROM receips JOIN Categories ON receips.Cid = Categories.Cid WHERE receips.Id = %s", (current_user.id,))
    recipes = cursor.fetchall()
    cursor.close()

    return render_template('manage_recipes.html', recipes=recipes)



if __name__ == '__main__':
    app.run(debug=True)
