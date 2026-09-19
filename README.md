<h1 align="center">
  pmu-server
</h1>

<p align="center">
  <strong>Pipeline de collecte et d'analyse des données hippiques PMU</strong>
</p>

<p align="center">
  Programmes, réunions, courses, partants, cotes et rapports — de l'API TurfInfo jusqu'à PostgreSQL, prêts pour l'exploration et la modélisation.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SQLModel-red" alt="SQLModel" />
  <img src="https://img.shields.io/badge/Alembic-migrations-black" alt="Alembic" />
</p>

Ce fichier README a été généré le 2026-09-19 par Cyril PERIE.

Dernière mise-à-jour le : 2026-09-19.

# INFORMATIONS GENERALES

## Titre du jeu de données

Archive hippique PMU (TurfInfo) : programmes, réunions, courses, partants, combinaisons de paris et rapports définitifs.

## DOI

Non attribué.

## Adresse de contact

cyril@cypit.dev

# INFORMATIONS METHODOLOGIQUES

## Conditions environnementales / experimentales

Il ne s'agit pas d'une expérimentation contrôlée. Les données sont **observationnelles** : elles décrivent l'activité hippique telle que publiée par le PMU.

Certaines conditions de course sont néanmoins capturées dans les payloads, lorsqu'elles sont renseignées par la source :

- météo de la réunion (nébulosité, température, vent) ;
- nature de la réunion et hippodrome ;
- type de piste, corde, parcours ;
- pénétromètre (intitulé et valeur mesurée, saisie manuelle côté PMU, virgule décimale d'origine).

Ces champs peuvent être absents ou tardifs selon l'hippodrome et le moment de la collecte.

## Description des sources et méthodes utilisées pour collecter et générer les données

**Source unique :** [API REST TurfInfo PMU](https://online.turfinfo.api.pmu.fr/rest/client/61/programme) (données déjà publiques). Projet indépendant, sans lien avec PMU.

**Périmètre temporel :** à partir du 1<sup>er</sup> janvier 2014 (`MIN_DATE = 01012014`).

**Collecte automatique** (orchestrée au démarrage de FastAPI, `scraper/orchestrator.py`) :

| Cadence | Pipeline | Ressources TurfInfo |
| --- | --- | --- |
| Tous les jours à 4 h (et une fois au démarrage) | `every_day` | programmes disponibles, réunions et courses, participants |
| Toutes les 5 minutes | `every_five_minutes` | combinaisons (cotes / enjeux) des courses **actives**, rapports définitifs des courses **terminées**, métriques |

**Client HTTP** (`pmu/client.py`) :

- timeout connect / lecture : 5 s / 15 s ;
- jusqu'à 3 tentatives, backoff exponentiel (plafond 8 s), respect de `Retry-After` ;
- retries sur `408`, `425`, `429`, `500`, `502`, `503`, `504` ;
- `404` → ressource absente, retour `None` (pas d'exception).

**Historisation** : `GET /scrap/historize?start_date=DDMMYYYY&end_date=DDMMYYYY` (ou `historize()` en Python) crée les programmes d'une période ; ils restent `is_scraped=False` jusqu'au passage des scrapers de courses et de partants.

Les identifiants repris de TurfInfo forment la clé primaire :

```text
programme     14072026
réunion       14072026/R1
course        14072026/R1/C3
participant   14072026/R1/C3/P7
combinaison   14072026/R1/C3-{updateTime}
rapport       14072026/R1/C3-{typePari}
```

Une course reste **active** (`is_over = false`) tant qu'elle n'est ni arrivée définitive, ni annulée (`COURSE_ANNULEE`), ni datée d'un jour passé. C'est ce sous-ensemble que le scraper de paris interroge toutes les 5 minutes.

## Méthodes de traitement des données

Aucune anonymisation : les données publiées (noms de chevaux, drivers, entraîneurs, etc.) sont conservées.

Traitements appliqués :

1. **Stockage brut** — le JSON TurfInfo est enregistré dans une colonne `raw` (PostgreSQL `json`). Les nœuds enfants déjà extraits ailleurs sont retirés du parent pour éviter la duplication (ex. `reunions` hors du programme, `courses` hors de la réunion).
2. **Normalisation relationnelle** — clés étrangères `programme → reunion → course → participant | combinaison | rapport`.
3. **Projection tabulaire** — les chargeurs `dataset/load_*.py` extraient des champs en SQL (`raw ->> …`) plutôt que d'aplatir tout le JSON en pandas. Filtre temporel commun : les 8 premiers caractères de `id` (`DDMMYYYY`), sans jointure.
4. **Conversions**
   - horodatages TurfInfo (millisecondes epoch) → timestamps UTC ;
   - `heure_depart_locale` = `heureDepart + timezoneOffset` (décalage de l'hippodrome) ;
   - pénétromètre : remplacement de `,` par `.` puis `float` ;
   - booléens absents : `coalesce(..., false)` sur plusieurs indicateurs ;
   - gains participants : **unité d'origine PMU (centimes d'euro)**, non convertis.
5. **Jeu de modélisation** (`load_jeu_modelisation`) — inner join partants × courses arrivées (`ARRIVEE_DEFINITIVE_COMPLETE`, `FIN_COURSE`, `ARRIVEE_DEFINITIVE`) × contexte de réunion. Les champs post-course (chrono, écart, réduction kilométrique) ne sont pas repris.

Les pipelines sont décorés (`@log_scraper`) : chaque exécution écrit une ligne dans `scraper_logs` (statut, durée, message et traceback en cas d'échec).

## Procédures d’assurance-qualité appliquées sur les données

- Journalisation de chaque scraper (`running` / `completed` / `failed`).
- Métriques de récupération recalculées toutes les 5 minutes : volumes (programmes, réunions, courses, partants, combinaisons), courses terminées vs à venir, moyennes, année minimale, taille de la base (`/metrics/recuperation`).
- Chargeurs de **couverture** (`load_couverture_courses`) et de **volumétrie** (`load_volumetrie`) pour vérifier qu'une course a bien des participants et des rapports.
- Pas de validation Pydantic systématique des payloads TurfInfo à l'ingestion (les types existent dans `pmu/types/api_types.py` mais ne sont pas encore appliqués en sortie du client).
- Upsert sur identifiant : une nouvelle collecte met à jour l'enregistrement existant.

Les données reflètent l'état TurfInfo **au moment du scrape**. Une cote live n'est pas interpolée entre deux relevés. Les combinaisons ne couvrent que les courses suivies en direct (pas tout l'historique).

## Autres informations contextuelles

Logiciels nécessaires pour lire et reproduire le jeu :

| Logiciel | Version |
| --- | --- |
| Python | 3.12 |
| PostgreSQL | (compatible SQLAlchemy 2 / JSON) |
| FastAPI | 0.139.2 |
| SQLModel | 0.0.39 |
| SQLAlchemy | 2.0.51 |
| Alembic | 1.19.0 |
| pandas | (chargeurs `dataset/`) |
| uvicorn | 0.51.0 |
| requests | 2.34.2 |
| pydantic | 2.13.4 |
| python-dotenv | 1.2.2 |
| psycopg2-binary | 2.9.10 |

Fichier `.env` à la racine :

```env
DATABASE_URL=postgresql://user:password@localhost:5432/pmu
```

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn server:app --reload
# sans scrapers :
python server.py dev
```

Le service écoute sur `http://0.0.0.0:8080`. `GET /health` → `{"message": "ok"}`.

Séparateur décimal dans les projections SQL / pandas : **point**. Dates d'identifiants : `DDMMYYYY`.

# APERCU DES DONNEES ET FICHIERS

Le jeu n'est pas diffusé comme un ensemble de fichiers plats : la source de vérité est **PostgreSQL**. Les DataFrames pandas sont des vues dérivées.

## Convention de nommage des fichiers

**Tables** : noms SQLModel au singulier (`programme`, `reunion`, `course`, `participant`, `combinaison`, `rapport`, `metrics`, `scraper_logs`).

**Identifiants métier** : préfixe date `DDMMYYYY`, puis `/R{n}`, `/C{n}`, `/P{n}` (voir ci-dessus).

**Chargeurs** : `dataset/load_{entité}.py`, fonction `load_{entité}(start_date, end_date)` sauf combinaisons (pas de fenêtre : la table n'existe que pour le suivi live).

**Notebooks** : `notebooks/00N_*.ipynb` (exploration, faisabilité de modélisation, marché en direct).

## Arborescence / plan de classement des fichiers

```text
pmu-server/
├── pmu/                 # client HTTP, endpoints, types TurfInfo
├── scraper/             # pipelines de récupération + orchestrateur
│   └── pipelines/recuperation/
├── models/              # tables SQLModel
├── service/             # accès base, CRUD, métriques
├── api/routes/          # FastAPI (scrap, metrics)
├── dataset/             # chargeurs SQL → pandas
├── notebooks/           # exploration et rapports
├── alembic/versions/    # migrations de schéma
├── requirements.txt
└── server.py
```

Relations :

```text
programme 1 ─── n reunion 1 ─── n course 1 ─── n participant
                                          ├── n combinaison
                                          └── n rapport
```

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : table `programme`

Une ligne par journée hippique. `raw` = payload programme **sans** le tableau `reunions`.

| Variable | Nom lisible | Description | Unité / format | Valeurs |
| --- | --- | --- | --- | --- |
| `id` | Identifiant programme | Date du programme | `DDMMYYYY` | à partir du 01012014 |
| `raw` | Payload brut | JSON TurfInfo du programme | JSON | structure `Programme` |
| `is_scraped` | Programme traité | Courses / réunions déjà extraites | booléen | `true` / `false` |
| `created_at` | Création | Premier insert | timestamp local applicatif | |
| `updated_at` | Mise à jour | Dernier upsert | timestamp | |

**Valeurs manquantes :** `NULL` SQL. Un programme historisé peut exister avec `is_scraped = false` tant que les courses n'ont pas été scrapées.

**Chargeur :** `load_programmes` → `model_dump()` des enregistrements (colonnes ci-dessus).

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : table `reunion`

Une ligne par réunion (hippodrome × jour). `raw` = payload réunion **sans** `courses`.

| Variable | Nom lisible | Description | Unité / format | Valeurs |
| --- | --- | --- | --- | --- |
| `id` | Identifiant réunion | `{programme}/R{numOfficiel}` | texte, max 14 | ex. `14072026/R1` |
| `programme_id` | Programme parent | FK vers `programme.id` | `DDMMYYYY` | |
| `raw` | Payload brut | JSON TurfInfo (hippodrome, pays, météo, nature, spécialités, …) | JSON | |
| `created_at` / `updated_at` | Horodatages internes | | timestamp | |

Champs utiles dans `raw` (non projetés par défaut, utilisés par `load_jeu_modelisation`) : `hippodrome.libelleLong`, `pays.libelle`, `nature`, `meteo.temperature`.

**Chargeur :** `load_reunions` → dump SQLModel.

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : table `course` / `load_courses`

Une ligne par épreuve. `raw` conserve le JSON course complet. Le chargeur projette :

| Variable | Nom lisible | Description | Unité / format | Valeurs / domaine |
| --- | --- | --- | --- | --- |
| `id` | Identifiant course | `{réunion}/C{numExterne}` | texte | ex. `14072026/R1/C3` |
| `reunion_id` | Réunion parente | FK | texte | |
| `programme_id` | Date programme | 8 premiers caractères de `id` | `DDMMYYYY` | |
| `date_programme` | Date du programme | | timestamp (date) | |
| `num_reunion` | N° de réunion | `numReunion` | entier | |
| `num_course` | N° de course | `numExterne` | entier | |
| `num_ordre` | Ordre dans la réunion | `numOrdre` | entier | |
| `libelle` | Nom de l'épreuve | | texte | |
| `discipline` | Discipline | | texte | valeurs TurfInfo |
| `specialite` | Spécialité | | texte | |
| `statut` | Statut de course | | texte | dont `ARRIVEE_DEFINITIVE`, `ARRIVEE_DEFINITIVE_COMPLETE`, `FIN_COURSE`, `COURSE_ANNULEE` |
| `categorie_statut` | Catégorie de statut | | texte | |
| `categorie_particularite` | Particularité | | texte | |
| `condition_age` | Condition d'âge | | texte | nullable |
| `condition_sexe` | Condition de sexe | | texte | nullable |
| `distance` | Distance | | entier (unité dans `distance_unite`) | |
| `distance_unite` | Unité de distance | | texte | souvent `m` |
| `corde` | Corde | | texte | |
| `type_piste` | Type de piste | | texte | |
| `parcours` | Parcours | | texte | |
| `montant_prix` | Allocation | | float, point décimal | unité PMU |
| `montant_total_offert` | Total offert | | float | |
| `montant_offert_premier` | Dotation du 1<sup>er</sup> | | float | |
| `nombre_declares_partants` | Partants déclarés | | entier | |
| `duree_course_ms` | Durée de l'épreuve | | float, ms | post-course, nullable |
| `heure_depart_utc` | Heure de départ UTC | epoch ms `heureDepart` | timestamp UTC | |
| `heure_depart_locale` | Heure locale hippodrome | `heureDepart + timezoneOffset` | timestamp | |
| `timezone_offset_ms` | Décalage hippodrome | | entier, ms | |
| `arrivee_definitive` | Arrivée homolaguée | | booléen | `false` si absent |
| `rapports_definitifs_disponibles` | Rapports dispo | | booléen | `false` si absent |
| `exclusive_internet` | Course internet | | booléen | |
| `pari_multi_courses` | Pari multi-courses | | booléen | |
| `replay_disponible` | Replay | | booléen | |
| `penetrometre_intitule` | Libellé pénétromètre | | texte | nullable |
| `penetrometre_valeur` | Mesure pénétromètre | virgule PMU → point | float | `NULL` si vide |
| `nombre_paris` | Paris ouverts | longueur de `raw.paris` | entier | |
| `nombre_places_arrivee` | Places à l'arrivée | longueur de `ordreArrivee` | entier | |
| `nombre_incidents` | Incidents | longueur de `incidents` | entier | |
| `is_over` | Course close côté serveur | plus suivie pour les cotes live | booléen | |
| `created_at` / `updated_at` | Horodatages internes | | timestamp | |

**Valeurs manquantes :** `NULL` / `NaN`. Booléens d'indicateurs : `false` si la clé TurfInfo est absente. L'hippodrome n'est **pas** sur la course : le lire sur la réunion.

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : table `participant` / `load_participants`

Une ligne par partant déclaré. Table la plus volumineuse. Gains laissés en **centimes**.

| Variable | Nom lisible | Description | Unité / format | Valeurs / domaine |
| --- | --- | --- | --- | --- |
| `id` | Identifiant partant | `{course}/P{numPmu}` | texte | |
| `course_id` | Course parente | FK | texte | |
| `programme_id` / `date_programme` | Programme | | `DDMMYYYY` / timestamp | |
| `num_pmu` | Numéro de dossard | `numPmu` | entier | |
| `nom` | Nom du cheval | | texte | |
| `statut` | Statut d'engagement | | texte | `PARTANT`, non-partants, etc. |
| `ordre_arrivee` | Place à l'arrivée | | entier | `NULL` avant l'arrivée |
| `incident` | Incident | | texte | nullable |
| `age` | Âge | | années, entier | |
| `sexe` | Sexe | | texte | |
| `race` | Race | | texte | |
| `allure` | Allure | | texte | |
| `robe` | Robe | `robe.libelleCourt` | texte | |
| `driver` | Driver / jockey | | texte | |
| `driver_change` | Changement de driver | | booléen | `false` si absent |
| `entraineur` | Entraîneur | | texte | |
| `proprietaire` | Propriétaire | | texte | |
| `eleveur` | Éleveur | | texte | |
| `nom_pere` / `nom_mere` | Pedigree | | texte | |
| `nombre_courses` | Courses en carrière | | entier | avant cette épreuve, selon source |
| `nombre_victoires` / `nombre_places` | Palmarès | | entier | |
| `gains_carriere` | Gains carrière | | float, **centimes** | |
| `gains_annee_en_cours` | Gains année | | float, centimes | |
| `gains_victoires` | Gains sur victoires | | float, centimes | |
| `cote_reference` | Rapport de référence | `dernierRapportReference.rapport` | float | nullable |
| `cote_directe` | Dernière cote live | `dernierRapportDirect.rapport` | float | snapshot à la collecte partants |
| `favori` | Marqué favori | | booléen | |
| `tendance_cote` | Tendance | `indicateurTendance` | texte | |
| `reduction_kilometrique` | Réduc. km | | entier | post-course, nullable |
| `temps_obtenu` | Chrono | | entier | post-course, nullable |
| `handicap_poids` | Poids handicap | | float | plat / obstacles, nullable |
| `handicap_distance` | Distance handicap | | entier | trot, nullable |
| `handicap_valeur` | Valeur handicap | | float | nullable |
| `place_corde` | Place à la corde | | entier | nullable |
| `ecart_cheval_precedent` | Écart | `distanceChevalPrecedent.identifiant` | texte | post-course |
| `deferre` | Deferrage | | texte | |
| `oeilleres` | Œillères | | texte | |
| `jument_pleine` | Jument pleine | | booléen | |
| `inedit` | Inédit | | booléen | |
| `engagement` | Engagement | | booléen | |
| `supplement` | Supplément | | float | |
| `musique` | Musique | formules de places récentes | texte | ex. `1a3a5a` |
| `avis_entraineur_present` | Avis entraîneur | présence de `avisEntraineur` | booléen | |
| `created_at` / `updated_at` | Horodatages | | timestamp | |

**Valeurs manquantes :** `NULL` pour les champs post-course tant que l'arrivée n'est pas connue. `statut != PARTANT` : cheval déclaré puis retiré / non-partant.

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : table `rapport` / `load_rapports` / `load_dividendes`

Un rapport = un couple (course, type de pari) **après** l'arrivée. Collecté lorsque la course passe `is_over`.

Types de paris (`pmu/types/enum.py`) : `E_SIMPLE_PLACE`, `E_SIMPLE_GAGNANT`, `SIMPLE_PLACE_INTERNATIONAL`, `SIMPLE_GAGNANT_INTERNATIONAL`, `E_COUPLE_PLACE`, `E_COUPLE_GAGNANT`, `E_COUPLE_ORDRE`, `E_TRIO`, `E_TRIO_ORDRE`, `E_SUPER_QUATRE`, `E_DEUX_SUR_QUATRE`, `E_MULTI`, `E_TIERCE`, `E_QUARTE_PLUS`, `E_QUINTE_PLUS`, `E_MINI_MULTI`, `E_PICK5`, `EB5`.

`load_rapports` — une ligne par rapport :

| Variable | Nom lisible | Description | Unité / format |
| --- | --- | --- | --- |
| `id` | Identifiant | `{course}-{typePari}` | texte |
| `course_id` | Course | FK | texte |
| `programme_id` / `date_programme` | Programme | | `DDMMYYYY` / timestamp |
| `type_pari` | Type de pari | | texte, enum ci-dessus |
| `famille_pari` | Famille | | texte |
| `audience` | Audience | | texte |
| `mise_base` | Mise de base | | float |
| `dividende_unite` | Unité du dividende | | texte |
| `rembourse` | Pari remboursé / annulé | | booléen, `false` si absent |
| `nombre_lignes` | Lignes de dividendes | | entier |
| `dividende_premier` | Dividende 1<sup>re</sup> ligne | pour 1 € | float |
| `gagnants_premier` | Gagnants 1<sup>re</sup> ligne | | float |
| `taille_combinaison` | Taille de la 1<sup>re</sup> combinaison | | entier |
| `dividende_min` / `dividende_max` | Étendue des dividendes | pour 1 € | float |
| `gagnants_total` | Somme des gagnants | | float |
| `created_at` / `updated_at` | Horodatages | | timestamp |

`load_dividendes` — une ligne par combinaison gagnante (défaut : `E_SIMPLE_GAGNANT`, `SIMPLE_GAGNANT`) : `rapport_id`, `position`, `libelle`, `dividende`, `dividende_pour_un_euro`, `nombre_gagnants`, `taille_combinaison`.

**Valeurs manquantes :** `NULL` si le tableau `rapports` est vide. `rembourse = true` : pas de jeu gagnant à exploiter.

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : table `combinaison` (marché en direct)

Photographies du marché **avant** l'arrivée, uniquement pour les courses suivies en live. Pas de fenêtre de dates sur les chargeurs.

`load_releves` — un enregistrement par instant × type de pari :

| Variable | Nom lisible | Description | Unité / format |
| --- | --- | --- | --- |
| `id` | Identifiant | `{course}-{updateTime}` | texte |
| `course_id` | Course | FK | texte |
| `date_programme` | Date | | date |
| `type_pari` | Type (`pariType`) | | texte |
| `masse` | Enjeu total du pari | `totalEnjeu` | float, unité PMU |
| `update_time` | Instant TurfInfo | epoch ms | entier |
| `instant` | Instant UTC | | timestamp UTC |
| `nombre_lignes` | Combinaisons listées | | entier |
| `created_at` | Insert local | | timestamp |

`load_marche_simple` — enjeux du **simple gagnant**, une ligne par cheval et par instant : `masse`, `enjeu` (part du cheval), `num_pmu`.

`load_arrivees_marche` / `load_courses_marche` : partants (`statut = PARTANT`) et cadre des courses pour lesquelles un relevé existe.

**Couverture incomplète :** la table n'existe pas pour l'historique non suivi en direct. Les cotes ne sont pas interpolées entre deux `updateTime`.

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : `load_jeu_modelisation`

Jeu d'étude (une ligne par partant de course **arrivée**). Inner join : participants `PARTANT` × courses au statut d'arrivée × hippodrome / pays / nature / température de la réunion.

Colonnes partant reprises : `id`, `course_id`, `date_programme`, `nom`, `num_pmu`, `statut`, `ordre_arrivee`, `incident`, `age`, `sexe`, `race`, `driver`, `driver_change`, `entraineur`, `nombre_courses`, `nombre_victoires`, `nombre_places`, `gains_carriere`, `cote_reference`, `cote_directe`, `favori`, `place_corde`, `handicap_*`, `deferre`, `oeilleres`, `inedit`, `musique`.

Colonnes épreuve / réunion : `discipline`, `specialite`, `statut_course`, `distance`, `nombre_partants`, `montant_prix`, `corde`, `type_piste`, `condition_sexe`, `penetrometre`, `hippodrome`, `pays`, `nature_reunion`, `temperature`.

**Non repris :** chrono, écart, réduction kilométrique (fuite d'information post-course).

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : `load_couverture_courses` et `load_volumetrie`

**Couverture** — index `course_id`, colonnes `participant` et `rapport` : nombre d'enregistrements filles. Un `NaN` après pivot = aucun enregistrement de cette entité.

**Volumétrie** — `entite` ∈ {`programme`, `reunion`, `course`, `participant`, `rapport`}, `date_programme`, `nombre`. Catégorie ordonnée dans cet ordre. Les combinaisons live ne sont pas dans cette union.

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : tables `metrics` et `scraper_logs`

Suivi opérationnel, pas le métier hippique.

`metrics` : `name` (PK), `value` (JSON), `category` (`recuperation` | `exploration`), `type` (`count` | `table`), horodatages.

`scraper_logs` : `id`, `status` (`running` | `completed` | `failed`), `scraper` (nom de fonction), `start_time`, `end_time`, `duration` (secondes, colonne calculée), `error_message`, `error_traceback`.

API : `GET /metrics/`, `GET /metrics/recuperation`, `GET /metrics/update`, `GET /scrap/historize`.
