from django.urls import path
from . import views



#app_name='accounts'

urlpatterns=[
    path('login',views.login_view,name='login'),
    path('reserve',views.reserve_view, name='reserve'),
    path('logout',views.logout_view,name='logout'),
    path('reservation/delete/<int:pk>/', views.delete_reservation, name='delete_reservation'),
    path('my_reservation',views.employee_report,name='my_reservations'),
    ]
