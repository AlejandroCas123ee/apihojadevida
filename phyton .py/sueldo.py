print("Calcular el sueldo del empleado")

sueldo = float(input("Registrar el sueldo del empleado: "))
antigue = int(input("Registrar los años de antiguedad: "))

if sueldo<500 and antigue>10:
    aumento = sueldo * 0.20
    sueldot = sueldo + aumento 

elif sueldo <500 and antigue<10:
    aumento = sueldo * 0.05
    sueldot= sueldo +aumento
else:
    aumento = 0 
    sueldot = sueldo 
     
print(f"el sueldo inicial: {sueldo}\n"
      f"valor del aumento: {aumento}\n"
      f"total de pago: {sueldot}")    