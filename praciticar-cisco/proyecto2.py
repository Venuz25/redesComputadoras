import tkinter as tk
from tkinter import messagebox
import traceback

# FUNCIONES
def redtype(s0):
    if s0 < 128:
        return "Clase A"
    elif s0 >= 128 and s0 < 192:
        return "Clase B"
    elif s0 >= 192 and s0 < 224:
        return "Clase C"

def calc(ip, mask, wildcard, num_mask):
    num_host = 2 ** (32 - num_mask) - 2
    
    ip_red = []
    for i, ip_num in enumerate(ip):
        aux = ip_num & mask[i]
        ip_red.append(aux)
    
    broadcast = []
    for i, ip_num in enumerate(ip_red):
        aux = ip_num | wildcard[i]
        broadcast.append(aux)
    
    host_min = ""
    for i, ip_num in enumerate(ip_red):
        if i == 3:
            host_min += str(ip_num + 1)
        else:
            host_min += str(ip_num)
        host_min += "."
    host_min = host_min[:-1]
    
    host_max = ""
    for i, ip_num in enumerate(broadcast):
        if i == 3:
            host_max += str(ip_num - 1)
        else:
            host_max += str(ip_num)
        host_max += "."
    host_max = host_max[:-1]
    
    siguiente_red = []
    flag = False
    for i in range(3, -1, -1):
        if flag:
            siguiente_red.append(broadcast[i])
            continue
        
        if broadcast[i] == 255:
            if i != 0: 
                siguiente_red.append(0)
            else:
                siguiente_red = None
        else:
            siguiente_red.append(broadcast[i] + 1)
            flag = True
    siguiente_red = siguiente_red[::-1] if (siguiente_red != None) else None
    
        
    return {"ip": ip, 
            "ip red": ip_to_str(ip_red),
            "num host": num_host, 
            "broadcast": ip_to_str(broadcast), 
            "host min": host_min, 
            "host max": host_max,
            "ip_red": ip_red,
            "siguiente_red": siguiente_red,
            "ip_broadcast": broadcast}

def get_mask(num_bits):
    count = 0
    mask = []
    wildcard = []
    aux = ""
    mask_bin = ""
    for i in range(0, 4):
        for j in range(0, 8):
            if count < num_bits:
                aux += "1"
                count += 1
            else:
                aux += "0"
        mask_int = int(aux, 2)
        mask.append(mask_int)
        mask_bin += aux + "."
        wildcard.append(~mask_int & 0xFF)
        aux = ""
    mask_bin = mask_bin[:-1]
    return mask, wildcard, mask_bin

def ip_to_str(ip):
    ip_str = ""
    for i, ip_num in enumerate(ip):
        ip_str += str(ip_num)
        if i != 3:
            ip_str += "."
    return ip_str

def subnet_is_part_of_red(broadcast_red, broadcast_subred):
    if broadcast_red is None:
        return False
    for i in range(4):
        if broadcast_subred[i] > broadcast_red[i]:
            return False
    return True
    
    
def calcular(ip_split, num_mask, new_mask):
    try:
        clase = redtype(ip_split[0])
        
        mask, wildcard, mask_bin = get_mask(num_mask)
        
        inf = calc(ip_split, mask, wildcard, num_mask)
        
        # Mostrar los resultados en la interfaz
        resultado = (
            f"____________________________________________________\n"
            f"                        RED\n"
            f"             Dirección IP: {ip_to_str(ip_split)}\n"
            f"             Clase de red: {clase}\n"
            f" Mascara de red (binario): {mask_bin}\n"
            f"           Mascara de red: {ip_to_str(mask)}\n"
            f"                    Hosts: {inf["num host"]}\n"
            f"____________________________________________________\n"
            f"                    DIRECCIONES\n"
            f"         Dirección de red: {inf["ip red"]}\n"
            f"              Host mínimo: {inf["host min"]}\n"
            f"              Host máximo: {inf["host max"]}\n"
            f"   Dirección de broadcast: {inf["broadcast"]}\n"
        )
        
        # Calcular subredes si se ingresó una nueva máscara
        if new_mask:
           
            mask_red = mask.copy()
            new_bits = int(new_mask)
            
            if new_bits < num_mask:
                raise ValueError("La nueva máscara debe tener más bits que la original")
            
            bits_subred = new_bits - num_mask
            subnets = 2 ** bits_subred
            
            mask, wildcard, mask_bin = get_mask(new_bits)
        
            resultado += (           
                f"____________________________________________________\n"
                f"                       SUBREDES\n"
                f"       Numero de subredes: {subnets}\n"
                f"  Nueva máscara (binario): {mask_bin}\n"
                f"            Nueva máscara: {ip_to_str(mask)}\n"
                f"____________________________________________________\n"
            )
            
            broadcast_red = inf["ip_broadcast"].copy()
            i = 1
            broadcast_subred = inf["ip_broadcast"]

            # Calcular y mostrar las subredes
            resultado += "\nSubredes generadas:\n"
            
            ip_subred = inf["ip_red"].copy()

            while True:
                inf = calc(ip_subred, mask, wildcard, new_bits)
                print(inf)
                broadcast_subred = inf["ip_broadcast"]
                if subnet_is_part_of_red(broadcast_red, broadcast_subred):
                    resultado += (
                        f"\nSubred {i}:\n"
                        f"         Dirección de red: {inf["ip red"]}\n"
                        f"              Host mínimo: {inf["host min"]}\n"
                        f"              Host máximo: {inf["host max"]}\n"
                        f"   Dirección de broadcast: {inf["broadcast"]}\n"
                        f"                    Hosts: {inf["num host"]}\n"
                        f"____________________________________________________\n"
                    )
                    ip_subred = inf["siguiente_red"]
                    if ip_subred is None:
                        break
                    i += 1
                else:
                    break
        
        print(resultado)

        # Mostrar los resultados en la interfaz
        resultado_text.set(resultado)
        

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")
        traceback.print_exc()

def validarIp():
    ip = ip_entry.get()
    ip_split = ip.split('/')
    if len(ip_split) != 2:
        messagebox.showerror("Error", "La dirección IP debe tener el formato x.x.x.x/x")
        ip_entry.focus()
        return
    
    try:
        num_mask = int(ip_split[1])
    except ValueError:
        messagebox.showerror("Error", "El número de bits de la máscara debe ser un número")
        ip_entry.focus()
        return
    
    ip_split = ip_split[0].split('.')
    try:
        ip_split = list(map(int, ip_split))
    except ValueError:
        messagebox.showerror("Error", "Los octetos de la dirección IP deben ser números")
        ip_entry.focus()
        return
    
    if len(ip_split) != 4:
        messagebox.showerror("Error", "La dirección IP debe tener 4 octetos")
        ip_entry.focus()
        return
    for ip_num in ip_split:
        if ip_num < 0 or ip_num > 255:
            messagebox.showerror("Error", "Los octetos de la dirección IP deben ser números entre 0 y 255")
            ip_entry.focus()
            return
    
    if num_mask < 0 or num_mask > 32:
        messagebox.showerror("Error", "El número de bits de la máscara debe ser un número entre 0 y 32")
        ip_entry.focus()
        return
    
    new_mask_entry.focus()
    return ip_split, num_mask

def validarMascaraSubred():
    try:
        ip_split, num_mask = validarIp()
    except TypeError:
        return
    new_mask = new_mask_entry.get()
    if new_mask:
        try:
            new_mask = int(new_mask)
            if new_mask < num_mask or new_mask > 32:
                messagebox.showerror("Error", f"El número de bits de la máscara debe ser un número entre {num_mask} y 32")
                new_mask_entry.focus()
                return
        except ValueError:
            messagebox.showerror("Error", "El número de bits de la máscara debe ser un número entero")
            new_mask_entry.focus()
            return
    if ip_split and num_mask:
        calcular(ip_split, num_mask, new_mask)
    
# Config ventana
root = tk.Tk()
root.title("Calculadora de red")

# Elementos
tk.Label(root, text="Proyecto 2: Calculadora de Redes").pack(pady=5)
tk.Label(root, text="Ingresa la IP (x.x.x.x/x):").pack(pady=10)
ip_entry = tk.Entry(root, width=30)
ip_entry.pack()
ip_entry.focus()
ip_entry.bind("<Return>", lambda e: validarIp())

# Entrada opcional para Netmask to Subnet
tk.Label(root, text="Máscara de subred (opcional):").pack(pady=10)
new_mask_entry = tk.Entry(root, width=30)
new_mask_entry.pack()
new_mask_entry.bind("<Return>", lambda e: validarMascaraSubred())

# Botón para calcular
tk.Button(root, text="Calcular", command=validarMascaraSubred).pack(pady=20)

# Crear un contenedor con Canvas y Scrollbar para el área de resultados
resultado_frame = tk.Frame(root)
resultado_frame.pack(expand=True, fill=tk.BOTH)

canvas = tk.Canvas(resultado_frame)
scrollbar = tk.Scrollbar(resultado_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

# Configurar el Canvas y el Scrollbar para que se ajuste al contenido
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

# Empaquetar el Canvas y el Scrollbar
canvas.pack(side="left", expand=True, fill=tk.BOTH)
scrollbar.pack(side="right", fill=tk.Y)

# Crear el Label dentro del scrollable_frame para mostrar los resultados
resultado_text = tk.StringVar()
resultado_label = tk.Label(scrollable_frame, textvariable=resultado_text, justify="left", font=("Courier", 10), anchor="w")
resultado_label.pack(expand=True, fill=tk.BOTH)

# Ejecutar la aplicación
root.mainloop()
