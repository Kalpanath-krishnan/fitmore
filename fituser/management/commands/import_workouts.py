import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from fituser.models import WeightLossWorkout, WeightGainWorkout, StrengthTrainingWorkout, RehabilitationWorkout
from django.db import connection  # Import connection for raw SQL queries

class Command(BaseCommand):
    help = "Import workouts from CSV files into the database"

    def reset_auto_increment(self, model):
        """Reset the auto-increment ID sequence for the given model."""
        with connection.cursor() as cursor:
            table_name = model._meta.db_table
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")  # Reset sequence

    def handle(self, *args, **kwargs):
        csv_dir = os.path.join(settings.MEDIA_ROOT, "csv/")

        csv_files = {
            "weight_loss.csv": WeightLossWorkout,
            "weight_gain.csv": WeightGainWorkout,
            "strength_training.csv": StrengthTrainingWorkout,
            "rehabilitation.csv": RehabilitationWorkout,
        }

        for filename, model in csv_files.items():
            file_path = os.path.join(csv_dir, filename)

            if not os.path.isfile(file_path):
                self.stdout.write(self.style.ERROR(f"❌ File not found: {file_path}"))
                continue  

            try:
                # Read CSV
                df = pd.read_csv(file_path)

                # Print column names for debugging
                print(f"\n=== COLUMN NAMES for {filename} ===")
                print(df.columns.tolist())  

                # Ensure required columns exist
                required_columns = ["Day", "Activity"]
                for col in required_columns:
                    if col not in df.columns:
                        raise KeyError(f"Column '{col}' not found in {filename}")

                # Delete old records before importing
                model.objects.all().delete()
                
                # Reset Auto-Increment ID Sequence
                self.reset_auto_increment(model)

                # Insert new records
                for _, row in df.iterrows():
                    model.objects.create(
                        day=row["Day"],
                        activity=row["Activity"],
                    )

                self.stdout.write(self.style.SUCCESS(f"✅ Successfully imported {filename}!"))

            except KeyError as e:
                self.stdout.write(self.style.ERROR(f"❌ Column Error in {filename}: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Import Error in {filename}: {str(e)}"))
