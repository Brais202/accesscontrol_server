from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_uid, name='submit_uid'),
    path('logs/', views.log_list, name='log_list'),
]
