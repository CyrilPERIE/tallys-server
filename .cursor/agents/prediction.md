Cette approche sera la même pour les différents modèles, l'idée est d'industrialiser pour facilement pouvoir réaliser plusieurs tests.

La pipeline imaginée est 

1. Création du dataset (2025 entrainement, 2026 simulation)
2. Entrainement du modèle/statistiques/tir au sort...
3. Enregistrement du modèle (si c'est un modèle)
4. Création de metrics associés au modèle entrainé/statistiques/tir au sort, ces metrics seront réalisées sur 2026
5. Création d'un fonction qui prend un id de course en entrée et qui ressort les prédictions en chargeant le modèle...
6. Réadaction dans le readme de l'approche réalisée dans le cadre du modèle/statistiques/tir au sort...


Pour ce faire chaque approche est stockée dans un dossier

README.md --> Stockage de l'intuition et description de l'approche
dataset.py --> la fonction qui permet de livrer les données nécessaires à l'entrainement et validation du modèles...
predict.py --> la fonction qui charge le modèle et renvoie une prédiction en prenant en entrée l'id d'une course
train.py --> la fonction d'entrainement

