import pandas as pd
from fituser.models import WeightLossWorkout, WeightGainWorkout, StrengthTrainingWorkout, RehabilitationWorkout




def import_workout_data(file_path, model):
    """Reads CSV and imports data into the model"""
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        model.objects.create(
            day=row["Day"],
            activity=row["Activity"]
        )

    print(f"✅ {model.__name__} Data Imported Successfully!")

def import_all_workouts():
    """Import all workout categories"""
    import_workout_data("media/Specific Weight Loss-Table 1.csv", WeightLossWorkout)
    import_workout_data("media/Specific Weight Gain-Table 1.csv", WeightGainWorkout)
    import_workout_data("media/Specific Strength Building-Table 1.csv", StrengthTrainingWorkout)
    import_workout_data("media/Specific Rehabilitation-Table 1.csv", RehabilitationWorkout)

