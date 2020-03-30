from django.urls import path
from . import views

app_name ='shiftapp'

urlpatterns =[
    path('shift', views.makeshift, name='makeshift'),
    path('', views.yoshico, name='yoshico'),
]

