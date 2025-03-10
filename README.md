# Transaction Processing Pipeline

## Description

Ce projet est un pipeline de traitement de données bancaires développé avec **Apache Airflow**. Le pipeline effectue plusieurs étapes de transformation sur un jeu de données de transactions bancaires en CSV, telles que :

1. **Lecture et prétraitement des données** : Lecture d'un fichier CSV, nettoyage des données en supprimant les valeurs nulles.
2. **Filtrage des données par localisation** : Filtrage des transactions en fonction d'une localisation donnée (par exemple, San Diego).
3. **Grouper les données par type de transaction** : Agréger les données en fonction du type de transaction, en calculant la moyenne de l'âge des clients et la somme des montants des transactions.
4. **Branches conditionnelles** : Le flux de travail est conditionnel, ce qui permet d'exécuter soit un filtrage, soit un regroupement des données en fonction d'une variable définie.

## Fonctionnalités

- **Lecture du fichier CSV** : Le fichier CSV contenant les données des transactions bancaires est lu à partir d'un chemin relatif.
- **Transformation des données** : En fonction de la variable définie dans Airflow, les données peuvent être filtrées ou regroupées.
- **Gestion des erreurs** : Des vérifications sont effectuées pour s'assurer que les colonnes nécessaires existent dans le dataset avant d'effectuer des opérations.

## Prérequis

Avant d'exécuter ce projet, assure-toi que tu as les éléments suivants installés sur ta machine :

- **Python 3.x** : Le projet utilise Python 3.9+.
- **Airflow** : Tu peux installer Airflow via `pip` (voir instructions ci-dessous).
- **Pandas** : Pour la manipulation des données.
- **Autres dépendances** : Les autres dépendances sont gérées par Airflow.

### Installation

1. Clone ce projet sur ton ordinateur :
   ```bash
   git clone https://github.com/sakounta/ETL_ApacheAirflow.git
   cd transaction-processing-pipeline

