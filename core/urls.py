from django.urls import path
from . import views
from .views import authenticate_uid

urlpatterns = [
    path('submit/', views.submit_uid, name='submit_uid'),
    path('logs/', views.log_list, name='log_list'),
    path('authenticate/', authenticate_uid, name='authenticate_uid'),
]
