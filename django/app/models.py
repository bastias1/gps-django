from django.db import models
from django.contrib.auth.models import User

# Modelo Vehiculo
class Vehiculo(models.Model):
    patente = models.CharField(max_length=6, unique=True)  # Patente única
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anno = models.IntegerField()
    conductor = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='vehiculos')  # Relación uno a muchos

    def __str__(self):
        return f"{self.patente} - {self.modelo} ({self.anno})"

# Modelo Usuario
class Usuario(models.Model): 
    # Opciones para el tipo de usuario
    TIPO_USUARIO = [
        ('', 'Seleccione un tipo de usuario'),
        ('Administrador', 'Administrador'),
        ('Conductor', 'Conductor'),
    ]

    ESTADOS_CONDUCTOR = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Modelo user tiene los siguientes datos (Nombre, Apellido, Correo, Usuario, Contraseña, Fecha de Creación)
    rut = models.CharField(max_length=10, unique=True)
    telefono = models.BigIntegerField()
    tipo_usuario = models.CharField(max_length=50, choices=TIPO_USUARIO)
    estado = models.CharField(max_length=10, choices=ESTADOS_CONDUCTOR)  # Usar opciones predefinidas
    device = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()

    def ultima_posicion(self):
        """Obtiene la última posición GPS del conductor."""
        ultimo_log = self.gps_logs.order_by('-timestamp').first()
        if ultimo_log:
            return {'latitud': ultimo_log.latitud, 'longitud': ultimo_log.longitud, 'timestamp': ultimo_log.timestamp}
        return None
    
# Modelo para registrar posiciones GPS
class GPSLog(models.Model):
    conductor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='gps_logs')
    latitud = models.FloatField()
    longitud = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)  # Guarda automáticamente la fecha y hora de creación

    def __str__(self):
        return f"{self.conductor} - {self.latitud}, {self.longitud} @ {self.timestamp}"