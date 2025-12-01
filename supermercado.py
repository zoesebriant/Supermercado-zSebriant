import csv
import sys
from datetime import datetime

# --- CONFIGURACIÓN GLOBAL ---
SEPARADOR = ';'
INFORME_FILE = 'informe.txt'
MES_REPORTE = 10 
ANIO_REPORTE = 2010

# Carga productos.csv una sola vez
def _cargar_productos():
    """Carga productos.csv y devuelve {ID: {'nombre': str, 'precio': float, 'cant': int}}."""
    productos = {}
    try:
        with open('productos.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=SEPARADOR)
            next(reader) # Saltar encabezado
            
            for row in reader:
                if len(row) >= 4:
                    try:
                        productos[row[0]] = {
                            'nombre': row[1],
                            'precio': float(row[2]),
                            'cant': int(row[3])
                        }
                    except ValueError:
                        print(f"Advertencia: Fila de producto inválida o incompleta: {row}", file=sys.stderr)
    except FileNotFoundError:
        print("Error: No se encontró 'productos.csv'.", file=sys.stderr)
    return productos

# --- 1. Función: Producto Más Caro ---
def productoMasCaro(productos_data):
    """Encuentra el nombre del producto con el precio unitario más alto."""
    if not productos_data:
        return "N/A", 0.0

    # Encontrar el ID con el precio más alto
    id_max_precio = max(productos_data, key=lambda id: productos_data[id]['precio'])
    
    nombre = productos_data[id_max_precio]['nombre']
    precio = productos_data[id_max_precio]['precio']

    # Imprime el mensaje solicitado
    print(f"El producto más caro en el inventario es **{nombre}** con un precio de ${precio:,.2f}.")
    
    return nombre, precio

# --- 2. Función: Valor Total de la Bodega ---
def valorTotalBodega(productos_data):
    """Calcula el valor total del inventario: Sum(precio * cantidad_bodega)."""
    if not productos_data:
        return 0.0
    
    # Sumar (precio * cantidad) de todos los productos
    valor_total = sum(p['precio'] * p['cant'] for p in productos_data.values())
    
    return valor_total

# --- 3. Función: Producto con Más Ingresos ---
def productoConMasIngresos(productos_data):
    """Calcula el nombre del producto que ha generado la mayor cantidad de ingresos."""
    if not productos_data:
        return "N/A", 0.0
        
    ingresos_por_producto = {}
    try:
        with open('items.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=SEPARADOR)
            next(reader) # Saltar encabezado
            for row in reader:
                if len(row) >= 3:
                    id_p, cantidad = row[1], int(row[2])
                    
                    if id_p in productos_data:
                        ingreso = productos_data[id_p]['precio'] * cantidad
                        ingresos_por_producto[id_p] = ingresos_por_producto.get(id_p, 0) + ingreso
        
        if not ingresos_por_producto: 
            return "N/A", 0.0
            
        id_max = max(ingresos_por_producto, key=ingresos_por_producto.get)
        nombre_max = productos_data[id_max]['nombre']
        ingreso_max = ingresos_por_producto[id_max]
        
        return nombre_max, ingreso_max
    except FileNotFoundError:
        print("Error: No se encontró 'items.csv'.", file=sys.stderr)
        return "ERROR", 0.0
    except Exception as e:
        print(f"Error al procesar items.csv: {e}", file=sys.stderr)
        return "ERROR", 0.0

# --- 4. Función: Total de Ventas en un Período (Usando ventas.csv) ---
def totalVentasPeriodo(mes, anio):
    """Suma el campo 'venta' de ventas.csv que coincidan con el mes y año dados."""
    total_ventas = 0.0
    try:
        with open('ventas.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=SEPARADOR)
            next(reader) 
            for row in reader:
                if len(row) >= 3:
                    fecha_str = row[1].strip()
                    try:
                        monto_venta = float(row[2])
                        
                        # Intentar parsear fecha
                        if '/' in fecha_str:
                            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                        elif '-' in fecha_str:
                            try:
                                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                            except ValueError:
                                fecha_obj = datetime.strptime(fecha_str, '%d-%m-%Y')
                        else:
                            continue

                        if fecha_obj.month == mes and fecha_obj.year == anio:
                            total_ventas += monto_venta
                            
                    except ValueError:
                        continue # Ignorar filas con formato de número o fecha inválido
                        
        return total_ventas
    except FileNotFoundError:
        print("Error: No se encontró 'ventas.csv'.", file=sys.stderr)
        return 0.0
    except Exception as e:
        print(f"Error al procesar ventas.csv: {e}", file=sys.stderr)
        return 0.0

# ==========================================================
# --- PROGRAMA PRINCIPAL: Creación del Informe ---
# ==========================================================
def generar_informe_completo():
    """Llama a todas las funciones y escribe los resultados en informe.txt."""
    print("--- Iniciando el análisis de datos ---")
    
    # 1. Cargar datos base (productos.csv)
    productos_data = _cargar_productos()
    
    # 2. Ejecutar las funciones de análisis
    nombre_caro, _ = productoMasCaro(productos_data) 
    valor_bodega = valorTotalBodega(productos_data)
    nombre_ingresos, ingresos_total = productoConMasIngresos(productos_data)
    ventas_periodo = totalVentasPeriodo(MES_REPORTE, ANIO_REPORTE)
    
    # 3. Generar el contenido del informe
    lineas_informe = [
        "--- INFORME DE GESTIÓN SUPERMERCADO SOOS ---",
        "\n============================================\n",
        f"El producto más caro es **{nombre_caro}**.",
        f"El valor total de la bodega es de **${valor_bodega:,.2f}**.",
        f"El producto con más ingresos es **{nombre_ingresos}**.",
        f"En el período de **{MES_REPORTE:02d}/{ANIO_REPORTE}**, el total de ventas es de **${ventas_periodo:,.2f}**.",
        "\n============================================\n"
    ]

    # 4. Escribir el informe en el archivo
    try:
        with open(INFORME_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas_informe))
        
        return f"Informe generado con éxito. Se ha creado el archivo '{INFORME_FILE}'."
    except Exception as e:
        return f"Error al escribir el archivo de informe: {e}"

# --- Punto de entrada del programa ---
if __name__ == "__main__":
    print(generar_informe_completo())