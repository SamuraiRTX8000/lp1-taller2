# Sistema distribuido de chat

## Descripción

Chat distribuido en Python. Un servidor principal distribuye las conexiones entre tres backends, que atienden a los clientes y propagan eventos de chat entre sí.

## Arquitectura

```text
Cliente
   ↓
Servidor principal :5000
   ↓
Backend :5001 / Backend :5002 / Backend :5003
   ↔ Sincronización entre backends
```

- **Servidor principal:** comprueba la disponibilidad de los backends y asigna conexiones mediante Round Robin.
- **Backends:** gestionan las conexiones, los usuarios y los mensajes de chat.
- **Clientes:** se conectan al servidor principal y envían comandos.

## Características principales

- Atención de múltiples clientes mediante hilos.
- Chat por comandos, con usuarios y salas.
- Distribución Round Robin y health checks.
- Propagación de eventos entre backends.
- Tolerancia básica a fallos, desconexiones y errores de socket.
- Comunicación mediante sockets TCP.

## Puertos

| Componente | Puerto |
|---|---:|
| Servidor principal | 5000 |
| Backend 1 | 5001 |
| Backend 2 | 5002 |
| Backend 3 | 5003 |
| Comunicación interna entre backends | 15001–15003 |

Los puertos `15001`–`15003` se usan para sincronizar eventos entre backends.

## Comandos del cliente

| Comando | Función |
|---|---|
| `HELP` | Muestra los comandos disponibles. |
| `MSG mensaje` | Envía un mensaje a la sala actual. |
| `USERS` | Muestra los usuarios de la sala actual. |
| `JOIN sala` | Entra en la sala indicada. |
| `LEAVE` | Sale de la sala actual. |
| `QUIT` | Cierra la conexión. |

## Ejecución

Desde el directorio `problema9`, inicia cada backend en una terminal:

```bash
python3 backend_copilot.py 5001
```

```bash
python3 backend_copilot.py 5002
```

```bash
python3 backend_copilot.py 5003
```

En otra terminal, inicia el servidor principal:

```bash
python3 servidor_copilot.py
```

Después, inicia uno o más clientes en terminales separadas:

```bash
python3 cliente_copilot.py
```

## Tecnologías

- Python
- Sockets TCP
- `threading`
- `select`
- JSON