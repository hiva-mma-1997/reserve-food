from django.urls import path
from . import views

urlpatterns=[
    path('login/',views.login_view),
    path('reserve/',views.reserve_view, name='reserve')
]