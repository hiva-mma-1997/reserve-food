from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Reservation , Foodlist
from django.contrib.auth import logout

from rest_framework import generics,permissions
from .serializers import ReservationSerializer

class ReservationAPI(generics.ListAPIView):
    serializer_class=ReservationSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

class ReservationCreateAPI(generics.CreateAPIView):
    serializer_class=ReservationSerializer
    permission_classes=[permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

@login_required
def reserve_view(request):
    food_list = Foodlist.objects.all()
     

    if request.method=='POST':

        for item in food_list:
            qty=request.POST.get(f'qty_{item.id}')
            location=request.POST.get(f'location_{item.id}')

            if qty and qty.isdigit() and int(qty)>0:
                Reservation.objects.update_or_create(
                    user=request.user,
                    day=item.day,
                    defaults={'food':item.food,
                        'quantity':int(qty),
                        'location':location},
                        )

    reservations = Reservation.objects.filter(user=request.user)
    print(reservations) 
    res_dict = {(r.day, r.food): r for r in reservations}
    print(res_dict)
    
        
    return render(
        request,
        'accounts/reserve_view.html',
        {'reservations': reservations ,'food_list': food_list}
    )

@login_required
def delete_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    reservation.delete()
    return redirect('reserve')

def logout_view(request):
    logout(request)
    return redirect('login')