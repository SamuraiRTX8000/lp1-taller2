#!/usr/bin/env python3
"""
Problema 4: Servidor HTTP básico - Cliente
Objetivo: Crear un cliente HTTP que realice una petición GET a un servidor web local
"""

import http.client



address = ("localhost", 8000)


# HTTPConnection permite establecer conexiones HTTP con servidores
cliente = http.client.HTTPConnection(address)



# request() envía la petición HTTP al servidor
# Primer parámetro: método HTTP (GET, POST, etc.)
# Segundo parámetro: path del recurso solicitado
cliente.request('GET','/')


# getresponse() devuelve un objeto HTTPResponse con los datos de la respuesta
respuesta = cliente.getresponse()


# read() devuelve el cuerpo de la respuesta en bytes
datos = respuesta.read().decode()


# decode() convierte los bytes a string usando UTF-8 por defecto
print(datos)


cliente.close()

