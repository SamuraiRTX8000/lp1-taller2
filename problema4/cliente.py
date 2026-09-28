#!/usr/bin/env python3
"""
Problema 4: Servidor HTTP básico - Cliente
Objetivo: Crear un cliente HTTP que realice una petición GET a un servidor web local
"""

import http.client



address = ("localhost", 8000)


# HTTPConnection permite establecer conexiones HTTP con servidores
cliente = http.client.HTTPConnection(address)


# TODO: Realizar una petición GET al path raíz ('/')
# request() envía la petición HTTP al servidor
# Primer parámetro: método HTTP (GET, POST, etc.)
# Segundo parámetro: path del recurso solicitado
cliente.request('GET','/')


# TODO: Obtener la respuesta del servidor
# getresponse() devuelve un objeto HTTPResponse con los datos de la respuesta
respuesta = cliente.getresponse()

# TODO: Leer el contenido de la respuesta
# read() devuelve el cuerpo de la respuesta en bytes
datos = respuesta.read().decode()

# TODO: Decodificar los datos de bytes a string e imprimirlos
# decode() convierte los bytes a string usando UTF-8 por defecto
print(datos)

# TODO: Cerrar la conexión con el servidor
cliente.close()

