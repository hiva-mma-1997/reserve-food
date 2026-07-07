from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils import timezone
import django_jalali.db.models as jmodels
import jdatetime
from django.core.exceptions import ValidationError


class Employees(models.Model):
    LOCATION_CHOISES=[('sanat','صنعت'),('golchin','گلچین'),('mech','مکانیک')]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    location=models.CharField(max_length=20,choices=LOCATION_CHOISES)

    def __str__(self):
        return f'{self.user.username}'

class FoodMenu(models.Model):
    LOCATION_CHOISES=[('sanat','صنعت'),('golchin','گلچین'),('mech','مکانیک')]

    location=models.CharField(max_length=30 , choices=LOCATION_CHOISES)
    food=models.CharField(max_length=50)
    date=jmodels.jDateField(default=jdatetime.date.today)
    price=models.IntegerField(default=0)

    def __str__(self):
        return f'{self.food}'

class Reservation(models.Model):
    employee=models.ForeignKey(Employees,on_delete=models.CASCADE)
    menu=models.ForeignKey(FoodMenu,on_delete=models.CASCADE)
    #reserve_date=jmodels.jDateField(default=jdatetime.date.today)
    reserved_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return f'{self.employee.user.username}'
    
    def clean(self):
        if Reservation.objects.filter(employee=self.employee, menu__date=self.menu.date
                                      ).exclude(pk=self.pk).exists():
            raise ValidationError("این کارمند قبلاً برای این تاریخ رزرو ثبت کرده است.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
