from django.contrib import admin

from .models import Card, Client, Instructor, Party, PartyMembers, Kind, Hall, Schedule, ScheduleInstructor, Payment

# Добавление модели на главную страницу интерфейса администратора
admin.site.register(Card)
admin.site.register(Client)
admin.site.register(Instructor)
admin.site.register(Party)
admin.site.register(PartyMembers)
admin.site.register(Kind)
admin.site.register(Hall)
admin.site.register(Schedule)
admin.site.register(ScheduleInstructor)
admin.site.register(Payment)



