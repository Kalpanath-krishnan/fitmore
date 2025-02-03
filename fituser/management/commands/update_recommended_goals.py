from django.core.management.base import BaseCommand
from fituser.models import CustomUser  # ✅ Import the user model

class Command(BaseCommand):
    help = "Update recommended goal for all users based on BMI"

    def handle(self, *args, **kwargs):
        users = CustomUser.objects.all()  # ✅ Get all users
        updated_count = 0

        for user in users:
            old_goal = user.recommended_goal  # Store old goal for comparison
            user.bmi = user.calculate_bmi()  # ✅ Recalculate BMI
            user.recommended_goal = user.update_recommended_goal()  # ✅ Update goal
            user.save(update_fields=['bmi', 'recommended_goal'])  # ✅ Save only updated fields

            if old_goal != user.recommended_goal:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Updated recommended goals for {updated_count} users."))
