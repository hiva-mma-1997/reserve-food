from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils import timezone
import django_jalali.db.models as jmodels


class Employees(models.Model):
    LOCATION_CHOISES=[('sanat','صنعت'),('golchin','گلچین'),('mech','مکانیک')]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    location=models.CharField(max_length=20,choices=LOCATION_CHOISES)

    def __str__(self):
        return f'{self.user.username}'

class FoodMenu(models.Model):
    DAY_CHOICES=[(5,'شنبه'),(6,'یکشنبه'),(0,'دوشنبه'),(1,'سه‌شنبه'),(2,'چهارشنبه'),(3,'پنجشنبه')]
    LOCATION_CHOISES=[('sanat','صنعت'),('golchin','گلچین'),('mech','مکانیک')]

    location=models.CharField(max_length=30 , choices=LOCATION_CHOISES)
    day=models.CharField(max_length=20,choices=DAY_CHOICES)
    food=models.CharField(max_length=50)
    date=jmodels.jDateField(default=timezone.now)
    price=models.IntegerField(default=0)

    def __str__(self):
        return f'{self.location} - {self.day}'

class Reservation(models.Model):
    employee=models.ForeignKey(Employees,on_delete=models.CASCADE)
    menu=models.ForeignKey(FoodMenu,on_delete=models.CASCADE)
    reserve_date=models.DateField(default=timezone.now)
    reserved_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return f'{self.employee.user.username}'
