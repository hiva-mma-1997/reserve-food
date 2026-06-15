from django.urls import path
from . import views
from .views import ReservationAPI , ReservationCreateAPI

urlpatterns=[
    path('login/',views.login_view,name='login'),
    path('reserve/',views.reserve_view, name='reserve'),
    path('logout/',views.logout_view,name='logout'),
    path('api/reservations/',ReservationAPI.as_view()),
    path('api/reservation/create/',ReservationCreateAPI.as_view()),
    path('reservation/delete/<int:pk>/', views.delete_reservation, name='delete_reservation'),
    ]
