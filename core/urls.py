from django.urls import path
from . import views
from .views import authenticate_uid, get_appkey2

urlpatterns = [
    path('submit/', views.submit_uid, name='submit_uid'),
    path('logs/', views.log_list, name='log_list'),
    path('authenticate/', authenticate_uid, name='authenticate_uid'),
    path('get_appkey2/', get_appkey2, name='get_appkey2'),
]
