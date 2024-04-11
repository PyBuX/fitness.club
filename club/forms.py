from django import forms
from django.forms import ModelForm, TextInput, Textarea, DateInput, NumberInput, DateTimeInput, CheckboxInput
from .models import Card, Client, Instructor, Party, PartyMembers, Kind, Hall, Schedule, ScheduleInstructor, Payment
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# При разработке приложения, использующего базу данных, чаще всего необходимо работать с формами, которые аналогичны моделям.
# В этом случае явное определение полей формы будет дублировать код, так как все поля уже описаны в модели.
# По этой причине Django предоставляет вспомогательный класс, который позволит вам создать класс Form по имеющейся модели
# атрибут fields - указание списка используемых полей, при fields = '__all__' - все поля
# атрибут widgets для указания собственный виджет для поля. Его значением должен быть словарь, ключами которого являются имена полей, а значениями — классы или экземпляры виджетов.

# Виды клубных карт
class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['card_title',]
        widgets = {
            'card_title': TextInput(attrs={"size":"100"}),            
        }

# Клиенты
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('full_name', 'birthday', 'sex', 'phone', 'card')
        widgets = {
            'full_name': TextInput(attrs={"size":"100"}),
            'birthday': DateInput(attrs={"type":"date"}),
            'address': TextInput(attrs={"size":"100"}),            
            'phone': TextInput(attrs={"size":"40", "type":"tel", "pattern": "+7-[0-9]{3}-[0-9]{3}-[0-9]{4}"}),  
            'card': forms.Select(),
        }
        labels = {
            'card': _('card_title'),            
        }
    # Метод-валидатор для поля birthday
    def clean_birthday(self):        
        if isinstance(self.cleaned_data['birthday'], datetime.date) == True:
            data = self.cleaned_data['birthday']
            # Проверка даты рождения не моложе 16 лет
            if data > timezone.now() - relativedelta(years=16):
                raise forms.ValidationError(_('Minimum age 16 years old'))
        else:
            raise forms.ValidationError(_('Wrong date and time format'))
        # Метод-валидатор обязательно должен вернуть очищенные данные, даже если не изменил их
        return data   

# Инструкторы
class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ('full_name', 'sex', 'phone', 'user')
        widgets = {
            'full_name': TextInput(attrs={"size":"100"}),
            'phone': TextInput(attrs={"size":"40", "type":"tel", "pattern": "+7-[0-9]{3}-[0-9]{3}-[0-9]{4}"}),  
            'user': forms.Select(),            
        }
        labels = {
            'user': _('user'),            
        }

# Группа
class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('party_title',)
        widgets = {
            'party_title': TextInput(attrs={"size":"100"}),
        }

# Состав группы
class PartyMembersForm(forms.ModelForm):
    class Meta:
        model = PartyMembers
        fields = ['party', 'client',]
        widgets = {
            'party': forms.Select(),            
            'client': forms.Select(),            
        }
        labels = {
            'party': _('party'),            
            'client': _('client'),            
        }

# Виды занятий/предоставляемых услуг
class KindForm(forms.ModelForm):
    class Meta:
        model = Kind
        fields = ['kind_title', 'price',]
        widgets = {
            'kind_title': TextInput(attrs={"size":"100"}),  
            'price': NumberInput(attrs={"size":"10", "min": "1", "step": "1"}),            
        }

# Названия залов
class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ['hall_title', 'equipment']
        widgets = {
            'hall_title': TextInput(attrs={"size":"100"}),  
            'equipment': Textarea(attrs={'cols': 100, 'rows': 8}),           
        }

# Расписание занятий
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('start_date', 'finish_date', 'hall', 'kind', 'party')
        widgets = {
            'start_date': DateTimeInput(format='%d/%m/%Y %H:%M:%S'),
            'finish_date': DateTimeInput(format='%d/%m/%Y %H:%M:%S'),
            'hall': forms.Select(),
            'kind': forms.Select(),
            'party': forms.Select(),
        }
        labels = {
            'hall': _('hall'),            
            'kind': _('kind'),            
            'party': _('party'),            
        }

# Инструкторы на занятие
class ScheduleInstructorForm(forms.ModelForm):
    class Meta:
        model = ScheduleInstructor
        fields = ('schedule', 'instructor')
        widgets = {
            'schedule': forms.Select(),            
            'instructor': forms.Select(),            
        }
        labels = {
            'schedule': _('schedule'),            
            'instructor': _('instructor'),            
        }

# Продажа услуг
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('payment_date', 'party', 'client', 'amount')
        widgets = {
            'payment_date': DateTimeInput(format='%d/%m/%Y %H:%M:%S'),
            'party': forms.Select(),
            'client': forms.Select(),
            'amount': NumberInput(attrs={"size":"10", "min": "1", "step": "1"}),
        }
        labels = {
            'party': _('party'),                        
            'client': _('client'),                        
        }

# Форма регистрации
class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
