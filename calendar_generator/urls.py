from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('success/<int:calendar_id>/', views.calendar_success, name='calendar_success'),
    path('download/<int:calendar_id>/', views.download_calendar, name='download_calendar'),
]
