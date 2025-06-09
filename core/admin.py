from django.contrib import admin
from .models import HSMData, EntrySchedule , AppKey2, Role
# Register your models here.


admin.site.register(HSMData)
admin.site.register(EntrySchedule)
admin.site.register(AppKey2)
admin.site.register(Role)