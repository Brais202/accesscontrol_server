
# Create your views here.
from django.shortcuts import render , redirect
from django.http import JsonResponse, HttpResponse
from .models import AccessLog, HSMData, EntrySchedule , AppKey2
from django.utils import timezone
import hmac
import hashlib

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

def get_appkey2(request):
    # Supongamos que solo existe una fila con la AppKey2
    appkey_record = AppKey2.objects.first()
    if not appkey_record:
        return JsonResponse({"error": "No AppKey2 found"}, status=404)
    
    return JsonResponse(appkey_record.key_value, safe=False)

def compute_appkey0(request):
    # Obtiene los parámetros de la petición
    cardid = request.GET.get('cardid')
    msg = request.GET.get('msg')  # se espera "key UID"
    
    if not cardid or not msg:
        return JsonResponse({"error": "Se requieren los parámetros 'cardid' y 'msg'"}, status=400)
    
    # Obtiene la AppMasterKey; se asume que existe al menos un registro en HSMData
    try:
        hsm_record = HSMData.objects.first()
        masterkey = hsm_record.masterkey  # Este campo contiene la clave en hexadecimal
    except Exception as e:
        return JsonResponse({"error": "No se pudo obtener la AppMasterKey"}, status=500)
    
    try:
        # Convierte la masterkey de hexadecimal a bytes
        key_bytes = bytes.fromhex(masterkey)
    except Exception as e:
        return JsonResponse({"error": "La AppMasterKey tiene un formato incorrecto"}, status=500)
    
    try:
        # Se asume que cardid se pasa como un string hexadecimal de 16 bytes
        cardid_bytes = bytes.fromhex(cardid)
    except Exception as e:
        return JsonResponse({"error": "El cardid debe estar en formato hexadecimal"}, status=400)
    
    # Convierte el mensaje a bytes
    message_bytes = msg.encode()  # Ejemplo: "key UID"
    
    # Concatenamos cardid_bytes y message_bytes; el orden puede ajustarse según tu especificación
    data = cardid_bytes + message_bytes
    
    # Calcula el HMAC-SHA256
    mac = hmac.new(key_bytes, data, hashlib.sha256).digest()
    
    # Toma los primeros 16 bytes para formar la clave AES128 (AppKey0)
    appkey0_bytes = mac[:16]
    appkey0_hex = appkey0_bytes.hex().upper()
    
    # Devuelve solo la clave en formato JSON (un string sin envoltura)
    return JsonResponse(appkey0_hex, safe=False)