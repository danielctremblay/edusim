# EduSim — Un simulateur pour l'enseignement

EduSim est un simulateur d'environnements informationnels pour l'enseignement de compétences numériques auprès d'une clientèle universitaire. Le projet a été initié avec l'appui de la [Fabrique REL](https://fabriquerel.org) et du [Pôle régional en enseignement supérieur de l'Estrie (PRESE)](https://prese.ca).

Cette première version inclut :

* SchoolSim, un paquetage Python permettant de générer des données simples sur la réussite scolaire des élèves de niveau primaire. 



## SchoolSim : simulateur de la réussite scolaire

Le simulateur SchoolSim a été conçu pour illustrer la valeur des données numériques dans la gestion de la réussite scolaire des élèves du primaire. Le simulateur génère des données d'évaluation d'élèves sur une période temporelle de plusieurs années. Il peut être paramétré au moyen de tendances et de profils. Il produit une base de données décisionnelle (comptoir de données de modélisation OLAP) qui vient alimenter un tableau de bord de gestion de la réussite scolaire et une grille d'analyse soutenant le forage. 

Cette première version de SchoolSim est limitée au profil régulier d'élève.

La vision future de SchoolSim inclut :

* De nouveaux profils variés d'élèves (ex. TDAH, TSA, dyslexie, handicap)
* De nouveaux profils d'intervenants spécialiés (ex. orthophonie, travail social)
* La gestion de l'attribution des tâches des enseignants et des interventants au niveau de l'école et du centre de service scolaire, incluant les cas spéciaux comme le "looping"
* La gestion du milieu (ex. défavorisé)
* La gestion des absences des élèves et du personnel
* L'inclusion de classes multiniveaux
* La définition de cas limites (ex. nombre d'élèves par classe)
* L'inclusion d'autres types de données (ex. finances) pour la gestion d'école
* La réussite aux épreuves ministérielles
* La gestion d'école à vocation (ex. musique)
* L'adaptation du simulateur à la gestion du secondaire

L'objectif à terme est de fournir des environnements informationnels diversifiés pour soutenir le développement de compétences numériques de gestion des futures directions d'école.