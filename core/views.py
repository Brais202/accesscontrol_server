
# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from .models import AccessLog

def submit_uid(request):
    uid = request.GET.get("uid")
    if not uid:
        return JsonResponse({"error": "No UID provided"}, status=400)
    
    # Crea el registro de acceso
    log = AccessLog.objects.create(uid=uid)
    
    # Responde con una confirmación y datos del registro
    return JsonResponse({
        "message": "UID registrado",
        "uid": log.uid,
        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })

def log_list(request):
    logs = AccessLog.objects.all().order_by("-timestamp")
    return render(request, "core/log_list.html", {"logs": logs})
