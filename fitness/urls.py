"""
URL configuration for medicine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings 
from django.conf.urls import include
from django.conf.urls.static import static 


from club import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index),
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
        
    path('card/index/', views.card_index, name='card_index'),
    path('card/create/', views.card_create, name='card_create'),
    path('card/edit/<int:id>/', views.card_edit, name='card_edit'),
    path('card/delete/<int:id>/', views.card_delete, name='card_delete'),
    path('card/read/<int:id>/', views.card_read, name='card_read'),

    path('client/index/', views.client_index, name='client_index'),
    path('client/list/', views.client_list, name='client_list'),
    path('client/create/', views.client_create, name='client_create'),
    path('client/edit/<int:id>/', views.client_edit, name='client_edit'),
    path('client/delete/<int:id>/', views.client_delete, name='client_delete'),
    path('client/read/<int:id>/', views.client_read, name='client_read'),

    path('instructor/index/', views.instructor_index, name='instructor_index'),
    path('instructor/list/', views.instructor_list, name='instructor_list'),
    path('instructor/create/', views.instructor_create, name='instructor_create'),
    path('instructor/edit/<int:id>/', views.instructor_edit, name='instructor_edit'),
    path('instructor/delete/<int:id>/', views.instructor_delete, name='instructor_delete'),
    path('instructor/read/<int:id>/', views.instructor_read, name='instructor_read'),
    
    path('party/index/', views.party_index, name='party_index'),
    path('party/create/', views.party_create, name='party_create'),
    path('party/edit/<int:id>/', views.party_edit, name='party_edit'),
    path('party/delete/<int:id>/', views.party_delete, name='party_delete'),
    path('party/read/<int:id>/', views.party_read, name='party_read'),

    path('party_members/index/', views.party_members_index, name='party_members_index'),
    path('party_members/create/', views.party_members_create, name='party_members_create'),
    path('party_members/edit/<int:id>/', views.party_members_edit, name='party_members_edit'),
    path('party_members/delete/<int:id>/', views.party_members_delete, name='party_members_delete'),
    path('party_members/read/<int:id>/', views.party_members_read, name='party_members_read'),

    path('kind/index/', views.kind_index, name='kind_index'),
    path('kind/list/', views.kind_list, name='kind_list'),
    path('kind/create/', views.kind_create, name='kind_create'),
    path('kind/edit/<int:id>/', views.kind_edit, name='kind_edit'),
    path('kind/delete/<int:id>/', views.kind_delete, name='kind_delete'),
    path('kind/read/<int:id>/', views.kind_read, name='kind_read'),

    path('hall/index/', views.hall_index, name='hall_index'),
    path('hall/create/', views.hall_create, name='hall_create'),
    path('hall/edit/<int:id>/', views.hall_edit, name='hall_edit'),
    path('hall/delete/<int:id>/', views.hall_delete, name='hall_delete'),
    path('hall/read/<int:id>/', views.hall_read, name='hall_read'),
    
    path('schedule/index/', views.schedule_index, name='schedule_index'),
    path('schedule/list/', views.schedule_list, name='schedule_list'),
    path('schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/edit/<int:id>/', views.schedule_edit, name='schedule_edit'),
    path('schedule/delete/<int:id>/', views.schedule_delete, name='schedule_delete'),
    path('schedule/read/<int:id>/', views.schedule_read, name='schedule_read'),

    path('schedule_instructor/index/', views.schedule_instructor_index, name='schedule_instructor_index'),
    path('schedule_instructor/create/', views.schedule_instructor_create, name='schedule_instructor_create'),
    path('schedule_instructor/edit/<int:id>/', views.schedule_instructor_edit, name='schedule_instructor_edit'),
    path('schedule_instructor/delete/<int:id>/', views.schedule_instructor_delete, name='schedule_instructor_delete'),
    path('schedule_instructor/read/<int:id>/', views.schedule_instructor_read, name='schedule_instructor_read'),

    path('payment/index/', views.payment_index, name='payment_index'),
    path('payment/list/', views.payment_list, name='payment_list'),
    path('payment/create/', views.payment_create, name='payment_create'),
    path('payment/edit/<int:id>/', views.payment_edit, name='payment_edit'),
    path('payment/delete/<int:id>/', views.payment_delete, name='payment_delete'),
    path('payment/read/<int:id>/', views.payment_read, name='payment_read'),

    path('report/report_1/', views.report_1, name='report_1'),
    path('report/report_2/', views.report_2, name='report_2'),
    path('report/report_3/', views.report_3, name='report_3'),

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', views.logoutUser, name="logout"),
    path('settings/account/', views.UserUpdateView.as_view(), name='my_account'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
