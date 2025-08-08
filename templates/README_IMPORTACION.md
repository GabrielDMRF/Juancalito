# Plantillas Excel para Importación

Este directorio contiene plantillas Excel para importar productos a cada tipo de inventario.

## Archivos Disponibles:

### 1. plantilla_quimicos.xlsx
**Columnas requeridas:**
- codigo: Código único del producto
- nombre: Nombre del producto químico
- clase: Tipo de químico (Fertilizante, Herbicida, Fungicida, etc.)
- saldo: Cantidad en stock
- unidad: Unidad de medida (Kg, L, etc.)
- valor_unitario: Precio por unidad

**Columnas opcionales:**
- descripcion: Descripción del producto
- stock_minimo: Stock mínimo para alertas
- ubicacion: Ubicación en almacén
- proveedor: Nombre del proveedor
- fecha_vencimiento: Fecha de vencimiento (YYYY-MM-DD)
- lote: Número de lote

### 2. plantilla_almacen.xlsx
**Columnas requeridas:**
- codigo: Código único del producto
- nombre: Nombre del producto
- categoria: Categoría del producto
- saldo: Cantidad en stock
- unidad: Unidad de medida
- valor_unitario: Precio por unidad

**Columnas opcionales:**
- descripcion: Descripción del producto
- stock_minimo: Stock mínimo para alertas
- ubicacion: Ubicación en almacén
- proveedor: Nombre del proveedor

### 3. plantilla_poscosecha.xlsx
**Columnas requeridas:**
- codigo: Código único del producto
- nombre: Nombre del producto
- tipo: Tipo de producto
- saldo: Cantidad en stock
- unidad: Unidad de medida
- valor_unitario: Precio por unidad

**Columnas opcionales:**
- descripcion: Descripción del producto
- stock_minimo: Stock mínimo para alertas
- ubicacion: Ubicación en almacén
- proveedor: Nombre del proveedor

## Instrucciones de Uso:

1. Descargue la plantilla correspondiente al tipo de inventario
2. Complete los datos en las columnas requeridas
3. Guarde el archivo Excel
4. En el sistema, vaya al inventario correspondiente
5. Haga clic en "Importar Excel"
6. Seleccione el archivo Excel completado
7. Confirme la importación

## Notas Importantes:

- Los códigos deben ser únicos
- Las fechas deben estar en formato YYYY-MM-DD
- Los valores numéricos no deben incluir símbolos de moneda
- El archivo debe estar en formato .xlsx o .xls
