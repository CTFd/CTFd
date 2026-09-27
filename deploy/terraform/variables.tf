variable "aws_region" {
  description = "Region AWS. eu-west-3 (Paris) : latence minimale et Amazon Bedrock / modeles Nova disponibles (GPU g4dn seulement pour le repli ollama)."
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  description = "Prefixe applique au nom de toutes les ressources."
  type        = string
  default     = "ctf"
}

# ---------------------------------------------------------------------------
# Phase de l'evenement : c'est LE levier de cout.
# ---------------------------------------------------------------------------

variable "phase" {
  description = <<-EOT
    Etat courant du CTF. Determine quelles machines existent et leur taille.

      off           Hors evenement. Aucune instance EC2. Seules subsistent
                    les archives statiques sur S3 (site statique, ~0.50 USD/mois).
      setup         Front seul, petite taille. Pour preparer les challenges,
                    tester, ouvrir les inscriptions.
      preselection  Front + arena, dimensionnes pour ~300 joueurs. IA servie
                    par Bedrock depuis le front (aucun noeud ; noeud IA GPU
                    seulement en repli ai_backend=ollama).
      final         Front + arena, dimensionnes pour ~50 joueurs. IA via
                    Bedrock (aucun noeud ; noeud IA GPU = repli ollama).

    Bascule via `make phase-<nom>`.
  EOT
  type        = string
  default     = "off"

  validation {
    condition     = contains(["off", "setup", "preselection", "final"], var.phase)
    error_message = "phase doit valoir off, setup, preselection ou final."
  }
}

variable "expected_players" {
  description = <<-EOT
    Nombre de joueurs attendus par phase. Sert uniquement a documenter le
    dimensionnement retenu dans locals.tf ; changez les types d'instance la-bas
    si ces chiffres bougent beaucoup.
  EOT
  type        = map(number)
  default = {
    preselection = 300
    final        = 50
  }
}

# ---------------------------------------------------------------------------
# Modele de langage des challenges IA
# ---------------------------------------------------------------------------

variable "ai_backend" {
  description = <<-EOT
    Qui repond aux challenges IA.
      bedrock  (defaut) AUCUN noeud IA : la passerelle ai-gateway du front
               appelle Amazon Bedrock (Converse) avec le role IAM du front.
               Choix retenu pour NCTF26 : le quota GPU EC2 a ete refuse le
               23/09/2026 (cas 179016552700802), donc aucune dependance GPU.
      ollama   REPLI historique : noeud GPU g4dn.xlarge + Ollama. Exige le
               quota EC2 "Running On-Demand G and VT instances" >= 4 vCPU
               (a demander plusieurs jours a l'avance).
  EOT
  type        = string
  default     = "bedrock"

  validation {
    condition     = contains(["ollama", "bedrock"], var.ai_backend)
    error_message = "ai_backend doit valoir ollama ou bedrock."
  }
}

variable "bedrock_models" {
  description = <<-EOT
    Pool de modeles Bedrock (ai_backend = bedrock), avec pour chacun son quota
    de requetes par minute : "id[=rpm],id[=rpm]...". Chaque modele a un petit
    quota par minute non ajustable sur ce compte ; la passerelle repartit les
    equipes sur le pool. Ces modeles DOIVENT supporter l'appel d'outils.
    Verifie en eu-west-3 le 24/09/2026 : les 4 Nova, sans formalite.
  EOT
  type        = string
  default     = "eu.amazon.nova-lite-v1:0=20,eu.amazon.nova-micro-v1:0=20,eu.amazon.nova-pro-v1:0=25,eu.amazon.nova-2-lite-v1:0=20"
}

variable "bedrock_chat_models" {
  description = <<-EOT
    Modeles Bedrock supplementaires reserves aux requetes SANS outils (ex :
    mistral.mistral-7b-instruct-v0:2=8, plus faible donc plus proche du
    llama3.1:8b sur lequel les niveaux sont calibres). Vide = aucun.
  EOT
  type        = string
  default     = ""
}

variable "ollama_model" {
  description = <<-EOT
    Repli ai_backend=ollama uniquement. Modele servi par Ollama pour les
    challenges de type prompt injection.
    llama3.1:8b tient largement sur le GPU T4 16 Go d'une g4dn.xlarge.
  EOT
  type        = string
  default     = "llama3.1:8b"
}

# ---------------------------------------------------------------------------
# Acces
# ---------------------------------------------------------------------------

variable "ssh_public_key" {
  description = "Contenu de votre cle publique SSH (ex: contenu de ~/.ssh/id_ed25519.pub)."
  type        = string
}

variable "admin_cidrs" {
  description = <<-EOT
    IPs autorisees en SSH. NE PAS laisser 0.0.0.0/0 : mettez l'IP publique de
    votre bureau ou de votre VPN.
  EOT
  type        = list(string)
}

variable "player_cidrs" {
  description = "IPs autorisees a atteindre le CTF. 0.0.0.0/0 = ouvert a tous."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# Ports web (80/443) du front. Derriere le proxy Cloudflare, on n'y laisse
# entrer QUE les plages Cloudflare (deploy/scripts/cloudflare-ips.sh) : sinon
# un joueur qui trouve l'IP contourne le WAF/anti-DDoS et les vraies IP
# clients (CF-Connecting-IP) ne sont plus fiables. Vide = player_cidrs.
# Les ports des instances (whale_port_range) restent sur player_cidrs.
variable "web_cidrs" {
  description = "IPs autorisees sur 80/443 du front. Vide = player_cidrs."
  type        = list(string)
  default     = []
}

variable "domain_name" {
  description = <<-EOT
    Nom de domaine du CTF (ex: ctf.exemple.com). Il pointe sur le front pendant
    l'evenement, et sur les archives statiques le reste de l'annee.
  EOT
  type        = string
  default     = ""
}

# ---------------------------------------------------------------------------
# Divers
# ---------------------------------------------------------------------------

variable "arena_use_spot" {
  description = <<-EOT
    true = instances Spot (~-70%) mais interruptibles par AWS.
    A garder sur false les 23-25 et 29-30 octobre : une interruption tuerait
    toutes les instances des equipes en cours de resolution.
  EOT
  type        = bool
  default     = false
}

variable "whale_port_range_start" {
  description = "Premier port TCP alloue aux instances de challenge par equipe."
  type        = number
  default     = 28000
}

variable "whale_port_range_end" {
  description = "Dernier port TCP alloue aux instances de challenge par equipe."
  type        = number
  default     = 28500
}

variable "arena_instance_type_override" {
  description = <<-EOT
    Surcharge du type d'instance de l'arena (sinon locals.tf : c6i.4xlarge en
    preselection, c6i.2xlarge en finale). Utile tant que le quota vCPU
    "Running On-Demand Standard" (L-1216C47A) reste bas : le front prend 2 vCPU,
    une c6i.4xlarge en demande 16. Ex. "c6i.2xlarge" (8 vCPU). Vide = defaut.
  EOT
  type        = string
  default     = ""
}
