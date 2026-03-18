2. Bot 2 : Le Coach CV (bot2.py)
Ce bot agit comme un consultant en recrutement pour optimiser une candidature précise.

Analyse de Match : Compare textuellement les compétences du CV avec les exigences de la fiche de poste.

Identification des "Gaps" : Liste ce qui manque ou ce qui n'est pas assez mis en avant pour le poste visé.

Reformulation IA : Propose des modifications concrètes (phrases à copier-coller) pour adapter le vocabulaire du CV aux mots-clés de l'offre.

Commandes : /setcv, /setfiche, /cv (analyse complète).

3. Bot 3 : Le Simulateur d'Entretien (bot3.py)
C'est le bot le plus complexe techniquement car il est "stateful" (il conserve la mémoire de l'échange).

Persona Dynamique : L'IA adopte le rôle d'un recruteur exigeant en se basant sur la fiche de poste fournie.

Mode Coaching Double : Le bot envoie un seul message contenant deux parties :

Le Recruteur : Pose la question suivante de manière naturelle.

Le Coach (Feedback) : Donne entre parenthèses un retour immédiat sur la qualité de votre réponse précédente.

Évaluation de Fin : La commande /stop déclenche un bilan pédagogique avec une note sur 10 et des axes de progression.

Commandes : /entretien (lance la boucle), /stop (bilan et reset).
