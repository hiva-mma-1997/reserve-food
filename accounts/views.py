from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        print("username =", username)
        print("password =", password)

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
    return render(request,'accounts/reserve_view.html')