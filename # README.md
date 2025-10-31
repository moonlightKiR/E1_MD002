# README.md

## Acceso a la máquina virtual

La IP de la máquina virtual es: **172.16.124.137**

---

## Copiar `main.sh` a la máquina virtual

Puedes transferir el archivo `main.sh` a la máquina virtual utilizando `scp` desde tu máquina local. Usa el siguiente comando:

```bash
scp main.sh guille@172.16.124.137:/home/guille/
```

- **Usuario:** `guille`
- **Contraseña:** `357253`

Cuando se te solicite la contraseña, introduce `357253`.

---

## Ejecutar `main.sh` al inicio del sistema

## Daemon con systemd (Recomendado para producción)

Para crear un daemon profesional que se gestione con systemd, sigue estos pasos:

### Pasos:

1. Crea el archivo del servicio:
   ```bash
   sudo nano /etc/systemd/system/etl.service
   ```

2. Añade el siguiente contenido:
   ```ini
   [Unit]
   Description=ETL Application - Auto inicio
   After=network.target

   [Service]
   Type=simple
   User=guille
   WorkingDirectory=/home/guille
   ExecStart=/bin/bash /home/guille/main.sh
   Restart=always
   RestartSec=1

   [Install]
   WantedBy=multi-user.target
   ```

3. Recarga systemd y habilita el servicio:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable etl.service
   sudo systemctl start etl.service
   ```

4. Verifica que está funcionando:
   ```bash
   sudo systemctl status etl.service
   ```

### Comandos útiles para gestionar el daemon:

```bash
# Ver estado
sudo systemctl status etl.service

# Ver logs en tiempo real
sudo journalctl -u etl.service -f

# Detener el servicio
sudo systemctl stop etl.service

# Iniciar el servicio
sudo systemctl start etl.service

# Reiniciar el servicio
sudo systemctl restart etl.service

# Deshabilitar el auto-inicio
sudo systemctl disable etl.service
```

---

> Con cualquiera de estos métodos, el script se ejecutará automáticamente cada vez que la máquina virtual arranque.

