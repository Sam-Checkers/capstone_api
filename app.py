from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jmzqeonv:1WgKhEutN5IXxPPo6E0AZFpyAp2bWMFf@raja.db.elephantsql.com/jmzqeonv'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CORS(app, resources={r"/*": {"origins": "*"}})

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    exercises = db.relationship('Exercise', backref='user', cascade='all, delete-orphan')

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    main_target = db.Column(db.String(120), nullable=False)
    secondary_target = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class UserExercise(db.Model):
    __tablename__ = 'user_exercise'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_exercises', cascade='all, delete-orphan'))
    exercise = db.relationship('Exercise', backref=db.backref('exercise_users', cascade='all, delete-orphan'))

@app.route('/register', methods=['POST'])
def register():
    try:
        email = request.json['email']
        password = request.json['password']
        hashed_password = generate_password_hash(password)
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def login_page():
    return render_template('base.html')

@app.route('/registration', methods=['GET'])
def registration_page():
    return render_template('register.html')

@app.route('/exercises')
def show_exercises():
    exercises = Exercise.query.all()
    return render_template('exercise_list.html', exercises=exercises)

@app.route('/profile/<int:user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('profile.html', user=user)
    else:
        return "User not found", 404
    
@app.route('/signin', methods=['GET'])
def show_login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # breakpoint()
    try:
        email = request.json['email']
        password = request.json['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return "Login successful"
        else:
            return "Invalid email or password", 401
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
@app.route('/add_user_exercise/<int:exercise_id>', methods=['POST'])
def add_user_exercise(exercise_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            new_user_exercise = UserExercise(user_id=user_id, exercise_id=exercise_id)
            db.session.add(new_user_exercise)
            db.session.commit()
            return "Exercise added successfully"
        else:
            return "User not logged in", 401
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
@app.route('/get_all_exercises', methods=['GET'])
def get_all_exercises():
    exercises = Exercise.query.all()
    exercise_list = []
    for exercise in exercises:
        exercise_data = {
            'id': exercise.id,
            'category': exercise.category,
            'name': exercise.name,
            'main_target': exercise.main_target,
            'secondary_target': exercise.secondary_target
        }
        exercise_list.append(exercise_data)
    return jsonify({'exercises': exercise_list})

@app.route('/get_exercise/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    exercise = Exercise.query.get(exercise_id)
    if exercise is None:
        return jsonify({'message': 'Exercise not found'}), 404
    exercise_data = {
        'id': exercise.id,
        'category': exercise.category,
        'name': exercise.name,
        'main_target': exercise.main_target,
        'secondary_target': exercise.secondary_target
    }
    return jsonify({'exercise': exercise_data})

@app.route('/get_image/<image_name>')
def get_image(image_name):
    return send_from_directory('images', image_name)

if __name__ == '__main__':
    app.run(debug=True)