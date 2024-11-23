from django.shortcuts import render,redirect
from django.http import Http404,JsonResponse
from .models import *
from . import forms 
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests

# Create your views here.
def index(request):
    return render(request,'login.html')

def inicioSesion(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.success(request,("Hubo un error al iniciar sesion."))
            return redirect('login')
    else:
        return render(request, 'login.html')
    
def cerrarSesion(request):
    logout(request)
    messages.success(request,("Se a cerrado la sesion."))
    return redirect('login')

def dashboard(request):
    return render(request, 'dashboard.html')

def get_users_and_devices():
    try:
        # Fetch the data from the Recorder API
        response = requests.get("http://192.168.0.6:8083/api/0/monitor")  # Cambiar la IP con la IP del Owntracks.
        response.raise_for_status()
        data = response.text.strip().split("\n")
        users_devices = []

        for line in data:
            parts = line.split()  # Dividir Lineas
            if len(parts) > 1:
                topic = parts[1]  # Topic contiene user y device (dispositivo)
                # Ejemplo topic: "owntracks/conductor/beyond1"
                try:
                    _, user, device = topic.split("/")
                    users_devices.append({'user': user, 'device': device})

                    # Actualizar el campo dipositivo para el usuario/conductor correspondiente en la bdd
                    try:
                        usuario = Usuario.objects.get(user__username=user)
                        if usuario.device != device:  # Actualizar solo si el dispositivo a cambiado
                            usuario.device = device
                            usuario.save()
                            print(f"Updated device for user {user}: {device}")
                    except Usuario.DoesNotExist:
                        print(f"User {user} not found in the database, skipping device update.")

                except ValueError:
                    continue  # Skip lines that don't match the format

        return users_devices
    except requests.RequestException as e:
        print(f"Error fetching users and devices: {e}")
        return []

def mapa(request):
    # Fetch all conductors
    conductores = Usuario.objects.filter(tipo_usuario='Conductor')
    conductores_ubi = []

    for conductor in conductores:
        # Get the last known position of the conductor
        ultima_posicion = conductor.ultima_posicion()
        if ultima_posicion:
            conductores_ubi.append({
                'user_id': f"{conductor.user.first_name} {conductor.user.last_name}",
                'latitud': ultima_posicion['latitud'],
                'longitud': ultima_posicion['longitud'],
                'timestamp': ultima_posicion['timestamp'],
            })

    # Pass the data to the template
    return render(request, 'mapa.html', {'drivers': conductores_ubi})

def mapa_data(request):
    fetch_and_save_gps_data()
    conductores = Usuario.objects.filter(tipo_usuario='Conductor')
    conductores_ubi = []

    for conductor in conductores:
        ultima_posicion = conductor.ultima_posicion()
        if ultima_posicion:
            conductores_ubi.append({
                'user_id': f"{conductor.user.first_name} {conductor.user.last_name}",
                'latitud': ultima_posicion['latitud'],
                'longitud': ultima_posicion['longitud'],
                'timestamp': ultima_posicion['timestamp'],
            })

    return JsonResponse(conductores_ubi, safe=False)

def fetch_and_save_gps_data():
    users_devices = get_users_and_devices()  # Get user/device pairs
    if not users_devices:
        print("No users or devices found.")
        return

    for user_device in users_devices:
        user = user_device['user']
        device = user_device['device']

        params = {
            'user': user,
            'device': device
        }
        try:
            print(f"Fetching data for user={user} and device={device}...")
            response = requests.get("http://192.168.0.6:8083/api/0/locations", params=params)
            response.raise_for_status()
            data = response.json()
            

            # Debugging: Print the API response
            print(f"Response for user={user}, device={device}: {data}")

            if "data" in data:
                locations = data["data"]  # Extract the location data
                for entry in locations:
                    print(f"Raw location entry: {entry}")  # Debugging

                    lat = entry.get('lat')  # Adjust key names based on actual data
                    lon = entry.get('lon')
                    tst = entry.get('tst')

                    if lat and lon and tst:
                        print(f"Processing entry with lat={lat}, lon={lon}, tst={tst}")
                        try:
                            conductor = Usuario.objects.get(user__username=user)
                            GPSLog.objects.update_or_create(
                                conductor=conductor,
                                defaults={
                                    "latitud": lat,
                                    "longitud": lon,
                                }
                            )
                            print(f"GPSLog created/updated for lat={lat}, lon={lon}")
                        except Usuario.DoesNotExist:
                            print(f"User {user} not found in the database, skipping entry.")
                    else:
                        print(f"Incomplete entry: {entry}")
            else:
                print(f"Unexpected API response format: {data}")


        except requests.RequestException as e:
            print(f"Error fetching data for user={user}, device={device}: {e}")

    print("GPS data successfully fetched and saved!")




#Empleados
def gestionUsuarios(request):
    usuarios = Usuario.objects.filter(tipo_usuario='Administrador')
    
    data = {
        'usuarios':usuarios
    }
    return render(request, 'gestionUsuarios.html',data)

def creacionUsuario(request):
    if request.method=='POST':
        form_user = forms.registroUser(request.POST)
        form_usuario = forms.registroUsuario(request.POST)
        print("Form Insertado")
        if form_usuario.is_valid() and form_user.is_valid():
            print("Datos insertados a la base de datos")
            user = form_user.save(commit=False)
            user.set_password(form_user.cleaned_data['password'])
            user.save()
            usuario = form_usuario.save(commit=False)
            usuario.tipo_usuario = 'Administrador'
            usuario.user = user
            usuario.save()
            return redirect('usuarios')  # Redirigir a la URL raíz
        else:
            print("Errores en los formularios")
    else:
        print("Datos NO insertados")
        form_user = forms.registroUser()
        form_usuario = forms.registroUsuario()
    
    data = {
        'form_usuario':form_usuario,
        'form_user':form_user,
    }
    return render(request,'crearUsuarios.html',data)

def modificarUsuario(request,id):
    # Obtener el empleado por ID
    usuario = Usuario.objects.get(id=id)
    user = usuario.user  # Obtener el usuario asociado

    # Formularios prellenados con los datos actuales
    form_usuario = forms.registroUsuario(instance=usuario)
    form_user = forms.registroUser(instance=user)

    if request.method == "POST":
        # Actualizar datos de empleado y usuario
        form_usuario = forms.registroUsuario(request.POST, instance=usuario)
        form_user = forms.registroUser(request.POST, instance=user)

        if form_usuario.is_valid() and form_user.is_valid():
            # Guardar datos de usuario y empleado
            user = form_user.save(commit=False)
            if form_user.cleaned_data.get('password'):
                user.set_password(form_user.cleaned_data['password'])
            user.save()

            usuario = form_usuario.save(commit=False)
            usuario.user = user
            usuario.save()

            print("Usuario modificado correctamente")
            return redirect('usuarios')  # Redirige al listado de empleados

    data = {
        'form_usuario': form_usuario,
        'form_user': form_user,
        'es_modificar': True,  # Variable de contexto para diferenciar
        'usuario': usuario,
    }
    return render(request, 'crearUsuarios.html', data)

def eliminarUsuario(request,id):
    if User.objects.count() <= 1:
        messages.success(request,("No se puede eliminar el último usuario"))
        return redirect('usuarios')
    usuario = Usuario.objects.get(id=id)
    usuario.delete()
    print("Usuario Eliminado")
    return redirect('usuarios')



#GESTIONAR VEHICULOS

def gestionVehiculos(request):
    vehiculos = Vehiculo.objects.all()
    
    data = {
        'vehiculos':vehiculos
    }
    return render(request, 'gestionVehiculos.html',data)


def crearVehiculo(request):
    if request.method == 'POST':
        form = forms.registroVehiculo(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/vehiculos')
    else:
        form = forms.registroVehiculo()

    data = {'form': form}
    return render(request, 'crearVehiculo.html', data)


def eliminarVehiculo(request, id):
    try:
        vehiculo = Vehiculo.objects.get(id=id)
        vehiculo.delete()
    except Vehiculo.DoesNotExist:
        pass
    return redirect('/vehiculos')

def modificarVehiculo(request, id):
    vehiculo = Vehiculo.objects.get(id=id)  # Obtener el vehículo

    # Si el formulario es enviado (POST)
    if request.method == 'POST':
        form = forms.registroVehiculo(request.POST, instance=vehiculo)  # Usamos el formulario con la instancia
        if form.is_valid():
            form.save()  # Guardamos los cambios en la base de datos
            return redirect('/vehiculos')  # Redirigimos después de guardar
    else:
        form = forms.registroVehiculo(instance=vehiculo)  # Para GET, solo pasamos la instancia

    data = {'form': form}
    return render(request, 'crearVehiculo.html', data)


#Gestionar Conductores

def gestionConductores(request):
    usuarios = Usuario.objects.filter(tipo_usuario='Conductor').prefetch_related('vehiculos')

    data = {
        'usuarios':usuarios
    }

    return render(request,'gestionConductores.html',data)

def crearConductor(request):
    if request.method=='POST':
        form_user = forms.registroUser(request.POST)
        form_usuario = forms.registroUsuario(request.POST)
        if form_usuario.is_valid() and form_user.is_valid():
            user = form_user.save(commit=False)
            user.set_password(form_user.cleaned_data['password'])
            user.save()
            usuario = form_usuario.save(commit=False)
            usuario.tipo_usuario = 'Conductor'
            usuario.user = user
            usuario.save()
            return redirect('conductores')  # Redirigir a la URL raíz
        else:
            print("Errores en los formularios")
    else:
        print("Datos NO insertados")
        form_user = forms.registroUser()
        form_usuario = forms.registroUsuario()
    
    data = {
        'form_usuario':form_usuario,
        'form_user':form_user,
    }

    return render(request,'crearConductor.html',data)


def modificarConductor(request,id):
    conductor = User.objects.get(id=id) # Obtener el vehículo
    conductor1 = Usuario.objects.get(id=id)

    # Si el formulario es enviado (POST)
    if request.method == 'POST':
        form_user = forms.registroUser(request.POST, instance=conductor)  # Usamos el formulario con la instancia
        form_usuario = forms.registroUsuario(request.POST, instance=conductor)
        if form_user.is_valid() and form_usuario.is_valid():
            form_user.save()
            form_usuario.save()  # Guardamos los cambios en la base de datos
            return redirect('conductores')  # Redirigimos después de guardar
    else:
        form_user = forms.registroUser(instance=conductor) 
        form_usuario = forms.registroUsuario(instance=conductor1)   # Para GET, solo pasamos la instancia

    data = {
        'form_usuario':form_usuario,
        'form_user':form_user,
        }
    return render(request, 'crearConductor.html', data)

def eliminarConductor(request,id):
    usuario = Usuario.objects.get(id=id)
    usuario.delete()
    return redirect('conductores')