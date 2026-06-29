from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils import timezone


class Employees(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    location=models.CharField(max_length=20)

    def __str__(self):
        return f'{self.user.username}'

class FoodMenu(models.Model):
    location=models.CharField(max_length=30)
    day=models.CharField(max_length=20)
    food=models.CharField(max_length=50)
    date=models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.location} - {self.day}'

class Reservation(models.Model):
    employee=models.ForeignKey(Employees,on_delete=models.CASCADE)
    menu=models.ForeignKey(FoodMenu,on_delete=models.CASCADE)
    reserve_date=models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.employee.user.username}'
