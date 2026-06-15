from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Reservation


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
            print("LOGIN SUCCESS")
            login(request, user)
            return redirect('reserve')
        else:
            print("LOGIN FAILED")

        if user is not None:
            login(request, user)
            return redirect('reserve')
        
    return render(request, 'accounts/account_view.html')

@login_required
def reserve_view(request):

    week_menu = [
    ('saturday','شنبه', 'زرشک پلو با مرغ'),
    ('sunday','یکشنبه', 'کوکو سیب زمینی'),
    ('monday','دوشنبه', 'قرمه سبزی'),
    ('thuesday','سشنبه', 'کباب کوبیده'),
    ('wednesday','چهارشنبه', 'جوجه کباب'),
    ('thursday','پنجشنبه', 'آبگوشت'),
    ]

    if request.method=='POST':
        """weekday=[('saturday_qty','saturday_location'),
                 ('sunday_qty','sunday_location'),
                 ('monday_qty','monday_location'),
                 ('thuesday_qty','thuesday_location'),
                 ('wednesday_qty','wednesday_location'),
                 ('thursday_qty','thursday_location')
                 ]"""
        
        i=0
        for day_qty,day_location in weekday:
            day_qty=request.POST.get(day_qty)
            day_location=request.POST.get(day_location)

            if int(day_qty)>0:
                Reservation.objects.update_or_create(
                    user=request.user,
                    day=week_menu[i][0],
                    defaults={'food':week_menu[i][1],
                        'quantity':day_qty,
                        'location':day_location},
                        )
            i+=1
        """saturday_qty=request.POST.get('saturday_qty')
        saturday_location=request.POST.get('saturday_location')

        sunday_qty=request.POST.get('sunday_qty')
        sunday_location=request.POST.get('sunday_location')

        monday_qty=request.POST.get('monday_qty')
        monday_location=request.POST.get('monday_location')"""


        """if int(day_qty)>0:
            Reservation.objects.update_or_create(
                user=request.user,
                day='شنبه',
                defaults={'food':'زرشک پلو با مرغ',
                    'quantity':saturday_qty,
                    'location':saturday_location},
                    
            )

        if int(sunday_qty)>0:
            Reservation.objects.update_or_create(
                user=request.user,
                day='یکشنبه',
                defaults={'food':'کوکو سیب زمینی',
                    'quantity':sunday_qty,
                    'location':sunday_location},
                    
            )
                
        if int(monday_qty)>0:
            Reservation.objects.update_or_create(
                user=request.user,
                day='دوشنبه',
                defaults={'food':'قرمه سبری',
                    'quantity':monday_qty,
                    'location':monday_location},
                    
            )"""

    
    reservations = Reservation.objects.filter(user=request.user)

    return render(
        request,
        'accounts/reserve_view.html',
        {'reservations': reservations}
    )
