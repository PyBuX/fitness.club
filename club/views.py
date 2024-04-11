from django.shortcuts import render, redirect

# Класс HttpResponse из пакета django.http, который позволяет отправить текстовое содержимое.
from django.http import HttpResponse, HttpResponseNotFound
# Конструктор принимает один обязательный аргумент – путь для перенаправления. Это может быть полный URL (например, 'https://www.yahoo.com/search/') или абсолютный путь без домена (например, '/search/').
from django.http import HttpResponseRedirect

from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

#from django.db.models import Max
from django.db.models import Q

from datetime import datetime, timedelta

# Подключение моделей
from .models import Card, Client, Instructor, Party, PartyMembers, Kind, Hall, Schedule, ScheduleInstructor, Payment
# Подключение форм
from .forms import CardForm, ClientForm, InstructorForm, PartyForm, PartyMembersForm, KindForm, HallForm, ScheduleForm, ScheduleInstructorForm, PaymentForm, SignUpForm

from django.db.models import Sum
#from django.db import models

#import sys

#import math

from django.utils.translation import gettext_lazy as _

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.contrib.auth import login as auth_login

#from django.db.models.query import QuerySet

from django.contrib.auth.decorators import user_passes_test

# Create your views here.
# Групповые ограничения
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

###################################################################################################

# Стартовая страница 
def index(request):
    try:
        #instructor = Instructor.objects.all().order_by('full_name')
        kind = Kind.objects.all().order_by('kind_title')
        schedule = Schedule.objects.all().order_by('start_date', 'kind__kind_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по типу услуги
                selected_item_kind = request.POST.get('item_kind')
                #print(selected_item_kind)
                if selected_item_kind != '-----':
                    kind_query = Kind.objects.filter(kind_title = selected_item_kind).only('id').all()
                    schedule = schedule.filter(kind_id__in = kind_query)
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    party_query = Party.objects.filter(party_title__contains = title_search).only('id').all()                    
                    schedule = schedule.filter(party_id__in = party_query)                
                return render(request, "index.html", {"schedule": schedule, "kind": kind, "selected_item_kind": selected_item_kind,  "title_search": title_search })    
            else:          
                return render(request, "index.html", {"schedule": schedule, "kind": kind, })
        else:
            return render(request, "index.html", {"schedule": schedule, "kind": kind,  })           
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Отчет 1
@login_required
@user_passes_test(lambda u: u.is_superuser)
def report_1(request):
    try:
        report = Client.objects.raw("""
SELECT 1 as id, client.full_name, kind.kind_title, SUM(kind.price) AS val
FROM client 
LEFT JOIN party_members ON client.id=party_members.client_id
LEFT JOIN party ON party_members.party_id=party.id
LEFT JOIN schedule ON party.id=schedule.party_id
LEFT JOIN kind ON schedule.kind_id=kind.id
GROUP BY client.full_name, kind.kind_title
""")
        return render(request, "report/report_1.html", {"report": report,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Отчет 2
@login_required
#@user_passes_test(lambda u: u.is_superuser)
def report_2(request):
    try:
        # Получить инструктора
        instructor = Instructor.objects.get(user_id=request.user.id)        
        where = "instructor.id=" + str(instructor.id);
        # Диапазон дат
        start_date = datetime(datetime.now().year, 1, 1, 0, 0).strftime('%Y-%m-%d') 
        finish_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).strftime('%Y-%m-%d') 
        selected_item_client = None
        client = Client.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дате
                start_date = request.POST.get("start_date")
                #print(start_date)
                finish_date = request.POST.get("finish_date")
                finish_date = str(datetime.strptime(finish_date, "%Y-%m-%d") + timedelta(days=1))
                #print(finish_date)
                if where != "":
                    where = where + " AND "        
                where = "instructor.id=" + str(instructor.id) + " AND schedule.start_date>='" + start_date + "' AND schedule.start_date<='" + finish_date + "'"
                #print(where)
                finish_date = request.POST.get("finish_date")
                # Добавить ключевое слово WHERE 
        if where != "":
            where = " WHERE " + where + " "              
        print(where)
        report = Schedule.objects.raw("""
SELECT 1 as id, schedule.start_date, schedule.finish_date, hall.hall_title, kind.kind_title, party.party_title, instructor.full_name
FROM schedule 
LEFT JOIN hall ON schedule.hall_id=hall.id
LEFT JOIN kind ON schedule.kind_id=kind.id
LEFT JOIN party ON schedule.party_id=party.id
LEFT JOIN schedule_instructor ON schedule.id=schedule_instructor.schedule_id
LEFT JOIN instructor ON schedule_instructor.instructor_id=instructor.id
""" + where +
"""
ORDER BY schedule.start_date
""")
        return render(request, "report/report_2.html", {"report": report, "start_date": start_date, "finish_date": finish_date,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Отчет 3
@login_required
#@user_passes_test(lambda u: u.is_superuser)
def report_3(request):
    try:
        # Получить инструктора
        instructor = Instructor.objects.get(user_id=request.user.id)        
        where = "instructor.id=" + str(instructor.id);
        # Диапазон дат
        start_date = datetime(datetime.now().year, 1, 1, 0, 0).strftime('%Y-%m-%d') 
        finish_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).strftime('%Y-%m-%d') 
        selected_item_client = None
        client = Client.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дате
                start_date = request.POST.get("start_date")
                #print(start_date)
                finish_date = request.POST.get("finish_date")
                finish_date = str(datetime.strptime(finish_date, "%Y-%m-%d") + timedelta(days=1))
                #print(finish_date)
                if where != "":
                    where = where + " AND "        
                where = "instructor.id=" + str(instructor.id) + " AND schedule.start_date>='" + start_date + "' AND schedule.start_date<='" + finish_date + "'"
                #print(where)
                finish_date = request.POST.get("finish_date")
                # Добавить ключевое слово WHERE 
        if where != "":
            where = " WHERE " + where + " "              
        print(where)
        report = Schedule.objects.raw("""
SELECT 1 as id, schedule.start_date, schedule.finish_date, hall.hall_title, kind.kind_title, party.party_title, client.full_name
FROM schedule 
LEFT JOIN hall ON schedule.hall_id=hall.id
LEFT JOIN kind ON schedule.kind_id=kind.id
LEFT JOIN party ON schedule.party_id=party.id
LEFT JOIN schedule_instructor ON schedule.id=schedule_instructor.schedule_id
LEFT JOIN instructor ON schedule_instructor.instructor_id=instructor.id
LEFT JOIN party_members ON party.id=party_members.party_id
LEFT JOIN client ON party_members.client_id=client.id
""" + where +
"""
ORDER BY schedule.start_date
""")
        return render(request, "report/report_3.html", {"report": report, "start_date": start_date, "finish_date": finish_date,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)


###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def card_index(request):
    try:
        card = Card.objects.all().order_by('card_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    card = card.filter(card_title__contains = title_search)                
                return render(request, "card/index.html", {"card": card,  "title_search": title_search })    
            else:          
                return render(request, "card/index.html", {"card": card, })
        else:
            return render(request, "card/index.html", {"card": card, })       
        return render(request, "card/index.html", {"card": card,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def card_create(request):
    try:
        if request.method == "POST":
            card = Card()
            card.card_title = request.POST.get("card_title")
            cardform = CardForm(request.POST)
            if cardform.is_valid():
                card.save()
                return HttpResponseRedirect(reverse('card_index'))
            else:
                return render(request, "card/create.html", {"form": cardform})
        else:        
            cardform = CardForm()
            return render(request, "card/create.html", {"form": cardform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def card_edit(request, id):
    try:
        card = Card.objects.get(id=id)
        if request.method == "POST":
            card.card_title = request.POST.get("card_title")
            cardform = CardForm(request.POST)
            if cardform.is_valid():
                card.save()
                return HttpResponseRedirect(reverse('card_index'))
            else:
                return render(request, "card/edit.html", {"form": cardform})
        else:
            # Загрузка начальных данных
            cardform = CardForm(initial={'card_title': card.card_title, })
            return render(request, "card/edit.html", {"form": cardform})
    except Card.DoesNotExist:
        return HttpResponseNotFound("<h2>Card not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def card_delete(request, id):
    try:
        card = Card.objects.get(id=id)
        card.delete()
        return HttpResponseRedirect(reverse('card_index'))
    except Card.DoesNotExist:
        return HttpResponseNotFound("<h2>Card not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def card_read(request, id):
    try:
        card = Card.objects.get(id=id) 
        return render(request, "card/read.html", {"card": card})
    except Card.DoesNotExist:
        return HttpResponseNotFound("<h2>Card not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_index(request):
    try:
        client = Client.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    client = client.filter(full_name__contains = title_search)                
                return render(request, "client/index.html", {"client": client,  "title_search": title_search })    
            else:          
                return render(request, "client/index.html", {"client": client, })
        else:
            return render(request, "client/index.html", {"client": client, })       
        return render(request, "client/index.html", {"client": client,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
@login_required
def client_list(request):
    try:
        ## Получить id клиента, посетившего данного доктора
        #instructor = Instructor.objects.get(user_id=request.user.id)        
        #client_query = Visit.objects.filter(doctor_id=doctor.id).only('client_id').all()
        ## Получить только данных лиентов
        #client = Client.objects.filter(id__in = client_query).order_by('full_name')
        client = Client.objects.all().order_by('full_name')
        return render(request, "client/list.html", {"client": client,})
    except Exception as exception:
        print(exception)
        return render(request, "client/list.html", {"client": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_create(request):
    try:
        if request.method == "POST":
            client = Client()
            client.full_name = request.POST.get("full_name")
            client.birthday = request.POST.get("birthday")
            client.sex = request.POST.get("sex")
            client.phone = request.POST.get("phone")
            client.card = Card.objects.filter(id=request.POST.get("card")).first()                        
            clientform = ClientForm(request.POST)
            if clientform.is_valid():
                client.save()
                return HttpResponseRedirect(reverse('client_index'))
            else:
                return render(request, "client/create.html", {"form": clientform})
        else:        
            clientform = ClientForm(initial={ 'birthday': datetime.now().strftime('%Y-%m-%d')})
            return render(request, "client/create.html", {"form": clientform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_edit(request, id):
    try:
        client = Client.objects.get(id=id)
        if request.method == "POST":
            client.full_name = request.POST.get("full_name")
            client.birthday = request.POST.get("birthday")
            client.sex = request.POST.get("sex")
            client.phone = request.POST.get("phone")
            client.card = Card.objects.filter(id=request.POST.get("card")).first()
            clientform = ClientForm(request.POST)
            if clientform.is_valid():
                client.save()
                return HttpResponseRedirect(reverse('client_index'))
            else:
                return render(request, "client/edit.html", {"form": clientform})
        else:
            # Загрузка начальных данных
            clientform = ClientForm(initial={'full_name': client.full_name, 'birthday': client.birthday.strftime('%Y-%m-%d'), 'sex': client.sex, 'phone': client.phone, 'card': client.card,  })
            return render(request, "client/edit.html", {"form": clientform})
    except Client.DoesNotExist:
        return HttpResponseNotFound("<h2>Client not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_delete(request, id):
    try:
        client = Client.objects.get(id=id)
        client.delete()
        return HttpResponseRedirect(reverse('client_index'))
    except Client.DoesNotExist:
        return HttpResponseNotFound("<h2>Client not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def client_read(request, id):
    try:
        client = Client.objects.get(id=id) 
        return render(request, "client/read.html", {"client": client})
    except Client.DoesNotExist:
        return HttpResponseNotFound("<h2>Client not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def instructor_index(request):
    try:
        instructor = Instructor.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    instructor = instructor.filter(full_name__contains = title_search)                
                return render(request, "instructor/index.html", {"instructor": instructor,  "title_search": title_search })    
            else:          
                return render(request, "instructor/index.html", {"instructor": instructor, })
        else:
            return render(request, "instructor/index.html", {"instructor": instructor, })       
        return render(request, "instructor/index.html", {"instructor": instructor,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
def instructor_list(request):
    try:
        instructor = Instructor.objects.all().order_by('full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    instructor = instructor.filter(full_name__contains = title_search)                
                return render(request, "instructor/list.html", {"instructor": instructor,  "title_search": title_search })    
            else:          
                return render(request, "instructor/list.html", {"instructor": instructor, })

        return render(request, "instructor/list.html", {"instructor": instructor,})
    except Exception as exception:
        print(exception)
        return render(request, "instructor/list.html", {"instructor": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def instructor_create(request):
    try:
        if request.method == "POST":
            instructor = Instructor()
            instructor.full_name = request.POST.get("full_name")
            instructor.sex = request.POST.get("sex")
            instructor.phone = request.POST.get("phone")
            instructor.user = User.objects.filter(id=request.POST.get("user")).first()                       
            instructorform = InstructorForm(request.POST)
            if instructorform.is_valid():
                instructor.save()
                return HttpResponseRedirect(reverse('instructor_index'))
            else:
                return render(request, "instructor/create.html", {"form": instructorform})
        else:        
            instructorform = InstructorForm()
            return render(request, "instructor/create.html", {"form": instructorform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def instructor_edit(request, id):
    try:
        instructor = Instructor.objects.get(id=id)
        if request.method == "POST":
            instructor.full_name = request.POST.get("full_name")
            instructor.sex = request.POST.get("sex")
            instructor.phone = request.POST.get("phone")
            instructor.user = User.objects.filter(id=request.POST.get("user")).first()  
            instructorform = InstructorForm(request.POST)
            if instructorform.is_valid():
                instructor.save()
                return HttpResponseRedirect(reverse('instructor_index'))
            else:
                return render(request, "instructor/edit.html", {"form": instructorform})
        else:
            # Загрузка начальных данных
            instructorform = InstructorForm(initial={'full_name': instructor.full_name, 'sex': instructor.sex, 'phone': instructor.phone, 'user': instructor.user,  })
            return render(request, "instructor/edit.html", {"form": instructorform})
    except Instructor.DoesNotExist:
        return HttpResponseNotFound("<h2>Instructor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def instructor_delete(request, id):
    try:
        instructor = Instructor.objects.get(id=id)
        instructor.delete()
        return HttpResponseRedirect(reverse('instructor_index'))
    except Instructor.DoesNotExist:
        return HttpResponseNotFound("<h2>Instructor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def instructor_read(request, id):
    try:
        instructor = Instructor.objects.get(id=id) 
        return render(request, "instructor/read.html", {"instructor": instructor})
    except Instructor.DoesNotExist:
        return HttpResponseNotFound("<h2>Instructor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)


###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_index(request):
    try:
        party = Party.objects.all().order_by('party_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    party = party.filter(party_title__contains = title_search)                
                return render(request, "party/index.html", {"party": party,  "title_search": title_search })    
            else:          
                return render(request, "party/index.html", {"party": party, })
        else:
            return render(request, "party/index.html", {"party": party, })       
        return render(request, "party/index.html", {"party": party,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_create(request):
    try:
        if request.method == "POST":
            party = Party()
            party.party_title = request.POST.get("party_title")
            partyform = PartyForm(request.POST)
            if partyform.is_valid():
                party.save()
                return HttpResponseRedirect(reverse('party_index'))
            else:
                return render(request, "party/create.html", {"form": partyform})
        else:        
            partyform = PartyForm()
            return render(request, "party/create.html", {"form": partyform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_edit(request, id):
    try:
        party = Party.objects.get(id=id)
        if request.method == "POST":
            party.party_title = request.POST.get("party_title")
            partyform = PartyForm(request.POST)
            if partyform.is_valid():
                party.save()
                return HttpResponseRedirect(reverse('party_index'))
            else:
                return render(request, "party/edit.html", {"form": partyform})
        else:
            # Загрузка начальных данных
            partyform = PartyForm(initial={'party_title': party.party_title, })
            return render(request, "party/edit.html", {"form": partyform})
    except Party.DoesNotExist:
        return HttpResponseNotFound("<h2>Party not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_delete(request, id):
    try:
        party = Party.objects.get(id=id)
        party.delete()
        return HttpResponseRedirect(reverse('party_index'))
    except Party.DoesNotExist:
        return HttpResponseNotFound("<h2>Party not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_read(request, id):
    try:
        party = Party.objects.get(id=id) 
        return render(request, "party/read.html", {"party": party})
    except Party.DoesNotExist:
        return HttpResponseNotFound("<h2>Party not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_members_index(request):
    try:
        party_members = PartyMembers.objects.all().order_by('party__party_title', 'client__full_name')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    party_query = Party.objects.filter(party_title__contains = title_search).only('id').all()
                    client_query = Client.objects.filter(full_name__contains = title_search).only('id').all()
                    party_members = party_members.filter(Q(party_id__in = party_query)|Q(client_id__in = client_query))
                return render(request, "party_members/index.html", {"party_members": party_members,  "title_search": title_search })    
            else:          
                return render(request, "party_members/index.html", {"party_members": party_members, })
        else:
            return render(request, "party_members/index.html", {"party_members": party_members, })       
        return render(request, "party_members/index.html", {"party_members": party_members,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_members_create(request):
    try:
        if request.method == "POST":
            party_members = PartyMembers()
            party_members.party = Party.objects.filter(id=request.POST.get("party")).first()
            party_members.client = Client.objects.filter(id=request.POST.get("client")).first()
            party_membersform = PartyMembersForm(request.POST)
            if party_membersform.is_valid():
                party_members.save()
                return HttpResponseRedirect(reverse('party_members_index'))
            else:
                return render(request, "party_members/create.html", {"form": party_membersform})
        else:        
            party_membersform = PartyMembersForm()
            return render(request, "party_members/create.html", {"form": party_membersform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_members_edit(request, id):
    try:
        party_members = PartyMembers.objects.get(id=id)
        if request.method == "POST":
            party_members.party = Party.objects.filter(id=request.POST.get("party")).first()
            party_members.client = Client.objects.filter(id=request.POST.get("client")).first()            
            party_membersform = PartyMembersForm(request.POST)
            if party_membersform.is_valid():
                party_members.save()
                return HttpResponseRedirect(reverse('party_members_index'))
            else:
                return render(request, "party_members/edit.html", {"form": party_membersform})
        else:
            # Загрузка начальных данных
            party_membersform = PartyMembersForm(initial={'party': party_members.party, 'client': party_members.client, })
            return render(request, "party_members/edit.html", {"form": party_membersform})
    except PartyMembers.DoesNotExist:
        return HttpResponseNotFound("<h2>PartyMembers not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_members_delete(request, id):
    try:
        party_members = PartyMembers.objects.get(id=id)
        party_members.delete()
        return HttpResponseRedirect(reverse('party_members_index'))
    except PartyMembers.DoesNotExist:
        return HttpResponseNotFound("<h2>PartyMembers not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def party_members_read(request, id):
    try:
        party_members = PartyMembers.objects.get(id=id) 
        return render(request, "party_members/read.html", {"party_members": party_members})
    except PartyMembers.DoesNotExist:
        return HttpResponseNotFound("<h2>PartyMembers not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_index(request):
    try:
        kind = Kind.objects.all().order_by('kind_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    kind = kind.filter(kind_title__contains = title_search)                
                return render(request, "kind/index.html", {"kind": kind,  "title_search": title_search })    
            else:          
                return render(request, "kind/index.html", {"kind": kind, })
        else:
            return render(request, "kind/index.html", {"kind": kind, })       
        return render(request, "kind/index.html", {"kind": kind,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
def kind_list(request):
    try:
        kind = Kind.objects.all().order_by('kind_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    kind = kind.filter(kind_title__contains = title_search)                
                return render(request, "kind/list.html", {"kind": kind,  "title_search": title_search })    
            else:          
                return render(request, "kind/list.html", {"kind": kind, })
        else:
            return render(request, "kind/list.html", {"kind": kind, })       
        return render(request, "kind/list.html", {"kind": kind,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_create(request):
    try:
        if request.method == "POST":
            kind = Kind()
            kind.kind_title = request.POST.get("kind_title")
            kind.price = request.POST.get("price")
            kindform = KindForm(request.POST)
            if kindform.is_valid():
                kind.save()
                return HttpResponseRedirect(reverse('kind_index'))
            else:
                return render(request, "kind/create.html", {"form": kindform})
        else:        
            kindform = KindForm()
            return render(request, "kind/create.html", {"form": kindform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_edit(request, id):
    try:
        kind = Kind.objects.get(id=id)
        if request.method == "POST":
            kind.kind_title = request.POST.get("kind_title")
            kind.price = request.POST.get("price")
            kindform = KindForm(request.POST)
            if kindform.is_valid():
                kind.save()
                return HttpResponseRedirect(reverse('kind_index'))
            else:
                return render(request, "kind/edit.html", {"form": kindform})
        else:
            # Загрузка начальных данных
            kindform = KindForm(initial={'kind_title': kind.kind_title, 'price': kind.price, })
            return render(request, "kind/edit.html", {"form": kindform})
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_delete(request, id):
    try:
        kind = Kind.objects.get(id=id)
        kind.delete()
        return HttpResponseRedirect(reverse('kind_index'))
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def kind_read(request, id):
    try:
        kind = Kind.objects.get(id=id) 
        return render(request, "kind/read.html", {"kind": kind})
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def hall_index(request):
    try:
        hall = Hall.objects.all().order_by('hall_title')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    hall = hall.filter(hall_title__contains = title_search)                
                return render(request, "hall/index.html", {"hall": hall,  "title_search": title_search })    
            else:          
                return render(request, "hall/index.html", {"hall": hall, })
        else:
            return render(request, "hall/index.html", {"hall": hall, })       
        return render(request, "hall/index.html", {"hall": hall,})

    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def hall_create(request):
    try:
        if request.method == "POST":
            hall = Hall()
            hall.hall_title = request.POST.get("hall_title")
            hall.equipment = request.POST.get("equipment")
            hallform = HallForm(request.POST)
            if hallform.is_valid():
                hall.save()
                return HttpResponseRedirect(reverse('hall_index'))
            else:
                return render(request, "hall/create.html", {"form": hallform})
        else:        
            hallform = HallForm()
            return render(request, "hall/create.html", {"form": hallform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def hall_edit(request, id):
    try:
        hall = Hall.objects.get(id=id)
        if request.method == "POST":
            hall.hall_title = request.POST.get("hall_title")
            hall.equipment = request.POST.get("equipment")
            hallform = HallForm(request.POST)
            if hallform.is_valid():
                hall.save()
                return HttpResponseRedirect(reverse('hall_index'))
            else:
                return render(request, "hall/edit.html", {"form": hallform})
        else:
            # Загрузка начальных данных
            hallform = HallForm(initial={'hall_title': hall.hall_title, 'equipment': hall.equipment, })
            return render(request, "hall/edit.html", {"form": hallform})
    except Hall.DoesNotExist:
        return HttpResponseNotFound("<h2>Hall not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def hall_delete(request, id):
    try:
        hall = Hall.objects.get(id=id)
        hall.delete()
        return HttpResponseRedirect(reverse('hall_index'))
    except Hall.DoesNotExist:
        return HttpResponseNotFound("<h2>Hall not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def hall_read(request, id):
    try:
        hall = Hall.objects.get(id=id) 
        return render(request, "hall/read.html", {"hall": hall})
    except Hall.DoesNotExist:
        return HttpResponseNotFound("<h2>Hall not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_index(request):
    try:
        schedule = Schedule.objects.all().order_by('start_date')
        #if request.method == "POST":
        #    # Определить какая кнопка нажата
        #    if 'searchBtn' in request.POST:
        #        # Поиск по названию 
        #        title_search = request.POST.get("title_search")
        #        #print(title_search)                
        #        if title_search != '':
        #            doctor_query = Doctor.objects.filter(full_name__contains = title_search).only('id').all()
        #            schedule = schedule.filter(doctor_id__in = doctor_query)
        #        return render(request, "schedule/index.html", {"schedule": schedule,  "title_search": title_search })    
        #    else:          
        #        return render(request, "schedule/index.html", {"schedule": schedule, })
        #else:
        #    return render(request, "schedule/index.html", {"schedule": schedule, })       
        return render(request, "schedule/index.html", {"schedule": schedule,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
@login_required
def schedule_list(request):
    try:
        #print(request.user.id)
        # Расписание только для текущего пользователя
        #doctor = Doctor.objects.get(user_id=request.user.id)
        schedule = Schedule.objects.filter(doctor_id=doctor.id).order_by('start_date')
        return render(request, "schedule/list.html", {"schedule": schedule,})
    except Exception as exception:
        print(exception)
        return render(request, "schedule/list.html", {"schedule": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_create(request):
    try:
        if request.method == "POST":
            schedule = Schedule()
            schedule.start_date = request.POST.get("start_date")
            schedule.finish_date = request.POST.get("finish_date")
            schedule.hall = Hall.objects.filter(id=request.POST.get("hall")).first()
            schedule.kind = Kind.objects.filter(id=request.POST.get("kind")).first()
            schedule.party = Party.objects.filter(id=request.POST.get("party")).first()
            scheduleform = ScheduleForm(request.POST)
            if scheduleform.is_valid():
                schedule.save()
                return HttpResponseRedirect(reverse('schedule_index'))
            else:
                return render(request, "schedule/create.html", {"form": scheduleform})
        else:        
            scheduleform = ScheduleForm(initial={ 'start_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'finish_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            return render(request, "schedule/create.html", {"form": scheduleform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_edit(request, id):
    try:
        schedule = Schedule.objects.get(id=id)
        if request.method == "POST":
            schedule.start_date = request.POST.get("start_date")
            schedule.finish_date = request.POST.get("finish_date")
            schedule.hall = Hall.objects.filter(id=request.POST.get("hall")).first()
            schedule.kind = Kind.objects.filter(id=request.POST.get("kind")).first()
            schedule.party = Party.objects.filter(id=request.POST.get("party")).first()
            scheduleform = ScheduleForm(request.POST)
            if scheduleform.is_valid():
                schedule.save()
                return HttpResponseRedirect(reverse('schedule_index'))
            else:
                return render(request, "schedule/edit.html", {"form": scheduleform})
        else:
            # Загрузка начальных данных
            scheduleform = ScheduleForm(initial={'start_date': schedule.start_date.strftime('%Y-%m-%d %H:%M:%S'), 'finish_date': schedule.finish_date.strftime('%Y-%m-%d %H:%M:%S'), 'hall': schedule.hall, 'kind': schedule.kind, 'party': schedule.party, })
            return render(request, "schedule/edit.html", {"form": scheduleform})
    except Schedule.DoesNotExist:
        return HttpResponseNotFound("<h2>Schedule not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_delete(request, id):
    try:
        schedule = Schedule.objects.get(id=id)
        schedule.delete()
        return HttpResponseRedirect(reverse('schedule_index'))
    except Schedule.DoesNotExist:
        return HttpResponseNotFound("<h2>Schedule not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_read(request, id):
    try:
        schedule = Schedule.objects.get(id=id) 
        return render(request, "schedule/read.html", {"schedule": schedule})
    except Schedule.DoesNotExist:
        return HttpResponseNotFound("<h2>Schedule not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_instructor_index(request):
    try:
        schedule_instructor = ScheduleInstructor.objects.all().order_by('schedule__start_date')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                title_search = request.POST.get("title_search")
                #print(title_search)                
                if title_search != '':
                    party_query = Party.objects.filter(party_title__contains = title_search).only('id').all()
                    schedule_query = Schedule.objects.all().filter(party_id__in = party_query)
                    instructor_query = Instructor.objects.filter(full_name__contains = title_search).only('id').all()
                    schedule_instructor = schedule_instructor.filter(Q(schedule_id__in = schedule_query)|Q(instructor_id__in = instructor_query))
                return render(request, "schedule_instructor/index.html", {"schedule_instructor": schedule_instructor,  "title_search": title_search })    
            else:          
                return render(request, "schedule_instructor/index.html", {"schedule_instructor": schedule_instructor, })
        else:
            return render(request, "schedule_instructor/index.html", {"schedule_instructor": schedule_instructor, })       
        return render(request, "schedule_instructor/index.html", {"schedule_instructor": schedule_instructor,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
@login_required
def schedule_instructor_list(request):
    try:
        #print(request.user.id)
        # Расписание только для текущего пользователя
        #doctor = Doctor.objects.get(user_id=request.user.id)
        schedule_instructor = ScheduleInstructor.objects.filter(doctor_id=doctor.id).order_by('start_date')
        return render(request, "schedule_instructor/list.html", {"schedule_instructor": schedule_instructor,})
    except Exception as exception:
        print(exception)
        return render(request, "schedule_instructor/list.html", {"schedule_instructor": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_instructor_create(request):
    try:
        if request.method == "POST":
            schedule_instructor = ScheduleInstructor()
            schedule_instructor.schedule = Schedule.objects.filter(id=request.POST.get("schedule")).first()
            schedule_instructor.instructor = Instructor.objects.filter(id=request.POST.get("instructor")).first()
            schedule_instructorform = ScheduleInstructorForm(request.POST)
            if schedule_instructorform.is_valid():
                schedule_instructor.save()
                return HttpResponseRedirect(reverse('schedule_instructor_index'))
            else:
                return render(request, "schedule_instructor/create.html", {"form": schedule_instructorform})
        else:        
            schedule_instructorform = ScheduleInstructorForm()
            return render(request, "schedule_instructor/create.html", {"form": schedule_instructorform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_instructor_edit(request, id):
    try:
        schedule_instructor = ScheduleInstructor.objects.get(id=id)
        if request.method == "POST":
            schedule_instructor.schedule = Schedule.objects.filter(id=request.POST.get("schedule")).first()
            schedule_instructor.instructor = Instructor.objects.filter(id=request.POST.get("instructor")).first()
            schedule_instructorform = ScheduleInstructorForm(request.POST)
            if schedule_instructorform.is_valid():
                schedule_instructor.save()
                return HttpResponseRedirect(reverse('schedule_instructor_index'))
            else:
                return render(request, "schedule_instructor/edit.html", {"form": schedule_instructorform})
        else:
            # Загрузка начальных данных
            schedule_instructorform = ScheduleInstructorForm(initial={'schedule': schedule_instructor.schedule, 'instructor': schedule_instructor.instructor, })
            return render(request, "schedule_instructor/edit.html", {"form": schedule_instructorform})
    except ScheduleInstructor.DoesNotExist:
        return HttpResponseNotFound("<h2>ScheduleInstructor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_instructor_delete(request, id):
    try:
        schedule_instructor = ScheduleInstructor.objects.get(id=id)
        schedule_instructor.delete()
        return HttpResponseRedirect(reverse('schedule_instructor_index'))
    except ScheduleInstructor.DoesNotExist:
        return HttpResponseNotFound("<h2>ScheduleInstructor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def schedule_instructor_read(request, id):
    try:
        schedule_instructor = ScheduleInstructor.objects.get(id=id) 
        return render(request, "schedule_instructor/read.html", {"schedule_instructor": schedule_instructor})
    except ScheduleInstructor.DoesNotExist:
        return HttpResponseNotFound("<h2>ScheduleInstructor not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)
###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@user_passes_test(lambda u: u.is_superuser)
def payment_index(request):
    try:
        payment = Payment.objects.all().order_by('payment_date')
        return render(request, "payment/index.html", {"payment": payment, })
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)
    
# Список для просмотра
@login_required
def payment_list(request):
    try:
        payment = Payment.objects.all().order_by('payment_date')
        return render(request, "payment/list.html", {"payment": payment,})
    except Exception as exception:
        print(exception)
        return render(request, "payment/list.html", {"payment": None, "total": None,})
        #return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@user_passes_test(lambda u: u.is_superuser)
def payment_create(request):
    try:
        if request.method == "POST":
            payment = Payment()
            payment.payment_date = request.POST.get("payment_date")
            payment.party = Party.objects.filter(id=request.POST.get("party")).first()
            payment.client = Client.objects.filter(id=request.POST.get("client")).first()            
            payment.amount = request.POST.get("amount")
            paymentform = PaymentForm(request.POST)
            if paymentform.is_valid():
                payment.save()
                return HttpResponseRedirect(reverse('payment_index'))
            else:
                return render(request, "payment/create.html", {"form": paymentform})
        else:        
            paymentform = PaymentForm(initial={ 'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            return render(request, "payment/create.html", {"form": paymentform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def payment_edit(request, id):
    try:
        payment = Payment.objects.get(id=id)
        if request.method == "POST":
            payment.payment_date = request.POST.get("payment_date")
            payment.party = Party.objects.filter(id=request.POST.get("party")).first()
            payment.client = Client.objects.filter(id=request.POST.get("client")).first()            
            payment.amount = request.POST.get("amount")
            paymentform = PaymentForm(request.POST)
            if paymentform.is_valid():
                payment.save()
                return HttpResponseRedirect(reverse('payment_index'))
            else:
                return render(request, "payment/edit.html", {"form": paymentform})
        else:
            # Загрузка начальных данных
            paymentform = PaymentForm(initial={'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'), 'party': payment.party, 'client': payment.client, 'amount': payment.amount, })
            return render(request, "payment/edit.html", {"form": paymentform})
    except Payment.DoesNotExist:
        return HttpResponseNotFound("<h2>Payment not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def payment_delete(request, id):
    try:
        payment = Payment.objects.get(id=id)
        payment.delete()
        return HttpResponseRedirect(reverse('payment_index'))
    except Payment.DoesNotExist:
        return HttpResponseNotFound("<h2>Payment not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def payment_read(request, id):
    try:
        payment = Payment.objects.get(id=id) 
        return render(request, "payment/read.html", {"payment": payment})
    except Payment.DoesNotExist:
        return HttpResponseNotFound("<h2>Payment not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Регистрационная форма 
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
            #return render(request, 'registration/register_done.html', {'new_user': user})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# Изменение данных пользователя
@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'registration/my_account.html'
    success_url = reverse_lazy('index')
    #success_url = reverse_lazy('my_account')
    def get_object(self):
        return self.request.user

# Выход
from django.contrib.auth import logout
def logoutUser(request):
    logout(request)
    return render(request, "index.html")

