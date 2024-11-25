"""
URL configuration for proyectoflota project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views as views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),

     # Vistas principales
    path('', views.index),

    # Sesión
    path('login/', views.inicioSesion, name='login'),
    path('logout/', views.cerrarSesion, name='logout'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),

    # Menús
    path('mapa/', login_required(views.mapa), name='mapa'),
    path('mapa/data/',login_required(views.mapa_data), name='mapa_data'),

    # Empleados
    path('usuarios/', login_required(views.gestionUsuarios), name='usuarios'),
    path('crearUsuario/', login_required(views.creacionUsuario), name='creacionUsuario'),
    path('modificarUsuario/<int:id>/', login_required(views.modificarUsuario), name='modificarUsuario'),
    path('eliminarUsuario/<int:id>/', login_required(views.eliminarUsuario), name='eliminarUsuario'),


    #Conductores
    path('conductores/',login_required(views.gestionConductores),name='conductores'),
    path('crearConductor/',login_required(views.crearConductor),name='creacionConductor'),
    path('modificarConductor/<int:id>/',login_required(views.modificarConductor),name='modificarConductor'),
    path('eliminarConductor/<int:id>/',login_required(views.eliminarConductor),name='eliminarConductor'),
    
    # Vehículos
    path('vehiculos/', login_required(views.gestionVehiculos), name='vehiculos'),
    path('crearVehiculo/', login_required(views.crearVehiculo), name='crearVehiculo'),
    path('modificarVehiculo/<int:id>/', login_required(views.modificarVehiculo), name='modificarVehiculo'),
    path('eliminarVehiculo/<int:id>/', login_required(views.eliminarVehiculo), name='eliminarVehiculo'),
]
