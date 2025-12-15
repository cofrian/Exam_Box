# Guía Rápida de Matplotlib

## Importar

```python
import matplotlib.pyplot as plt
import numpy as np
```

## Gráfico de líneas

```python
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

plt.plot(x, y)
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.title('Mi gráfico')
plt.show()
```

## Gráfico de barras

```python
categorias = ['A', 'B', 'C']
valores = [10, 20, 15]

plt.bar(categorias, valores)
plt.title('Ventas por categoría')
plt.show()
```

## Histograma

```python
datos = np.random.randn(1000)
plt.hist(datos, bins=30)
plt.title('Distribución')
plt.show()
```

## Scatter plot

```python
x = np.random.randn(100)
y = np.random.randn(100)

plt.scatter(x, y, alpha=0.5)
plt.xlabel('X')
plt.ylabel('Y')
plt.show()
```

## Subplots

```python
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

axes[0].plot(x, y)
axes[0].set_title('Gráfico 1')

axes[1].bar(categorias, valores)
axes[1].set_title('Gráfico 2')

plt.tight_layout()
plt.show()
```

## Guardar figura

```python
plt.savefig('grafico.png', dpi=150)
```
