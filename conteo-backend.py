import serial
import psycopg2
import re

puerto_serial = 'COM6'
baudrate = 9600

conn = psycopg2.connect(
    host="localhost",
    database="Conteo",
    user="postgres",
    password="admin",
    port=5432
)
cursor = conn.cursor()

ser = serial.Serial(puerto_serial, baudrate, timeout=1)

print("Escuchando puerto serial...")

try:
    while True:
        if ser.in_waiting > 0:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()
            print("Dato recibido:", linea)

            # Solo guardar cuando Arduino manda el resumen final al desactivarse
            if "Modo DESACTIVO" in linea:
                resultado = re.search(r'Total detectado:\s*(\d+)', linea)
                if resultado:
                    conteo = int(resultado.group(1))
                    print(f"Guardando conteo {conteo} en PostgreSQL")

                    cursor.execute(
                        "INSERT INTO conteos (cantidad) VALUES (%s)", (conteo,)
                    )
                    conn.commit()
                    print("Guardado exitoso")

except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    cursor.close()
    conn.close()
    ser.close()


#HOLAS