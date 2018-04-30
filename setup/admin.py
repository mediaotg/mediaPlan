from django.contrib import admin
from .models import TargetGroup, Publication, Client, Rate, Image

admin.site.register(TargetGroup)
admin.site.register(Publication)
admin.site.register(Client)
admin.site.register(Rate)
admin.site.register(Image)
