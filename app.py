from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/get_all_exercises": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gdpoxbud:MVJL5t1T6DWo_TWONVkbz80vk9prOaLm@ruby.db.elephantsql.com/gdpoxbud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    exercises = db.relationship('UserExercise', backref='user', cascade='all, delete-orphan')

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    main_target = db.Column(db.String(120), nullable=False)
    secondary_target = db.Column(db.String(120), nullable=False)
    user = db.relationship('User', backref='user_exercises', cascade='all, delete-orphan')

class UserExercise(db.Model):
    __tablename__ = 'user_exercise'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_exercises', cascade='all, delete-orphan'))
    exercise = db.relationship('Exercise', backref=db.backref('exercise_users', cascade='all, delete-orphan'))

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/exercises')
def display_exercises():
    exercises = Exercise.query.all()
    return render_template('exercises.html', exercises=exercises)

@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    if request.method == 'POST':
        data = request.get_json()
        new_exercise = Exercise(
            category=data['category'],
            name=data['name'],
            main_target=data['main_target'],
            secondary_target=data['secondary_target']
        )
        db.session.add(new_exercise)
        db.session.commit()
        return jsonify({'message': 'Exercise added successfully'})
    else:
        return jsonify({'message': 'Invalid request method'})

@app.route('/add_exercise_form', methods=['GET'])
def add_exercise_form():
    return render_template('add_exercise.html')

@app.route('/update_exercise/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    if request.method == 'PUT':
        exercise = Exercise.query.get(exercise_id)
        if exercise is None:
            return jsonify({'message': 'Exercise not found'}), 404
        data = request.get_json()
        exercise.category = data.get('category', exercise.category)
        exercise.name = data.get('name', exercise.name)
        exercise.main_target = data.get('main_target', exercise.main_target)
        exercise.secondary_target = data.get('secondary_target', exercise.secondary_target)
        db.session.commit()
        return jsonify({'message': 'Exercise updated successfully'})
    else:
        return jsonify({'message': 'Invalid request method'})

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

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = User(email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

if __name__ == '__main__':
    app.run(debug=True)