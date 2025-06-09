# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class AccessLog(models.Model):
    uid = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True, null=True)
    authorized = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.uid}) - {'Autorizado' if self.authorized else 'No autorizado'} - {self.timestamp}"


class Role(models.Model):
    """
    Defines a role to be assigned to a User.
    """
    code = models.CharField(max_length=10, unique=True, help_text="Internal code for the role, e.g. 'admin', 'user'")
    name = models.CharField(max_length=50, help_text="Descriptive name for the role")

    def __str__(self):
        return f"{self.code}: {self.name}"


class HSMData(models.Model):
    """
    Simula la información que almacenaría un HSM.
    """
    uid = models.CharField(max_length=14, unique=True, help_text="UID de la tarjeta NFC (por ejemplo, 7 bytes en hexadecimal)")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    masterkey = models.CharField(max_length=32, help_text="Clave maestra asociada, expresada en hexadecimal (32 caracteres para 128 bits)")
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="users",
        help_text="Rol asociado al usuario"
    )
    def __str__(self):
        base = f"{self.first_name} {self.last_name} ({self.uid})"
        return f"{base} - Rol: {self.role.code if self.role else 'Sin asignar'}"

class EntrySchedule(models.Model):
    """
    Define el horario permitido para el acceso de un usuario.
    """
    hsm_data = models.ForeignKey(HSMData, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(max_length=9, help_text="Nombre del día, ej. 'Monday'")
    start_time = models.TimeField(help_text="Hora de inicio del acceso permitido")
    end_time = models.TimeField(help_text="Hora de finalización del acceso permitido")
    
    def __str__(self):
        return f"{self.hsm_data.uid} - {self.day_of_week}: {self.start_time} a {self.end_time}"
    

class AppKey2(models.Model):
    """
    Modelo para almacenar la AppKey2 que se utiliza para todas las tarjetas.
    """
    key_value = models.CharField(max_length=32, help_text="Clave AES en hexadecimal (por ejemplo, 16 bytes => 32 hex)")

    def __str__(self):
        return f"AppKey2: {self.key_value}"