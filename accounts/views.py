from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Reservation ,FoodMenu ,Employees
from django.contrib.auth import logout
from django.utils import timezone
from datetime import time
from django.views.decorators.cache import never_cache

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
    employee=Employees.objects.get(user=request.user)
    food_list=FoodMenu.objects.filter(location=employee.location)
    #Expiring time reserve
    today=timezone.localdate()
    now = timezone.localtime().time()
    reservations = Reservation.objects.filter(employee=employee)
    if now > time(18, 0):
        return render(
            request,
            'accounts/reserve_view.html',
            {   'reservations':reservations,
                'food_list': food_list,
                'location':employee.location,
                'message': 'مهلت رزرو به پایان رسیده است.'
            }
        )
    employee = Employees.objects.get(user=request.user)
    if request.method=='POST':
        for item in food_list:
            selected = request.POST.get(f'food_{item.id}')
            if selected:
                Reservation.objects.get_or_create(employee=employee,menu=item,defaults={'reserved_by':request.user})
        reservations = Reservation.objects.filter(employee=employee) 
    return render(
        request,
        'accounts/reserve_view.html',
        {'reservations': reservations ,'food_list': food_list,'location':employee.location,'today':today}
    )


@login_required
def delete_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, employee__user=request.user)
    reservation.delete()
    return redirect('reserve')


def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def employee_report(request):
    employee = Employees.objects.get(user=request.user)
    reservations =Reservation.objects.filter(employee=employee).select_related('menu').order_by('-menu__date')
    return render(request, 'accounts/my_reservations.html', {
        'reservations': reservations
    })