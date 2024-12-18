# -*- coding: utf-8 -*-
"""Lab2_IA_SanMartin.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LQd7HDnRu6DXox4r1T9_p9QuIpGF1s4W

#Lab 2 Inteligencia Artificial

Autora: Valentina San Martín

Estructura del Pipeline:

1. Definición del problema
2. Recolección y preprocesamiento de datos
    * Análisis exploratorio de datos (EDA)
    * Escalado de características e Imputación de datos
    * Reducción de dimensionalidad
3. Entrenamiento de modelos
4. Evaluación de modelos
    * Entrenamiento-Validación-Prueba
    * Validación cruzada (Cross-Validation)

#1. Definición del problema

Para el siguiente Laboratorio se escogió un dataset de Our World In Data (específicamente en la sección Health -> Burden of Disease https://ourworldindata.org/grapher/life-expectancy-vs-expected-years-lived-with-disability ). Este dataset muestra la relación entre la esperanza de vida promedio (Average Life Expectancy) y la cantidad de años que se espera que una persona viva con una pérdida de salud (enfermedad o discapacidad) ya sea a corto o a largo plazo (Expected years lived with disability or disease). Este dataset incluye además de las variables mencionadas previamente, el año de cada registro (entre 1990 y 2016), el país, el continente, población (estimado histórico) y un código del país.

Este lab busca encontrar una tendencia entre la esperanza de vida promedio (Average Life Expectancy) y la cantidad de años que se espera que una persona viva con una enfermedad o discapacidad y compararlo con otras características para evaluar la posible razón de esta tendencia. Para esto se utilizará el algoritmo de clusterización K-Means.

#2. Recolección y preprocesamiento de datos

Priimero que todo se deben importar las librerías necesarias:

pandas y numpy para manipulación de datos y operaciones numéricas.
matplotlib.pyplot y seaborn para visualización de datos.
Módulos sklearn para preprocesamiento de datos (escalado, imputación), agrupación (KMeans, DBSCAN), evaluación de modelos (puntuación de silueta) y división de datos.
"""

# Importar librerías necesarias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, MiniBatchKMeans
from sklearn.metrics import silhouette_score, make_scorer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, cross_val_score

"""Dado que el dataset tiene 59.110 registros, se leerá el conjunto de datos en fragmentos de 10.000 filas para manejar archivos grandes de manera eficiente. Luego concatena estos fragmentos en un único dato de DataFrame."""

# Leer el conjunto de datos por lotes
chunksize = 10000
data = pd.DataFrame()
for chunk in pd.read_csv('life-expectancy-vs-expected-years-lived-with-disability.csv', chunksize=chunksize):
    data = pd.concat([data, chunk], ignore_index=True)

"""Luego se deben extraer las dos principales variables de interés y eliminar filas con valores faltantes en estas variables.
Además se escalan los datos utilizando StandardScaler para normalizar los valores, lo cual es importante para muchos algoritmos de aprendizaje automático.
Esta parte imputa los valores faltantes en columnas numéricas con la media, lo que puede ser útil para otros análisis que no se muestran en este código.
"""

# Extracción de columnas relevantes
X = data[['Years lived with disability', 'Life Expectancy (IHME)', ]]

# Escalado de Características
processed_data = data.dropna(subset=["Years lived with disability", "Life Expectancy (IHME)"])
scaler = StandardScaler()
scaled_data = scaler.fit_transform(processed_data[["Years lived with disability", "Life Expectancy (IHME)"]])

# Imputación de datos faltantes
numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
data_numeric = data[numeric_cols]
imputer = SimpleImputer(strategy='mean')
data_imputed = pd.DataFrame(imputer.fit_transform(data_numeric), columns=numeric_cols)

# Exploración de la base de datos
print(data.head())
print(data.info())
print(data.describe())

# Exploratory Data Analysis (EDA)
# Gráficos univariados
plt.figure(figsize=(16, 6))
for i, col in enumerate(data.select_dtypes(include=['float64', 'int64']).columns):
    plt.subplot(2, 4, i+1)
    sns.histplot(data[col], kde=True)
    plt.title(col)
plt.tight_layout()
plt.show()

# Gráficos multivariados
sns.pairplot(data.select_dtypes(include=['float64', 'int64']))
plt.show()

print("Exploratory Data Analysis:")
print(data.describe())
print(data.info())

"""#3. Entrenamiento de Modelos"""

# División de los datos (Split) en conjuntos de datos de entrenamiento, de validación y de prueba
X_train, X_test, y_train, y_test = train_test_split(scaled_data, processed_data['Continent'], test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=42)

init_strategies = ['k-means++', 'random', 'MiniBatchKMeans']
for strategy in init_strategies:
    if strategy == 'MiniBatchKMeans':
        kmeans = MiniBatchKMeans(n_clusters=3, init='k-means++', random_state=42)
    else:
        kmeans = KMeans(n_clusters=3, init=strategy, random_state=42)
    kmeans.fit(X_train)
    print(f"Inercia de la estrategia de inicialización {strategy} : {kmeans.inertia_}")

    # Visualización de clusters por cada estrategia de inicialización en gráficos de dispersión (scatter plot)
    plt.figure(figsize=(8, 6))
    plt.scatter(X_train[:, 0], X_train[:, 1], c=kmeans.labels_, cmap='viridis')
    plt.title(f'Clusters de la estrategia de inicialización {strategy} ')
    plt.xlabel('Años vividos con discapacidad o enfermedad')
    plt.ylabel('Esperanza de Vida (IHME)')
    plt.show()

print("\nComparación de DBSCAN según sus hiperparámetros:")
#Hiperparámetros:
epsilon_values = [0.5, 1.0, 1.5]
min_samples_values = [5, 10, 15]
for eps in epsilon_values:
    for min_samples in min_samples_values:
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        dbscan_clusters = dbscan.fit_predict(X_train)
        print(f"Epsilon: {eps}, min_samples: {min_samples}, Número de clusters: {len(set(dbscan_clusters)) - (1 if -1 in dbscan_clusters else 0)}")

        # Visualización de clusters por cada hiperparámetro en gráficos de dispersión (scatter plot)
        plt.figure(figsize=(8, 6))
        plt.scatter(X_train[:, 0], X_train[:, 1], c=dbscan_clusters, cmap='viridis')
        plt.title(f'Clusters de DBSCAN con hiperparámetros eps={eps}, min_samples={min_samples}')
        plt.xlabel('Años vividos con discapacidad o enfermedad')
        plt.ylabel('Esperanza de Vida (IHME)')
        plt.show()

"""#4. Evaluación de Modelos

##K-Means
"""

# Gráfico de Inercia vs clusters (K) para el algoritmo K-Means
print("\nGráfico de Inercia vs K para K-Means:")
inertias = []
k_values = range(2, 11)
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_train)
    inertias.append(kmeans.inertia_)

plt.figure(figsize=(8, 6))
plt.plot(k_values, inertias, 'bo-')
plt.title('Regla del Codo para una K óptima')
plt.xlabel('Número of clusters (K)')
plt.ylabel('Inercia')
plt.xticks(k_values)
plt.show()

# Gráfico de Silhouette score vs K para K-Means
print("\nGráfico de Silhouette score vs K para K-Means:")
silhouette_scores = []
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans_clusters = kmeans.fit_predict(X_train)
    silhouette_scores.append(silhouette_score(X_train, kmeans_clusters))

plt.figure(figsize=(8, 6))
plt.plot(k_values, silhouette_scores, 'bo-')
plt.title('Análisis de silueta (Silhouette) para una K óptima')
plt.xlabel('Número de Clusters (K)')
plt.ylabel('Silhouette Score')
plt.xticks(k_values)
plt.show()

"""Según el gráfico de Inercia y Número de Clústers y utilizando la regla del codo (Elbow Rule), el número de clústers que se debería utilizar es 4, ya que es en este punto donde se minimiza la recta.

##Validación cruzada (Cross-Validation)
"""

def silhouette_scorer(estimator, X):
    cluster_labels = estimator.fit_predict(X)
    if len(set(cluster_labels)) == 1:
        return 0
    return silhouette_score(X, cluster_labels)

"""##Conclusiones

Los clústeres al compararlos con los continentes de dónde provienen los datos, se puede observar una tendencia por países africanos a estar más minimizados por decirlo así, por países asiáticos a estar al medio y a norteamérica por estar más maximizado
"""

# Gráfico de dispersión con puntos coloreados por continente
print("\nGráfico de dispersión con puntos coloreados por continente:")
continents = data["Continent"].dropna().unique()
colors = ["r", "g", "b", "c", "m", "y", "k"]

plt.figure(figsize=(10, 6))
for continent, color in zip(continents, colors):
    continent_data = data[data["Continent"] == continent]
    plt.scatter(continent_data["Years lived with disability"], continent_data["Life Expectancy (IHME)"],
                color=color, label=continent, s=50, alpha=0.5)

plt.title("Gráfico de dispersión por Continente")
plt.xlabel('Años vividos con discapacidad o enfermedad')
plt.ylabel('Esperanza de Vida (IHME)')
plt.legend()
plt.show()