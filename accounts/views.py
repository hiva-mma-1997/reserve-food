from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Reservation ,FoodMenu ,Employees
from django.contrib.auth import logout
from django.utils import timezone
from datetime import time
from django.views.decorators.cache import never_cache
import jdatetime
from datetime import timedelta

@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user is not None:
            login(request, user)
            return redirect('reserve')
    return render(request, 'accounts/account_view.html')


@never_cache
@login_required
def reserve_view(request):
    persian_day={0:'شنبه' , 1:'یکشنبه' , 2:'دوشنبه' , 3:'سه‌شنبه' , 4:'چهارشنبه' , 5:'پنجشنبه'}
    today=jdatetime.date.today()
    dif=today.weekday()
    days_from_saturday=(dif-0)%7
    saturday=today-timedelta(days=days_from_saturday)
    next_saturday=saturday+timedelta(days=7)
    start_month=jdatetime.date(today.year,today.month,1)
    if today.month <= 6:
        last_day = 31
    elif today.month <= 11:
        last_day = 30
    else:
        last_day = 30 if jdatetime.date.isleap(today.year)else 29

    end_month = jdatetime.date(today.year, today.month, last_day)

    employee=Employees.objects.get(user=request.user)
    food_list=FoodMenu.objects.filter(location=employee.location,date__gte=saturday,date__lt=next_saturday+timedelta(days=7))
    reservations = Reservation.objects.filter(employee=employee,menu__date__gte=start_month,menu__date__lte=end_month).order_by('menu__date')
    for reserve in reservations:
        reserve.day_name = persian_day[reserve.menu.date.weekday()]
    for item in food_list:
        item.day_name = persian_day[item.date.weekday()]
    #Expiring time reserve
    now = timezone.localtime().time()
    reserve_time=time(10, 0)
    if now > reserve_time:
                message= 'مهلت رزرو امروز به پایان رسیده است.'
    else:
         message=''

    if request.method=='POST':
        for item in food_list:
            selected = request.POST.get(f'food_{item.id}')
            if selected:
                Reservation.objects.get_or_create(employee=employee,menu=item,defaults={'reserved_by':request.user})
    return render(
        request,
        'accounts/reserve_view.html',
        {'reservations': reservations ,'food_list': food_list,'employee':employee,'today':today, 'reserve_time':reserve_time , 'now': now ,'next_saturday':next_saturday , 'message':message,'persian_day':persian_day}
    )


@login_required
def delete_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, employee__user=request.user)
    reservation.delete()
    return redirect('reserve')


def logout_view(request):
    logout(request)
    return redirect('home')

@never_cache
@login_required
def my_reservations(request):
    employee = Employees.objects.get(user=request.user)
    reservations =Reservation.objects.filter(employee=employee).select_related('menu').order_by('menu__date')
    return render(request, 'accounts/my_reservations.html', {
        'reservations': reservations
    })