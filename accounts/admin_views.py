from openpyxl import Workbook
from django.http import HttpResponse
from accounts.models import Reservation

def export_employee_reservations_excel(response,employee):
        wb=Workbook()
        ws=wb.active
        ws.title="Employee Reservations"
        ws.append(['name','food','date'])
        reservations_employee=Reservation.objects.select_related('employee','food').filter(employee=employee).order_by('reserve_date')
        for reserve in reservations_employee:
            ws.append([reserve.employee.name,reserve.food.name,reserve.reserve_date])
        response=HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition']='attachment;filename="reserve_{employee}.xlsx"'
        wb.save(response)
        return response