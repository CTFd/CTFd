# CTFd MariaDB Backup & Restore (Docker)

Deze setup maakt **veilige, reproduceerbare database-backups** van een CTFd MariaDB-container en maakt **snel terugzetten** mogelijk via one-shot containers.

De backup staat **los van de database-container**, zodat een database-crash **nooit** je backups meeneemt.

---

## Overzicht

### Wat wordt geback-upt?
- ✅ **MariaDB database** (`ctfd`)
- ❌ Geen applicatiebestanden
- ❌ Geen Docker images
- ❌ Geen containers

Voor **volledige recovery** combineer je dit met:
- database backup (dit)
- CTFd uploads/content backup (challenges, logo's, theme)

---

## Architectuur

- **db**  
  Draait MariaDB met een persistent volume (`.data/mysql`)

- **backup**  
  One-shot container die via `mysqldump` een SQL-backup maakt

- **restore**  
  One-shot container die een gekozen SQL-backup terugzet

- **backups** (Docker volume)  
  Bevat alle `.sql` backups, los van de database

---

## Waar staat alles?

### Database data

```bash
.data/mysql/
```
Dit is het **live databasevolume**.  

### Backups

```bash
backups/
├── 2025-12-19_20-38-26.sql
├── 2025-12-20_03-00-00.sql
```

- Elke backup = één `.sql` bestand
- Naam = timestamp
- Blijft bestaan als DB/container crasht

---

## Vereisten

- Docker
- Docker Compose v2 (`docker compose`)
- Werkende `db` service

---

## Database backup maken

### Handmatig

```bash
docker compose run --rm backup
```

#### Resultaat

```bash
backups/"Timestamp".sql
```
De backup-container:

1. start
2. maakt de dump
3. stopt
4. wordt verwijderd

```bash
backup container
  └─ mysqldump → netwerk → db container
                  ↓
              backups volume
```

- Geen database-files gedeeld
- Geen risico op corruptie


## Database restore (terugzetten)

**LET OP: Een restore overschrijft data in de database!!!**

Gebruik dit:

- bij recovery
- bij migratie
- bij test/herstel

### Beschikbare backups bekijken

```bash
ls backups
```
Kies één bestand, bijvoorbeeld:

```sql
2025-12-19_20-38-26.sql
```

### Restore uitvoeren (Windows / Linux / macOS)

```bash
docker compose run --rm \
  --env BACKUP_FILE=2025-12-19_20-38-26.sql \
  restore
```
**Werkt op:**

- Windows (Git Bash, PowerShell)
- Linux
- macOS

#### Wat doet de restore?

1. Verbindt via netwerk met MariaDB
2. Zet foreign keys & unique checks tijdelijk uit
3. Laadt de SQL dump
4. Commit in één transactie
5. Zet checks weer aan


## Geautomatiseerd

Indien CTFd in Kubernetes is gedeployed, kan de backup container worden aangeroepen met een cronjob. Op deze manier zullen er automatisch backups worden gemaakt.