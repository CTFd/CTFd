# Règlement officiel — NCTF26

**NCTF26** — Capture The Flag national de cybersécurité du Togo, organisé par le
**CERT.tg**. Présélection en ligne du **vendredi 23 octobre 19:00** au **lundi
26 octobre 00:00** (heure de Lomé, GMT). Finale sur place à **Lomé les 29–30
octobre**.

> En vous inscrivant, chaque membre accepte ce règlement au nom de
> son équipe.

---

## 1. Objet et esprit

NCTF26 est une compétition **par équipes**. Chaque équipe résout les épreuves
**par ses propres moyens**, avec les seules informations mises à sa disposition
par les organisateurs et ses propres connaissances. Le classement n'a de valeur
que si cette règle est respectée par tout le monde. Le CTF vise à révéler et
faire progresser les talents togolais en cybersécurité, dans un esprit de fair-play.

## 2. Éligibilité et inscription

- La présélection est **ouverte** ; les conditions d'éligibilité à la finale
  (nationalité, âge, statut) sont précisées dans l'appel à participation et
  priment en cas de doute.
- On concourt en **équipe**. La taille maximale d'équipe est fixée par
  l'organisation et affichée à l'inscription ; elle est identique pour toutes.
- **Un seul compte par personne, une seule équipe par personne.** Créer plusieurs
  comptes, appartenir à plusieurs équipes ou concourir sous une fausse identité
  est interdit.
- Les informations d'inscription doivent être exactes. L'organisation peut
  demander une pièce justificative avant la finale.

## 3. Déroulement et format

- **Présélection** : en ligne, **du vendredi 23 octobre 19:00 au lundi 26 octobre
  00:00** (GMT/Lomé), soit 53 h non-stop. Les épreuves sont de type _jeopardy_
  (catégories : web, pwn, reverse, crypto, forensics, cloud, blockchain, IA/ML,
  OSINT, et autres) réparties sur plusieurs niveaux de difficulté, plus des
  épreuves **King of the Hill**.
- **Finale** : à Lomé les **29–30 octobre**, sur invitation des meilleures équipes
  de la présélection. Le classement de la finale **repart de zéro**.
- Chaque épreuve résolue rapporte des points ; certaines épreuves ont un score
  **dynamique** (la valeur baisse avec le nombre de résolutions). Le classement
  est au total de points, départage au **temps** de la dernière résolution utile.
- Le **scoreboard public** peut être **gelé** la dernière heure (les scores
  continuent de compter, seul l'affichage public est figé) pour ménager le
  suspense. L'organisation voit le classement en direct.

## 4. Indices, King of the Hill, épreuves à instance

- Des **indices** payants (en points) peuvent être proposés sur certaines
  épreuves ; les prendre est un choix d'équipe, sans pénalité autre que le coût.
- Les épreuves **King of the Hill** (collines partagées) attribuent des points
  **tant qu'une équipe tient la colline**, à chaque passage de scoring. Sur les
  collines _boot2root_, un maintien au niveau **utilisateur** rapporte **la moitié**
  des points d'un maintien **root**. Tenir une colline est un jeu ouvert : rien
  n'y est « volé » à une autre équipe.
- Les épreuves **à instance par équipe** fournissent à chaque équipe son propre
  conteneur et son **propre flag**. Ce flag n'est valable que pour l'équipe à qui
  il a été délivré.

## 5. Intégrité — partage de flags (disqualification)

**Transmettre un flag, ou une partie de solution qui revient à donner le flag, à
une autre équipe est interdit.** Recevoir et soumettre un flag obtenu d'une autre
équipe l'est tout autant, quelle que soit la façon dont il a circulé (message,
capture d'écran, compte partagé, poste partagé).

**Sanction : disqualification des deux équipes concernées**, celle qui donne et
celle qui reçoit, dès la première infraction établie. Il n'y a pas
d'avertissement préalable pour cette infraction. Les scores sont retirés du
classement, la qualification pour la finale est annulée, et l'incident est
consigné.

## 6. Les journaux font foi

La plateforme enregistre, pour chaque soumission et chaque validation, le compte,
l'équipe, l'heure à la seconde, l'adresse IP et la valeur soumise. Ces journaux
sont conservés et **constituent la preuve** en cas de litige :

- une équipe qui soumet le flag personnel d'une autre équipe (les flags des
  épreuves à instance sont différents pour chaque équipe) est identifiée sans
  ambiguïté, avec l'heure, l'adresse et l'équipe d'origine ;
- pour les épreuves dont le flag est commun, la répétition de validations
  simultanées entre deux équipes, l'ordre systématique de ces validations et
  l'usage d'adresses communes sont rapprochés après coup.

Une **coïncidence isolée n'est pas une infraction** ; une répétition l'est. Le
jury examine ces éléments et **entend les équipes concernées** avant de décider.

## 7. Périmètre technique et comportements interdits

Sont **interdits**, et exposent à sanction :

- Attaquer l'**infrastructure** de la compétition (plateforme de scoring, comptes,
  réseau, autres équipes) **hors du périmètre explicite** d'une épreuve. Seuls les
  services désignés par une épreuve sont dans le périmètre.
- Le **déni de service** sur une épreuve partagée, ou toute action qui dégrade
  l'expérience des autres équipes.
- Le **bruteforce** de flags : la plateforme limite le rythme des soumissions ;
  chercher à contourner cette limite est une infraction.
- L'usage de **plusieurs comptes** ou l'appartenance à **plusieurs équipes**.
- La **publication de solutions** (write-ups, flags, indices) avant la clôture
  officielle.
- Toute tentative d'accès aux flags ou aux ressources d'une épreuve **par un canal
  autre que l'exploitation prévue** (accès au dépôt, à l'infrastructure de build,
  fuite hors compétition).

Sanction : **avertissement**, puis **disqualification** en cas de récidive ;
**disqualification immédiate** si l'infraction a affecté d'autres équipes ou
l'infrastructure.

## 8. Données personnelles et journalisation

- L'organisation collecte les données d'inscription (identité, contact, équipe) et
  les **journaux d'activité** (soumissions, connexions, adresses IP ; en finale,
  éventuellement les prompts envoyés aux épreuves d'IA). Ces données servent
  **exclusivement** à la conduite de la compétition, au classement, à la lutte
  contre la triche et à l'amélioration des éditions suivantes.
- Elles sont conservées le temps nécessaire au règlement des litiges et aux
  besoins statistiques, puis supprimées ou anonymisées. Les comptes joueurs sont
  supprimés entre deux éditions.
- Une équipe peut demander la **communication des éléments qui la concernent** dans
  le cadre d'un litige. Pour toute question sur ses données, contacter le CERT.tg
  par le canal officiel.

## 9. Communication et support

- Les échanges officiels (annonces, questions, incidents) passent par le **canal
  officiel** indiqué à l'inscription. Aucune décision ne se prend par un autre
  canal.
- Les organisateurs peuvent publier des **annonces** en cours d'épreuve (correctif,
  indice global, prolongation). Elles font partie du règlement dès leur
  publication.

## 10. Jury, sanctions et recours

- Les décisions (validation d'une infraction, sanction, classement) sont prises
  par le **jury de l'organisation**, à partir des journaux et **après avoir entendu
  l'équipe**.
- Barème indicatif : avertissement, retrait de points, disqualification d'une
  épreuve, disqualification de l'édition, selon la gravité et la récidive. Le
  partage de flags (art. 5) entraîne la disqualification directe des deux équipes.
- La décision du jury est **définitive** pour le classement de l'édition. Une
  équipe peut demander la communication des éléments qui la concernent.

## 11. Dispositions finales

- L'organisation peut **ajuster** le calendrier, la liste des épreuves ou les
  paramètres (fenêtres, quotas, taille d'équipe) pour raisons techniques ou de
  sécurité ; les changements sont annoncés sur le canal officiel.
- En cas d'incident majeur (panne, indisponibilité prolongée), l'organisation peut
  **prolonger, suspendre ou neutraliser** tout ou partie d'une épreuve, dans un
  souci d'équité.
- **En vous inscrivant, vous acceptez ce règlement au nom de votre équipe.**
