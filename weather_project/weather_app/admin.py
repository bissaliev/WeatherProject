from django.contrib import admin

from .models import City, RequestHistory

admin.site.register(City)
admin.site.register(RequestHistory)
