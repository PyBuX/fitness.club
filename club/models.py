from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User

# Модели отображают информацию о данных, с которыми вы работаете.
# Они содержат поля и поведение ваших данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным

# choices (список выбора). Итератор (например, список или кортеж) 2-х элементных кортежей,
# определяющих варианты значений для поля.
# При определении, виджет формы использует select вместо стандартного текстового поля
# и ограничит значение поля указанными значениями.

# Читабельное имя поля (метка, label). Каждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
# первым аргументом принимает необязательное читабельное название.
# Если оно не указано, Django самостоятельно создаст его, используя название поля, заменяя подчеркивание на пробел.
# null - Если True, Django сохранит пустое значение как NULL в базе данных. По умолчанию - False.
# blank - Если True, поле не обязательно и может быть пустым. По умолчанию - False.
# Это не то же что и null. null относится к базе данных, blank - к проверке данных.
# Если поле содержит blank=True, форма позволит передать пустое значение.
# При blank=False - поле обязательно.

# Виды клубных карт
class Card(models.Model):
    card_title = models.CharField(_('card_title'), max_length=255, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'card'
        # Сортировка по умолчанию
        ordering = ['card_title']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}".format(self.card_title)

# Клиенты 
class Client(models.Model):
    SEX_CHOICES = (
        ('М','М'),
        ('Ж', 'Ж'),
    )    
    full_name = models.CharField(_('full_name'), max_length=128)
    birthday = models.DateTimeField(_('birthday'))
    sex = models.CharField(_('sex'), max_length=1, choices=SEX_CHOICES, default='М')
    phone = models.CharField(_('phone'), max_length=64)    
    card = models.ForeignKey(Card, related_name='client_card', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'client'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['full_name']),
        ]
        # Сортировка по умолчанию
        ordering = ['full_name']
    def __str__(self):
        # Вывод 
        return "{}, {}".format(self.full_name, self.birthday.strftime('%d.%m.%Y'))

# Инструкторы 
class Instructor(models.Model):
    SEX_CHOICES = (
        ('М','М'),
        ('Ж', 'Ж'),
    )    
    full_name = models.CharField(_('full_name'), max_length=128)
    sex = models.CharField(_('sex'), max_length=1, choices=SEX_CHOICES, default='М')
    phone = models.CharField(_('phone'), max_length=64)    
    user = models.OneToOneField(User, related_name='instructor_user', on_delete=models.PROTECT) 
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'instructor'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['full_name']),
        ]
        # Сортировка по умолчанию
        ordering = ['full_name']
    def __str__(self):
        # Вывод 
        return "{}, {}".format(self.full_name, self.birthday.strftime('%d.%m.%Y'))

# Группа 
class Party(models.Model):
    party_title = models.CharField(_('party_title'), max_length=96, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'party'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['party_title']),
        ]
        # Сортировка по умолчанию
        ordering = ['party_title']
    def __str__(self):
        # Вывод 
        return "{}".format(self.party_title)

# Состав группы
class PartyMembers(models.Model):
    party = models.ForeignKey(Party, related_name='party_members_party', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='party_members_client', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'party_members'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['party']),
            models.Index(fields=['client']),
        ]
        # Сортировка по умолчанию
        ordering = ['party']
    def __str__(self):
        # Вывод 
        return "{}: {}".format(self.party, self.client)

# Виды занятий/предоставляемых услуг
class Kind(models.Model):
    kind_title = models.CharField(_('kind_title'), max_length=128, unique=True)
    price = models.DecimalField(_('kind_price'), max_digits=9, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'kind'
        # Сортировка по умолчанию
        ordering = ['kind_title']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}".format(self.kind_title)

# Названия залов
class Hall(models.Model):
    hall_title = models.CharField(_('hall_title'), max_length=128, unique=True)
    equipment = models.TextField(_('equipment'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'hall'
        # Сортировка по умолчанию
        ordering = ['hall_title']
    def __str__(self):
        # Вывод удобочитаемой строки
        return "{}".format(self.hall_title)

# Расписание занятий
class Schedule(models.Model):
    start_date = models.DateTimeField(_('start_date'))
    finish_date = models.DateTimeField(_('finish_date'))
    hall = models.ForeignKey(Hall, related_name='schedule_hall', on_delete=models.CASCADE)
    kind = models.ForeignKey(Kind, related_name='schedule_kind', on_delete=models.CASCADE)
    party = models.ForeignKey(Party, related_name='schedule_party', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'schedule'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['start_date', 'finish_date']),
        ]
        # Сортировка по умолчанию
        ordering = ['start_date', 'finish_date']
    def __str__(self):
        # Вывод удобочитаемой строки 
        return "{}: {}, {}".format(self.date_schedule.strftime('%d.%m.%Y HH:mm'), self.kind, self.party)

# Инструкторы на занятие
class ScheduleInstructor(models.Model):
    schedule = models.ForeignKey(Schedule, related_name='schedule_instructor_schedule', on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, related_name='schedule_instructor_instructor', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'schedule_instructor'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['schedule', 'instructor']),
        ]
        # Сортировка по умолчанию
        ordering = ['schedule']
    def __str__(self):
        # Вывод удобочитаемой строки 
        return "{}: {}".format(self.schedule, self.instructor)
    
# Оплата
class Payment(models.Model):
    payment_date = models.DateTimeField(_('payment_date'))
    party = models.ForeignKey(Party, related_name='payment_party', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='payment_client', on_delete=models.CASCADE)
    amount = models.DecimalField(_('payment_amount'), max_digits=9, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'payment'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['party']),
            models.Index(fields=['client']),
        ]
        # Сортировка по умолчанию
        ordering = ['payment_date']
    def __str__(self):
        # Вывод в тег SELECT 
        return "{}: {} {}".format(self.payment_date.strftime('%d.%m.%Y HH:mm'), self.client, self.price)
