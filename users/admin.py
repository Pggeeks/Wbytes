from django.contrib import admin

from users.models import CustomUser

# Register your models here.
admin.site.site_header = "WhatBytes Assignment"
admin.site.site_title = "WhatBytes Assignment"
admin.site.register(CustomUser)