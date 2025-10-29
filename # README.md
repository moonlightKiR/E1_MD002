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

Para que el script `main.sh` se ejecute automáticamente al iniciar la máquina virtual, debes editar el archivo `/etc/rc.local`.

### Pasos:

1. Abre el archivo `/etc/rc.local` con permisos de superusuario:

   ```bash
   sudo nano /etc/rc.local
   ```

2. Antes de la línea `exit 0` (o al final si no existe), añade la siguiente línea:

   ```
   /bin/bash /home/guille/main.sh &
   ```

   El contenido debería quedar similar a:

   ```bash
   #!/bin/bash
   /bin/bash /home/guille/main.sh &
   exit 0
   ```

3. Guarda el archivo y sal del editor (`CTRL+O`, `Enter`, luego `CTRL+X` en nano).

---

> Con esto, el script se ejecutará automáticamente cada vez que la máquina virtual arranque.

