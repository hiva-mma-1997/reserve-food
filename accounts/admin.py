from django.contrib import admin
from accounts.models import Reservation,Employees,FoodMenu 
from django.urls import path
from django.db.models import Count
from django.shortcuts import render 
from django.shortcuts import redirect
from django.contrib import messages




class ReservationInline(admin.TabularInline):
     model=Reservation
     extra=0

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('employee','menu','reserve_date')
    list_filter = ('menu__location', 'menu__day')
    ordering = ('menu__location', 'menu__day',)

    change_list_template = "admin/reservation_changelist.html"
    
    def get_urls(self):
        urls = super().get_urls()
        report_urls=[
            path('report/<str:location>/',self.admin_site.admin_view(self.food_reporter),name='food_report'),
            path('clear',self.admin_site.admin_view(self.clear_reservation),name='clear_reservation')
        ]
        return report_urls+urls
    
    def food_reporter(self, request, location):
            days_order = ['شنبه','یکشنبه','دوشنبه','سشنبه','چهارشنبه','پنجشنبه','جمعه']
            data = Reservation.objects.filter(menu__location=location).values('menu__day','menu__location').annotate(
                total_reserve=Count('id'))
            report = sorted(data, key=lambda x: days_order.index(x['menu__day']))
            return render(request,'admin/food_report.html', {'report': report, 'location':location})
    

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
@admin.register(FoodMenu)
class FoodMenuAdmin(admin.ModelAdmin):
    list_display=('food','location','day',)
    list_filter=('location','day',)
    ordering=('location',)
    




"""class UserInline(admin.TabularInline):
    model=User.groups.through
    extra=1
    verbose_name='Member'
    verbose_name_plural='Members'

admin.site.unregister(Group)

class CustomGroupAdmin(GroupAdmin):
    #list_display=('name','member_count')
    inlines=[UserInline]
    def member_count(self,obj):
        return obj.user_set.count()

admin.site.register(Group,CustomGroupAdmin)"""