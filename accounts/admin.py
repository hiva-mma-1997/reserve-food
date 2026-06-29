from django.contrib import admin
from accounts.models import Reservation,Employees,FoodMenu 
from django.urls import path
from django.db.models import Count
from django.shortcuts import render 
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from datetime import time


class ReservationInline(admin.TabularInline):
     model=Reservation
     extra=0

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('employee','menu','menu__date')
    list_filter = ('menu__location', 'menu__day')
    ordering = ('menu__location', 'menu__date',)

    change_list_template = "admin/reservation_changelist.html"
    
    def get_urls(self):
        urls = super().get_urls()
        report_urls=[
            path('report/<str:location>/',self.admin_site.admin_view(self.food_reporter),name='food_report'),
            path('clear',self.admin_site.admin_view(self.clear_reservation),name='clear_reservation'),
            path('not-reserved', self.admin_site.admin_view(self.not_reserved_users), name='not-reserved')
        ]
        return report_urls+urls
    
    def food_reporter(self, request, location):
        #days_order = ['شنبه','یکشنبه','دوشنبه','سشنبه','چهارشنبه','پنجشنبه','جمعه']
        report = Reservation.objects.filter(menu__location=location).values('menu__date','menu__location','menu__day').annotate(
            total_reserve=Count('id')).order_by('menu__date')
        return render(request,'admin/food_report.html', {'report': report, 'location':location})
    
    def not_reserved_users(self,request):
        current_employee=Employees.objects.get(user=request.user)
        location=current_employee.location
        employees=Employees.objects.filter(location=location)
        today=timezone.now().date()
        reserved_ids=Reservation.objects.filter(menu__date=today).values_list('employee_id',flat=True)
        not_reserved=employees.exclude(id__in=reserved_ids)

        if request.method=='POST':
            employee_ids=request.POST.getlist('employees')
            menu=FoodMenu.objects.get(location=location,date=today)
            
            for emp_id in employee_ids:
                employee=Employees.objects.get(id=emp_id)
                Reservation.objects.get_or_create(
                    employee=employee,menu=menu)
                
            return redirect(request.path)

        return render(request,'admin/not_reserved.html',{'not_reserved':not_reserved,'location':location})

    def clear_reservation(self,request):
        Reservation.objects.all().delete()
        messages.success(
        request,
        'رزروهای هفته با موفقیت پاک شدند.'
        )
        return redirect('../')


from openpyxl import Workbook
from django.http import HttpResponse
from accounts.models import Reservation
from io import BytesIO

@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display=('user','location')
    list_filter=('location',)
    search_fields=('user__username',)
    ordering=('location',)
    inlines=[ReservationInline]

    change_form_template='admin/employee_change_form.html'

    def get_urls(self):
        urls=super().get_urls()
        custom_urls=[path('<int:employee_id>/export-excel/',self.admin_site.admin_view(self.export_excel),name='employee_export_report'),
                     path('<int:employee_id>/export-pdf/',self.admin_site.admin_view(self.export_pdf),name='employee_export_pdf'),]
        return custom_urls+urls
    
    def export_excel(self,request,employee_id):
        wb=Workbook()
        ws=wb.active
        ws.title="Employee Reservations"
        ws.append(['name','food','date'])
        reservations_employee=Reservation.objects.select_related('employee','employee__user','menu').filter(employee_id=employee_id).order_by('reserve_date')
        for reserve in reservations_employee:
            ws.append([reserve.employee.user.username,reserve.menu.food,reserve.reserve_date])
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response=HttpResponse(output.read,content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition']=f'attachment;filename="reserve_employee_{employee_id}.xlsx"'
        
        return response
    
    def export_pdf(self):
         pass

from django.db.models import Case,When,IntegerField
from datetime import date, timedelta

@admin.register(FoodMenu)
class FoodMenuAdmin(admin.ModelAdmin):
    list_display=('food','location','day','date',)
    list_filter=('location','date',)
    ordering=('date',)

    change_list_template='admin/food_changelist.html'

    def get_urls(self):
        urls=super().get_urls()
        custom_urls=[path('weekly_menu/<str:location>',self.admin_site.admin_view(self.weekly_menu),
                          name='weekly_menu'),]
        return urls+custom_urls
    
    def weekly_menu(self,request,location):
        today=timezone.localdate()
        days_name=["شنبه" ,"یکشنبه" , "دوشنبه" , "سشنبه" , "چهارشنبه" ,"پنجشنبه" , "جمعه"]
        dif=today.weekday()
        days_from_saturday=(dif-5)%7
        saturday=today-timedelta(days=days_from_saturday)
        week_dates=[ saturday+timedelta(days=i) for i in range(7)]
        week_data=[{'id':i+1,'day':days_name[i],'date':week_dates[i] } for i in range(7)]

        if request.method=='POST':
            for item in week_data:
                food = request.POST.get(f"food_{item['date'].strftime('%Y-%m-%d')}")
                if food:
                    FoodMenu.objects.get_or_create(location=location,date=item['date'], 
                                                   defaults={'food':food, 'day':item['day']})
            return redirect(request.path)
        
        return render(request,'admin/weekly_menu.html',{'location':location,'week_data':week_data,
                                                        'today':today})