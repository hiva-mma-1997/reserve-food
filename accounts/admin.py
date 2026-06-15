from django.contrib import admin
from accounts.models import Reservation,Foodlist
from django.urls import path
from django.db.models import Count
from django.shortcuts import render 
from django.shortcuts import redirect
from django.contrib import messages



class FoodlistAdmin(admin.ModelAdmin):
    list_display=('food','day',)
    ordering=('id',)

class ReservationAdmin(admin.ModelAdmin):
    list_display=('user','food','day')
    list_filter=('food',)
    change_list_template = "admin/reservation_changelist.html"
    

    def get_urls(self):
        urls = super().get_urls()
        report_urls=[
            path('report',self.admin_site.admin_view(self.food_reporter),name='food_report'),
            path('clear',self.admin_site.admin_view(self.clear_reservation),name='clear_reservation')
        ]

        return report_urls+urls
    
    def food_reporter(self, request):
        days_order = ['شنبه', 'یکشنبه', 'دوشنبه', 'سشنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
        report = sorted(Reservation.objects.values('day', 'location').annotate(
        total_reserve=Count('id')),key=lambda x: days_order.index(x['day']))
        return render(request, 'admin/food_report.html', {'report': report})
    
    def clear_reservation(self,request):
        Reservation.objects.all().delete()
        messages.success(
        request,
        'رزروهای هفته با موفقیت پاک شدند.'
        )
        return redirect('../')
        

admin.site.register(Reservation,ReservationAdmin)
admin.site.register(Foodlist,FoodlistAdmin)
