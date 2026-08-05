from django.contrib import admin
from accounts.models import Reservation,Employees,FoodMenu 
from django.urls import path , reverse
from django.db.models import Count
from django.shortcuts import render 
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from rangefilter.filters import DateRangeFilter
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from jalali_date.admin import ModelAdminJalaliMixin
import jdatetime
from datetime import time
from .forms import ExportExcelForm
from openpyxl import Workbook
from django.http import HttpResponse
from accounts.models import Reservation
from io import BytesIO
from django.http import JsonResponse
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Table, TableStyle
import arabic_reshaper
from bidi.algorithm import get_display

class ReservationInline(ModelAdminJalaliMixin,admin.TabularInline):
     model=Reservation
     extra=0

     def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "menu":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                employee = Employees.objects.get(pk=object_id)
                field.queryset = FoodMenu.objects.filter(location=employee.location,).order_by("date")

        return field

@admin.register(Reservation)
class ReservationAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):

    list_display = ('employee','menu__date','menu__food','reserved_by',)
    list_per_page=50
    list_filter=(('menu__date',DateRangeFilter),'menu__location',)
    ordering = ('menu__location', 'menu__date',)

    change_list_template = "admin/reservation_changelist.html"
    
    def get_urls(self):
        urls = super().get_urls()
        report_urls=[
            path('report/<str:location>/',self.admin_site.admin_view(self.food_reporter),name='food_report'),
            path('not-reserved', self.admin_site.admin_view(self.not_reserved_users), name='not-reserved'),
            path("get-menu/",self.admin_site.admin_view(self.get_menu),name="reservation-get-menu",),
        ]
        return report_urls+urls
    
    def food_reporter(self, request, location):
        persian_day=["شنبه" ,"یکشنبه" , "دوشنبه" , "سه‌شنبه" , "چهارشنبه" ,"پنجشنبه"]
        display_location=dict(Employees.LOCATION_CHOISES).get(location,location)
        today=jdatetime.date.today()
        dif=today.weekday()
        days_from_saturday=(dif-0)%7
        saturday=today-timedelta(days=days_from_saturday)
        if request.user.groups.filter(name__in=['Managers', 'Restaurant Coordinator', 'Office Admin']).exists():
            report = Reservation.objects.filter(menu__location=location ,menu__date__gte=saturday,menu__date__lt=saturday+timedelta(days=6)).values('menu__date','menu__location').annotate(
                total_reserve=Count('id')).order_by('menu__date')
            for reserve in report:
                reserve['day_name']= persian_day[reserve['menu__date'].weekday()]
            return render(request,'admin/food_report.html', {'report': report, 'location':display_location})
        else:
            messages.error(request,'شما به این صفحه دسترسی ندارید')
            return redirect('admin/accounts/foodmenu/')
    
    def not_reserved_users(self,request):
        current_employee=Employees.objects.get(user=request.user)
        location=current_employee.location
        employees=Employees.objects.filter(location=location)
        today=jdatetime.date.today()
        reserved_ids=Reservation.objects.filter(menu__date=today).values_list('employee_id',flat=True)
        admin_reserve_time=time(10,30)
        now=timezone.localtime().time()
        if request.user.groups.filter(name__in=['Managers',]).exists():
            not_reserved=Employees.objects.exclude(id__in=reserved_ids).order_by('location')
        else:
            not_reserved=employees.exclude(id__in=reserved_ids).order_by('user_id')

        if request.method=='POST':
            employee_ids=request.POST.getlist('employees')
            menu=FoodMenu.objects.get(location=location,date=today)
            for emp_id in employee_ids:
                employee=Employees.objects.get(id=emp_id)
                Reservation.objects.get_or_create(
                    employee=employee,menu=menu,defaults={'reserved_by':request.user}) 
            return redirect(request.path)
        return render(request,'admin/not_reserved.html',{'not_reserved':not_reserved,
                                                         'location':location,'admin_reserve_time':admin_reserve_time,'now':now,})

    def get_menu(self, request):
        employee_id = request.GET.get("employee")
        employee = Employees.objects.get(pk=employee_id)
        if not employee:
            return JsonResponse([], safe=False)
        today=jdatetime.date.today()
        first_day=jdatetime.date(today.year,today.month,1)
        if today.month == 12:
            next_month = jdatetime.date(today.year + 1, 1, 1)
        else:
            next_month = jdatetime.date(today.year, today.month + 1, 1)
        menus = FoodMenu.objects.filter(location=employee.location,date__gte=first_day,
                                        date__lt=next_month,).order_by("date")
        data = [{"id": menu.id,"text": f"{str(menu.date.strftime('%Y-%m-%d'))} - {menu.food}",}for menu in menus]
        
        return JsonResponse(data, safe=False)
    
    class Media:
        js = ("admin/js/reservation.js",)

@admin.register(Employees)
class EmployeesAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    list_display=('user','location')
    list_filter=('location',)
    search_fields=('user__username',)
    ordering=('location',)

    change_form_template='admin/employee_change_form.html'

    def get_urls(self):
        urls=super().get_urls()
        custom_urls=[path('<int:employee_id>/export-excel/',self.admin_site.admin_view(self.export_excel),name='employee_export_report'),
                     path('<int:employee_id>/export-files/',self.admin_site.admin_view(self.reserve_per_date),name='export_files'),]
        return custom_urls+urls
    def reserve_per_date(self, request, employee_id):
        form = ExportExcelForm(request.GET or None)
        employee=Employees.objects.get(pk=employee_id)
        return render(request,"admin/export_files.html",{"form": form,"employee_id": employee_id,'employee':employee})
        
    def export_excel(self,request,employee_id):
        pdfmetrics.registerFont(TTFont("Vazir", "static/fonts/Vazir.ttf"))
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        reservations_employee=Reservation.objects.select_related('employee','employee__user','menu','reserved_by').filter(employee_id=employee_id).order_by('menu__date')
        if from_date:
            reservations_employee = reservations_employee.filter(menu__date__gte=from_date)
        if to_date:
            reservations_employee = reservations_employee.filter(menu__date__lte=to_date)
        Total=reservations_employee.count()
        if request.GET.get('type')=='excel':
            wb=Workbook()
            ws=wb.active
            ws.title="Employee Reservations"
            ws.append(['Name','Food','Date','Reserved_by'])
            for reserve in reservations_employee:
                ws.append([reserve.employee.user.username,reserve.menu.food,reserve.menu.date.strftime("%Y/%m/%d"),reserve.reserved_by.username if reserve.reserved_by else "-"])
            ws.append(['Total', Total])
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            response=HttpResponse(output.read(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition']=f'attachment;filename="reserve_employee_{employee_id}.xlsx"'
            return response
        if request.GET.get('type')=='pdf':
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            data = []
            data.append([get_display(arabic_reshaper.reshape("ثبت کننده")),get_display(arabic_reshaper.reshape("تاریخ")),
            get_display(arabic_reshaper.reshape("غذا")),get_display(arabic_reshaper.reshape("نام")),])
            for reserve in reservations_employee:
                data.append([get_display(arabic_reshaper.reshape(reserve.reserved_by.username if reserve.reserved_by else "-")),
            reserve.menu.date.strftime("%Y/%m/%d"),get_display(arabic_reshaper.reshape(reserve.menu.food)),
            get_display(arabic_reshaper.reshape(reserve.employee.user.username)),])

            data.append(["","",get_display(arabic_reshaper.reshape("جمع کل")),str(reservations_employee.count()),])
            table = Table(data)
            table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 1, colors.black),
                                       ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                                       ("FONTNAME", (0, 0), (-1, -1), "Vazir"),
                                       ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                       ("BOTTOMPADDING", (0, 0), (-1, 0), 8),]))
            doc.build([table])
            buffer.seek(0)
            response = HttpResponse(buffer,content_type="application/pdf",)
            response["Content-Disposition"] = (f'inline; filename="reserve_employee_{employee_id}.pdf"')
            return response
        return HttpResponse("نوع فایل نامعتبر است یا درخواستی ارسال نشده.", status=400)
        


@admin.register(FoodMenu)
class FoodMenuAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    list_display=('food','location','date',)
    list_filter=('location',)
    ordering=('date',)
    list_per_page=50

    change_list_template='admin/foodmenu_changelist.html'

    def get_urls(self):
        urls=super().get_urls()
        custom_urls=[path('weekly_menu/<str:location>',self.admin_site.admin_view(self.weekly_menu),
                          name='weekly_menu'),]
        return urls+custom_urls
    
    @method_decorator(never_cache)
    def weekly_menu(self,request,location):
        today=jdatetime.date.today()
        days_name=["شنبه" ,"یکشنبه" , "دوشنبه" , "سه‌شنبه" , "چهارشنبه" ,"پنجشنبه"]
        dif=today.weekday()
        days_from_saturday=(dif-0)%7
        saturday=today-timedelta(days=days_from_saturday)
        next_saturday=saturday+timedelta(days=7)
        week_dates=[saturday+timedelta(days=i) for i in range(6)]
        week_dates_next=[next_saturday+timedelta(days=i) for i in range(6) ]
        foods = {food.date: food.food for food in FoodMenu.objects.filter(
        location=location,
        date__gte=saturday,
        date__lt=next_saturday)}
        foods_next={food.date: food.food for food in FoodMenu.objects.filter(
            location=location,
            date__gte=next_saturday,
            date__lt=next_saturday+timedelta(days=7))}
        week_data = [{
        'id': i + 1,
        'day': days_name[i],
        'date': week_dates[i],
        'food': foods.get(week_dates[i], '')}for i in range(6)]
        week_data_next=[{
            'id':i+1,
            'day':days_name[i],
            'date':week_dates_next[i],
            'food':foods_next.get(week_dates_next[i], '')}for i in range(6)]

        if request.method=='POST':
            for item in week_data:
                food = request.POST.get(f"food_{item['date'].strftime('%Y-%m-%d')}")
                if food:
                    FoodMenu.objects.update_or_create(location=location,date=item['date'], 
                                                   defaults={'food':food,})
            for item in week_data_next:
                food = request.POST.get(f"food_{item['date'].strftime('%Y-%m-%d')}")
                if food:
                    FoodMenu.objects.update_or_create(location=location,date=item['date'], 
                                                   defaults={'food':food,})
            return redirect(request.path)
        if request.user.groups.filter(name__in=['Managers', 'Restaurant Coordinator']).exists():
            display_location=dict(Employees.LOCATION_CHOISES).get(location,location)
            return render(request,'admin/weekly_menu.html',{'location':display_location,'week_data':week_data,'week_data_next':week_data_next,
                                                        'today':today,})
        else:
            messages.error(request,'شما به این صفحه دسترسی ندارید')
            return redirect('admin/accounts/foodmenu/')

from django.contrib.auth.models import Group , User
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

admin.site.unregister(Group)

class GroupUserInline(admin.TabularInline):
    model = User.groups.through
    extra = 0

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    inlines = [GroupUserInline]
    