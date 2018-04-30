from django.contrib import admin
from .models import Design, MediaPlan, Week, WeeklyMediaPlacement, DailyMediaPlacement, FullMediaPlacement, Expense

admin.site.register(Design)
admin.site.register(MediaPlan)
admin.site.register(Week)
admin.site.register(WeeklyMediaPlacement)
admin.site.register(DailyMediaPlacement)
admin.site.register(FullMediaPlacement)
admin.site.register(Expense)
