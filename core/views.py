
# Create your views here.
from django.shortcuts import render , redirect
from django.http import JsonResponse
from .models import AccessLog, HSMData, EntrySchedule
from django.utils import timezone

def submit_uid(request):
    uid = request.GET.get("uid")
    if not uid:
        return JsonResponse({"error": "No UID provided"}, status=400)
    
    # Crea el registro de acceso
    log = AccessLog.objects.create(uid=uid)
    
    # Responde con una confirmación y datos del registro
    return JsonResponse({
        "message": "UID registered",
        "uid": log.uid,
        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })

def log_list(request):
    logs = AccessLog.objects.all().order_by("-timestamp")
    return render(request, "core/log_list.html", {"logs": logs})

def authenticate_uid(request):
    uid = request.GET.get("uid")
    if not uid:
        return JsonResponse({"error": "No UID provided"}, status=400)
    
    try:
        hsm_record = HSMData.objects.get(uid__iexact=uid)
    except HSMData.DoesNotExist:
        return JsonResponse({"authorized": False, "error": "UID no registrado"}, status=404)
    
   
    now = timezone.now()
    current_time = now.time()
    current_day = now.strftime('%A')
    
    schedules = EntrySchedule.objects.filter(hsm_data=hsm_record, day_of_week__iexact=current_day)
    authorized = any(schedule.start_time <= current_time <= schedule.end_time for schedule in schedules)
    log = AccessLog.objects.create(uid=uid, name=hsm_record.first_name,authorized=authorized)
      
    return redirect('log_list')