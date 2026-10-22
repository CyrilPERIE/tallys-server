
from typing import List, Optional
from pydantic import BaseModel

'''
TODO: Tester les différents types de données.
'''
class Libelle(BaseModel):
    code: Optional[str] = None
    libelleCourt: str
    libelleLong: str


class TexteSource(BaseModel):
    source: str
    texte: str


class Traductible(BaseModel):
    text: str
    translate: str


class Media(BaseModel):
    heightSize: int
    originalSize: bool
    url: str
    widthSize: Optional[int] = None


class RapportCourse(BaseModel):
    dateRapport: int
    favoris: bool
    grossePrise: bool
    indicateurTendance: Optional[str] = None
    nomIndicateurTendance: Optional[str] = None
    numPmu1: int
    permutation: Optional[int] = None
    rapport: Optional[float] = None
    typePari: str
    typeRapport: str


Hippodrome = Libelle


class Pays(BaseModel):
    code: str
    libelle: str


class Cagnotte(BaseModel):
    cagnotteInternet: bool
    montant: float
    numCourse: int
    typePari: str


class GainParticipant(BaseModel):
    gainsAnneeEnCours: float
    gainsAnneePrecedente: float
    gainsCarriere: float
    gainsPlace: float
    gainsVictoires: float


class Pari(BaseModel):
    audience: str
    cagnotte: Optional[float] = None
    codePari: str
    combine: bool
    complement: bool
    enVente: bool
    misEnPaiement: Optional[bool] = None
    miseBase: float
    nbChevauxReglementaire: int
    ordre: bool
    poolId: Optional[str] = None
    reportable: bool
    spoteAutorise: Optional[bool] = None
    typePari: str

class ListeCombinaisons(BaseModel):
    combinaison: List[int]
    totalEnjeu: int

class Combinaison(BaseModel):
    listeCombinaisons: List[ListeCombinaisons]
    pariType: str
    totalEnjeu: int
    updateTime: int
    updateTimeOffset: int

class Meteo(BaseModel):
    compressed: bool
    date_prevision: int
    id: str
    nebulosite_code: str
    nebulosite_libelle_court: str
    nebulosite_libelle_court_en: str
    nebulosite_libelle_long: Traductible
    temperature: float
    vent_direction: Traductible
    vent_force: float


class PronosticsDetailles(BaseModel):
    class Crible(BaseModel):
        commentaire: str
        nom: str
        numPmu: int
        partant: bool

    commentaire: TexteSource
    cribles: List[Crible]
    quinte: bool


class RapportDefinitif(BaseModel):
    class Rapport(BaseModel):
        combinaison: List[int]
        dividende: float
        dividendePourUnEuro: float
        dividendePourUneMiseDeBase: float
        dividendeUnite: str
        libelle: str
        nombreGagnants: int

    audience: str
    dividendeUnite: str
    famillePari: str
    miseBase: float
    rapports: List[Rapport]
    rembourse: bool
    typePari: str


class RapportParticipant(BaseModel):
    age: int
    allure: str
    driver: str
    driverChange: bool
    engagement: bool
    entraineur: str
    favoris: bool
    grossePrise: bool
    handicapDistance: int
    incident: str
    indicateurInedit: bool
    jumentPleine: bool
    maxRapportProbable: float
    minRapportProbable: float
    musique: str
    nom: str
    nomMere: str
    nomPere: str
    nombreCourses: int
    nombrePlaces: int
    nombreVictoires: int
    numPmu: int
    numerosParticipant: List[int]
    oeilleres: str
    poidsConditionMonteChange: bool
    proprietaire: str
    race: str
    robe: Libelle
    sexe: str
    statu: str
    urlCasaque: str


class Participant(BaseModel):
    age: int
    allure: str
    avisEntraineur: Optional[str] = None
    commentaireApresCourse: Optional[TexteSource] = None
    dernierRapportDirect: Optional[RapportCourse] = None
    dernierRapportReference: Optional[RapportCourse] = None
    driver: str
    driverChange: bool
    engagement: bool
    entraineur: str
    gainsParticipant: GainParticipant
    handicapDistance: Optional[int] = None
    handicapPoids: Optional[int] = None
    indicateurInedit: bool
    jumentPleine: bool
    musique: Optional[str] = None
    nom: str
    nomMere: Optional[str] = None
    nomPere: str
    nomPereMere: Optional[str] = None
    nombreCourses: int
    nombrePlaces: int
    nombrePlacesSecond: int
    nombrePlacesTroisieme: int
    nombreVictoires: int
    numPmu: int
    oeilleres: str
    ordreArrivee: Optional[int] = None
    placeCorde: Optional[int] = None
    poidsConditionMonteChange: bool
    proprietaire: str
    race: str
    reductionKilometrique: Optional[float] = None
    robe: Optional[Libelle] = None
    sexe: str
    statut: str
    supplement: int
    tempsObtenu: Optional[float] = None
    urlCasaque: str

class Incident(BaseModel):
        numeroParticipants: List[int]
        type: str
        
class Course(BaseModel):
    arriveeDefinitive: Optional[bool] = None
    cached: bool
    cagnottes: List[Cagnotte]
    categorieParticularite: str
    categorieStatut: str
    conditionAge: Optional[str] = None
    conditionSexe: Optional[str] = None
    conditions: str
    corde: str
    courseExclusiveInternet: bool
    courseTrackee: bool
    departImminent: bool
    discipline: str
    distance: float
    distanceUnit: str
    dureeCourse: Optional[int] = None
    ecuries: List[dict] = []
    epcPourTousParis: bool
    formuleChampLibreIndisponible: Optional[bool] = None
    grandPrixNationalTrot: bool
    hasEParis: bool
    heureDepart: int
    hippodrome: Hippodrome
    incidents: Optional[List[Incident]] = None
    isArriveeDefinitive: Optional[bool] = None
    isDepartAJPlusUn: bool
    isDepartImminent: bool
    libelle: str
    libelleCourt: str
    montantOffert1er: float
    montantOffert2eme: float
    montantOffert3eme: float
    montantOffert4eme: float
    montantOffert5eme: float
    montantPrix: float
    montantTotalOffert: float
    nombreDeclaresPartants: int
    numCourseDedoublee: int
    numExterne: int
    numExterneReunion: int
    numOrdre: int
    numReunion: int
    numSocieteMere: int
    ordreArrivee: Optional[List[List[int]]] = None
    parcours: str
    pariMultiCourses: bool
    pariSpecial: bool
    paris: List[Pari]
    participants: List[Participant] = []
    photosArrivee: Optional[List[Media]] = None
    poolIds: Optional[List[dict]] = None
    pronosticsExpires: bool
    rapportsDefinitifsDisponibles: Optional[bool] = None
    replayDisponible: bool
    specialite: str
    statut: str
    timezoneOffset: int
    typePiste: str


class Rapport(BaseModel):
    dateMajDirect: int
    dateMajDirectOffset: int
    dateProgramme: int
    dateProgrammeOffset: int
    nbParticipants: int
    numCourse: int
    numReunion: int
    rapportParticipants: List[RapportParticipant]
    rapportsEcurie: List[dict]
    spriteCasaques: List[Media]
    totalEnjeu: float
    typePari: str


class Pronostics(BaseModel):
    class Selection(BaseModel):
        cote_prob: str
        id_nav_partant: int
        num_partant: int
        rang: int

    class PronoPmuFr(BaseModel):
        chapeau: Traductible
        selection: List["Pronostics.Selection"]

    class PresentationCourse(BaseModel):
        translate: str

    compressed: bool
    dateReunion: str
    id: str
    id_nav_course: int
    nom_prix: str
    np_partants: int
    num_course_pmu: int
    numeroCourse: int
    numeroReunion: int
    pronostics: dict
    source: str


class Reunion(BaseModel):
    audience: str
    cached: bool
    courses: List[Course]
    dateReunion: int
    datesProgrammesDisponibles: List[str]
    derniereReunion: bool
    disciplinesMere: List[str]
    hippodrome: Hippodrome
    meteo: dict
    nature: str
    numExterne: int
    numOfficiel: int
    numOfficielReunionPrecedente: Optional[int] = None
    numOfficielReunionSuivante: Optional[int] = None
    offsetInternet: bool
    parisEvenement: List[dict]
    pays: Pays
    prochaineCourse: int
    prochainesCoursesAPartir: List[dict]
    specialites: List[str]
    statut: str
    timezoneOffset: int


class Programme(BaseModel):
    cached: bool
    date: int
    dateProgrammeActif: int
    datesProgrammesDisponibles: List[str]
    prochainesCoursesAPartir: dict
    reunions: List[Reunion]
    timezoneOffset: int

class ParticipantsResponse(BaseModel):
    participants: List[Participant]
    ecuries: List[dict]
    spriteCasaques: List[Media]
    cached: bool

class CombinaisonResponse(BaseModel):
    dateProgramme: int
    timezoneOffset: int
    numeroReunion: int
    numeroCourse: int
    combinaisons: List[Combinaison]

class ProgrammeResponse(BaseModel):
    programme: Programme