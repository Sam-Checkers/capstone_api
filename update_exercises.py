from app import app, db
from app import Exercise

# Create an application context
app.app_context().push()
exercise_data = {
    "exercises": [
		{
			"category": "chest",
			"main_target": "Chest",
			"name": "Push-ups",
			"secondary_target": "abdomen/deltoids/triceps"
		},
		{
			"category": "chest",
			"main_target": "Chest",
			"name": "Bench Press",
			"secondary_target": "deltoids/triceps"
		},
		{
			"category": "chest",
			"main_target": "Chest",
			"name": "Pectoral Fly",
			"secondary_target": "deltoids/triceps"
		},
		{
			"category": "back",
			"main_target": "Lats",
			"name": "Barbell Row",
			"secondary_target": "traps"
		},
		{
			"category": "back",
			"main_target": "Lats",
			"name": "Pull-ups",
			"secondary_target": "traps/biceps/forearms"
		},
		{
			"category": "back",
			"main_target": "Lats",
			"name": "Pull-downs",
			"secondary_target": "traps/chest"
		},
		{
			"category": "back",
			"main_target": "Traps",
			"name": "Shoulder Shrug",
			"secondary_target": "neck/deltoids"
		},
		{
			"category": "back",
			"main_target": "Traps",
			"name": "Inverted Row",
			"secondary_target": "lats/biceps"
		},
		{
			"category": "core",
			"main_target": "Obliques",
			"name": "Side Plank",
			"secondary_target": "abs"
		},
		{
			"category": "core",
			"main_target": "Obliques",
			"name": "Bicycle Crunches",
			"secondary_target": "abs"
		},
		{
			"category": "core",
			"main_target": "Obliques",
			"name": "Russian Twist",
			"secondary_target": "abs/hips"
		},
		{
			"category": "core",
			"main_target": "Abs",
			"name": "Front Plank",
			"secondary_target": "obliques"
		},
		{
			"category": "core",
			"main_target": "Abs",
			"name": "Sit-ups",
			"secondary_target": "obliques"
		},
		{
			"category": "arms",
			"main_target": "Biceps",
			"name": "Bicep Curl",
			"secondary_target": "forearms"
		},
		{
			"category": "arms",
			"main_target": "Triceps",
			"name": "Dips",
			"secondary_target": "deltoids/chest"
		},
		{
			"category": "arms",
			"main_target": "Triceps",
			"name": "Skull Crushers",
			"secondary_target": "lats"
		},
		{
			"category": "arms",
			"main_target": "Forearms",
			"name": "Wrist Curl",
			"secondary_target": "N/A"
		},
		{
			"category": "legs",
			"main_target": "Quads",
			"name": "Squat",
			"secondary_target": "glutes/abs"
		},
		{
			"category": "legs",
			"main_target": "Quads",
			"name": "Leg Press",
			"secondary_target": "glutes/hamstrings"
		},
		{
			"category": "legs",
			"main_target": "Calves",
			"name": "Calf Raises",
			"secondary_target": "glutes/hamstrings"
		},
		{
			"category": "legs",
			"main_target": "Hamstrings",
			"name": "Leg Curls",
			"secondary_target": "N/A"
		},
		{
			"category": "cardio",
			"main_target": "Cardio",
			"name": "Jogging",
			"secondary_target": "calves/hamstrings/glutes"
		},
		{
			"category": "cardio",
			"main_target": "Cardio",
			"name": "Biking",
			"secondary_target": "hamstrings/glutes"
		},
		{
			"category": "cardio",
			"main_target": "Cardio",
			"name": "Jumping Rope",
			"secondary_target": "calves"
		},
		{
			"category": "cardio",
			"main_target": "Cardio",
			"name": "Swimming",
			"secondary_target": "chest"
		}
    ]
}

with app.app_context():
    for exercise_info in exercise_data['exercises']:
        exercise = Exercise(
            category=exercise_info['category'],
            main_target=exercise_info['main_target'],
            name=exercise_info['name'],
            secondary_target=exercise_info['secondary_target']
        )
        db.session.add(exercise)

    db.session.commit()