# Guía Rápida de Scikit-Learn

## Importaciones comunes

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
```

## División train/test

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,    # 20% para test
    random_state=42   # Reproducibilidad
)
```

## Modelos de Clasificación

### Decision Tree
```python
from sklearn.tree import DecisionTreeClassifier

modelo = DecisionTreeClassifier(max_depth=5)
modelo.fit(X_train, y_train)
predicciones = modelo.predict(X_test)
```

### Random Forest
```python
from sklearn.ensemble import RandomForestClassifier

modelo = RandomForestClassifier(n_estimators=100)
modelo.fit(X_train, y_train)
predicciones = modelo.predict(X_test)
```

### SVM
```python
from sklearn.svm import SVC

modelo = SVC(kernel='rbf')
modelo.fit(X_train, y_train)
predicciones = modelo.predict(X_test)
```

## Evaluación

```python
# Precisión
accuracy = accuracy_score(y_test, predicciones)
print(f"Accuracy: {accuracy:.2%}")

# Matriz de confusión
cm = confusion_matrix(y_test, predicciones)
print(cm)

# Reporte completo
print(classification_report(y_test, predicciones))
```

## Pipeline

```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier())
])

pipeline.fit(X_train, y_train)
predicciones = pipeline.predict(X_test)
```
