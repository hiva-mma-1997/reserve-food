from django.db import models
from django.contrib.auth.models import User

class Reservation(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    day=models.CharField(max_length=30)
    food=models.CharField(max_length=40)
    quantity=models.IntegerField()
    location=models.CharField(max_length=40)

    def __str__(self):
        return f'{self.user}'

class Foodlist(models.Model):
    food=models.CharField(max_length=30)
    day=models.CharField(max_length=20)
    reservedate=models.DateField()

    def __str__(self):
        return f'{self.day}'