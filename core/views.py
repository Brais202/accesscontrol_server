
# Create your views here.
from django.shortcuts import render , redirect
from django.http import JsonResponse, HttpResponse
from .models import AccessLog, HSMData, EntrySchedule , AppKey2
from django.utils import timezone
import os
import binascii
import subprocess

# Parámetros de tu instalación
PKCS11_TOOL = r"C:\Program Files\OpenSC Project\OpenSC\tools\pkcs11-tool.exe"
PKCS11_MODULE = r"C:\SoftHSM2\lib\softhsm2-x64.dll"
SLOT = "1945065443"
PIN = "6666"
KEY_ID = "02"

# Rutas fijas de input/output
INPUT_PATH = r"C:\Users\brais\Documents\input.bin"
OUTPUT_PATH = r"C:\Users\brais\Documents\hmac.bin"

def genera_hmac():
    """
    Llama a pkcs11-tool.exe para firmar INPUT_PATH
    y volcar el resultado en OUTPUT_PATH.
    """
    args = [
        PKCS11_TOOL,
        "--module", PKCS11_MODULE,
        "--slot", SLOT,
        "--login",
        "--pin", PIN,
        "--session-rw",
        "--sign",
        "--mechanism", "SHA256-HMAC",
        "--id", KEY_ID,
        "--input-file", INPUT_PATH,
        "--output-file", OUTPUT_PATH,
    ]
    # Ejecutamos la herramienta
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode != 0:
        # Puedes loguear res.stderr para depurar
        raise RuntimeError(f"pkcs11-tool falló: {res.stderr.strip()}")
    return True






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
    # 1) Parámetros
    cardid = request.GET.get('cardid')
    msg    = request.GET.get('msg')   # p.ej. "key UID"

    if not cardid or not msg:
        return JsonResponse(
            {"error": "Se requieren 'cardid' y 'msg'"},
            status=400
        )

    # 2) Conversión a bytes
    try:
        cardid_bytes = binascii.unhexlify(cardid)
    except binascii.Error:
        return JsonResponse(
            {"error": "El cardid debe ser hex válido"},
            status=400
        )
    data = cardid_bytes + msg.encode('utf-8')

    # 3) Escribe el fichero input.bin
    try:
        with open(INPUT_PATH, "wb") as f:
            f.write(data)
    except Exception as e:
        return JsonResponse(
            {"error": f"No pude escribir {INPUT_PATH}: {e}"},
            status=500
        )

    # 4) Lanza el hmac en el HSM vía pkcs11-tool
    try:
        genera_hmac()
    except Exception as e:
        return JsonResponse(
            {"error": f"Error al generar el HMAC: {e}"},
            status=500
        )

    # 5) Lee el resultado de hmac.bin
    try:
        with open(OUTPUT_PATH, "rb") as f:
            full_mac = f.read()
    except Exception as e:
        return JsonResponse(
            {"error": f"No pude leer {OUTPUT_PATH}: {e}"},
            status=500
        )

    if len(full_mac) < 16:
        return JsonResponse(
            {"error": "El HMAC devuelto es demasiado corto."},
            status=500
        )

    # 6) Toma los primeros 16 bytes y pásalos a hex
    appkey0_hex = full_mac[:16].hex().upper()

    return JsonResponse(appkey0_hex, safe=False)