# NCTF26 — Volume de challenges & proposition de calendrier

_Document d'organisation. Chiffres extraits du dépôt (challenges en `state: visible`)._

## 1. Proposition de nouvelles dates

| Phase            | Proposition                            | Format            | Public visé               |
| ---------------- | -------------------------------------- | ----------------- | ------------------------- |
| **Présélection** | **jeu 22 → sam 24 octobre 2026** (3 j) | Jeopardy en ligne | ~300 joueurs, équipes     |
| **Finale**       | **jeu 19 novembre 2026** (Lomé, 1 j)   | King of the Hill  | ~10 équipes (~50 joueurs) |

> Rappel — dates actuellement inscrites dans le déploiement : présélection 23–24 oct,
> finale 29–30 oct. La nouvelle proposition **allonge la présélection à 3 jours** et
> **repousse la finale au 19 novembre**, soit ~3 semaines de battement après la
> présélection (plus de marge pour dépouiller, préparer l'arène et convoquer les
> finalistes).

## 2. Présélection — nombre de challenges

**226 challenges** jouables, répartis sur **21 catégories**.

- **61** servis par équipe (`type: team_instance`, instance Docker + flag HMAC par équipe)
- **165** statiques / dynamiques (fichier ou service partagé)

| Catégorie   |   Total | Servis (instance/équipe) | Statiques/dyn |
| ----------- | ------: | -----------------------: | ------------: |
| web         |      22 |                       14 |             8 |
| crypto      |      17 |                        8 |             9 |
| warmup      |      16 |                        0 |            16 |
| cloud       |      14 |                        7 |             7 |
| misc        |      14 |                        4 |            10 |
| supplychain |      14 |                        4 |            10 |
| ai          |      12 |                        4 |             8 |
| sysadmin    |      12 |                        4 |             8 |
| ml          |      11 |                        3 |             8 |
| pwn         |      11 |                        5 |             6 |
| blockchain  |      10 |                        1 |             9 |
| networking  |       9 |                        0 |             9 |
| ppc         |       9 |                        0 |             9 |
| forensics   |       8 |                        0 |             8 |
| hardware    |       8 |                        0 |             8 |
| mobile      |       8 |                        0 |             8 |
| osint       |       8 |                        0 |             8 |
| reverse     |       8 |                        0 |             8 |
| stego       |       8 |                        0 |             8 |
| chains      |       6 |                        6 |             0 |
| cve         |       1 |                        1 |             0 |
| **Total**   | **226** |                   **61** |       **165** |

_Réserve : **126** challenges supplémentaires existent dans le dépôt en `state: hidden`
(squelettes non finalisés ou servis pas encore validés en répétition Docker). Ils
n'apparaissent pas aux joueurs tant qu'ils ne sont pas terminés et basculés en visible._

## 3. Finale — nombre de challenges

La finale est un **King of the Hill** sur l'arène : **4 collines** déployées, tenues en
continu, chaque tick de possession rapporte des points.

| Colline        | Nature                                                  |
| -------------- | ------------------------------------------------------- |
| throne         | Prise de contrôle générique                             |
| citadel        | Boot2root (accès SSH joueur)                            |
| armory         | Boot2root (accès SSH joueur)                            |
| réseau-fortune | Économie / marketing de réseau (« richesse du réseau ») |

> **Décision à prendre :** aucun **lot jeopardy dédié à la finale** n'est encore
> désigné dans le dépôt. Deux options :
>
> - **Finale 100 % KotH** (4 collines) — format compact, spectaculaire, adapté à
>   une journée sur site ;
> - **KotH + jeopardy finale** — ajouter un lot restreint (~20–30 épreuves) puisé
>   dans les catégories difficiles et/ou dans la réserve `hidden`, à finaliser
>   spécifiquement pour la finale.
>
> Recommandation : trancher ce point avant de figer le calendrier, car préparer un
> lot jeopardy finale supplémentaire pèse sur le planning.

## 4. Notes

- Ces comptes reflètent l'**état du dépôt** (source de vérité pour un déploiement neuf).
  La base de prod actuelle porte en plus ~155 challenges orphelins masqués (importés
  avant la déduplication, sans source) — invisibles aux joueurs, à purger séparément.
- Le pool présélection couvre les 21 catégories : de `warmup` (16, mise en jambe) aux
  familles techniques (web, crypto, pwn, cloud, ai/ml…).
- Les 61 servis sont dimensionnés pour ~300 joueurs (une instance Docker par équipe,
  flag unique par équipe) — pas de flag partagé, donc pas de triche par recopie.
