# Guía Rápida de Pandas

## Cargar datos

```python
import pandas as pd

# Desde CSV
df = pd.read_csv('archivo.csv')

# Desde Excel
df = pd.read_excel('archivo.xlsx')
```

## Exploración básica

```python
df.head()        # Primeras 5 filas
df.tail()        # Últimas 5 filas
df.info()        # Información del DataFrame
df.describe()    # Estadísticas descriptivas
df.shape         # (filas, columnas)
df.columns       # Lista de columnas
```

## Selección de datos

```python
# Columna
df['columna']
df[['col1', 'col2']]

# Filas
df.iloc[0]       # Por índice
df.loc[0]        # Por etiqueta

# Filtros
df[df['precio'] > 100]
df[(df['precio'] > 100) & (df['categoria'] == 'A')]
```

## Operaciones

```python
df['columna'].mean()    # Media
df['columna'].sum()     # Suma
df['columna'].count()   # Conteo
df['columna'].max()     # Máximo
df['columna'].min()     # Mínimo
```

## Agrupaciones

```python
df.groupby('categoria')['precio'].mean()
df.groupby(['cat1', 'cat2']).agg({'col': 'sum'})
```
