from django.contrib import admin
from .models import (
    CustomUser,
    WeightLossWorkout,
    WeightGainWorkout,
    StrengthTrainingWorkout,
    RehabilitationWorkout,
    # UserWorkoutTracking,
)
# Register all models in the admin panel
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'fullname', 'height', 'weight', 'bmi')  # Customize displayed fields
    search_fields = ('username', 'fullname')
    list_filter = ('bmi',)


@admin.register(WeightLossWorkout)
class WeightLossWorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'activity')
    search_fields = ('activity',)

@admin.register(WeightGainWorkout)
class WeightGainWorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'activity')
    search_fields = ('activity',)

@admin.register(StrengthTrainingWorkout)
class StrengthTrainingWorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'activity')
    search_fields = ('activity',)

@admin.register(RehabilitationWorkout)
class RehabilitationWorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'activity')
    search_fields = ('activity',)

# @admin.register(UserWorkoutTracking)
# class UserWorkoutTrackingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'goal', 'workout', 'status')
#     list_filter = ('goal', 'status')
#     search_fields = ('user__username', 'goal')
# @admin.register(UserWorkoutTracking)
# class UserWorkoutTrackingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'goal', 'get_workout_activity', 'status')  # ✅ Use custom method
#     list_filter = ('goal', 'status')
#     search_fields = ('user__username', 'goal')

#     def get_workout_activity(self, obj):
#         """Retrieve the workout name based on workout_id and goal."""
#         workout_model_map = {
#             'weight_loss': WeightLossWorkout,
#             'weight_gain': WeightGainWorkout,
#             'strength_building': StrengthTrainingWorkout,
#             'rehabilitation': RehabilitationWorkout
#         }
        
#         model = workout_model_map.get(obj.goal)  # Select correct model based on goal
        
#         if model:
#             workout = model.objects.filter(id=obj.workout_id).first()
#             return workout.activity if workout else "Workout Not Found"
#         return "Invalid Goal"

#     get_workout_activity.short_description = "Workout"  #