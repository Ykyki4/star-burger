from django.contrib import admin

from geoapp.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass
