from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import joinedload
from sqlalchemy import Index
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jmzqeonv:1WgKhEutN5IXxPPo6E0AZFpyAp2bWMFf@raja.db.elephantsql.com/jmzqeonv'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '12345'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "https://tubular-lokum-b3922e.netlify.app"}})
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String)

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    main_target = db.Column(db.String(120), nullable=False)
    secondary_target = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class UserExercise(db.Model):
    __tablename__ = 'user_exercise'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    day = db.Column(db.String(50))

    user = db.relationship('User', backref=db.backref('user_exercises', cascade='all, delete-orphan'))
    exercise = db.relationship('Exercise', backref=db.backref('exercise_users', cascade='all, delete-orphan'))

@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    data = request.get_json()
    new_exercise = Exercise(
        category=data['category'],
        name=data['name'],
        main_target=data['main_target'],
        secondary_target=data['secondary_target'],
        user_id=data['user_id']
    )
    db.session.add(new_exercise)
    db.session.commit()
    return jsonify({'message': 'Exercise added successfully'})

@app.route('/delete_exercise/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    exercise = Exercise.query.get(exercise_id)
    if exercise:
        db.session.delete(exercise)
        db.session.commit()
        return jsonify({'message': 'Exercise deleted successfully'})
    else:
        return jsonify({'message': 'Exercise not found'})
    
@app.route('/edit_exercise/<int:exercise_id>', methods=['PUT'])
def edit_exercise(exercise_id):
    exercise = Exercise.query.get(exercise_id)
    if exercise:
        data = request.get_json()
        exercise.category = data.get('category', exercise.category)
        exercise.name = data.get('name', exercise.name)
        exercise.main_target = data.get('main_target', exercise.main_target)
        exercise.secondary_target = data.get('secondary_target', exercise.secondary_target)
        exercise.user_id = data.get('user_id', exercise.user_id)
        db.session.commit()
        return jsonify({'message': 'Exercise updated successfully'})
    else:
        return jsonify({'message': 'Exercise not found'})

@app.route('/user_exercise/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_exercise(user_id):
    user_exercises = UserExercise.query.filter_by(user_id=user_id).options(joinedload(UserExercise.user), joinedload(UserExercise.exercise)).all()
    if user_exercises:
        user_exercise_data = []
        for user_exercise in user_exercises:
            user_exercise_info = {
                'id': user_exercise.id,
                'user_id': user_exercise.user_id,
                'exercise_id': user_exercise.exercise_id,
                'day': user_exercise.day,
                'user': {
                    'id': user_exercise.user.id,
                    'email': user_exercise.user.email
                },
                'exercise': {
                    'id': user_exercise.exercise.id,
                    'category': user_exercise.exercise.category
                }
            }
            user_exercise_data.append(user_exercise_info)
        return jsonify(user_exercise_data), 200
    else:
        return jsonify({'message': 'No user exercises found for the user id'}), 404

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(email=email, password=generate_password_hash(password), token=create_access_token(identity=email, expires_delta=False))
    db.session.add(new_user)
    db.session.commit()
    access_token = new_user.token
    return jsonify(access_token=access_token), 200

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid email or password"}), 401
    existing_token = user.token
    return jsonify(access_token=existing_token), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/logout', methods=['GET'])
def logout():
    return "Logout successful"

@app.route('/get_user_id/<token>', methods=['GET'])
def get_user_id(token):
    user = User.query.filter_by(token=token).first()
    if user:
        return jsonify({'user_id': user.id})
    else:
        return jsonify({'error': 'User not found for the given token'}), 404

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            current_user = User.query.filter_by(token=token).first()
            if not current_user:
                return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

        return f(current_user, *args, **kwargs)
    return decorated_function

@app.route('/add_user_exercise/<int:exercise_id>', methods=['POST'])
@token_required
def add_user_exercise(current_user, exercise_id):
    try:
        data = request.get_json()
        day = data.get('day')

        existing_user_exercise = UserExercise.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, day=day).first()
        if existing_user_exercise:
            return jsonify({"error": "Exercise already exists for this day"}), 400

        new_user_exercise = UserExercise(user_id=current_user.id, exercise_id=exercise_id, day=day)
        db.session.add(new_user_exercise)
        db.session.commit()
        return jsonify({"message": "Exercise added successfully"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/remove_user_exercise/<int:exercise_id>', methods=['DELETE'])
@token_required
def remove_user_exercise(current_user, exercise_id):
    try:
        data = request.get_json()
        day = data.get('day')

        user_exercise = UserExercise.query.filter_by(user_id=current_user.id, exercise_id=exercise_id, day=day).first()

        if user_exercise:
            db.session.delete(user_exercise)
            db.session.commit()
            return jsonify({"message": "Exercise removed successfully"})
        else:
            return jsonify({"error": "Exercise not found for the specified day and exercise id"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

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