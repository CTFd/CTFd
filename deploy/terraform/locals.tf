# ---------------------------------------------------------------------------
# Dimensionnement par phase.
#
# Le calendrier est concentre : preselection les 23-25 octobre (~300 joueurs),
# finale les 29-30 octobre (~50 joueurs). Rien ne tourne en dehors de ces
# fenetres, donc on peut se permettre des machines confortables pendant les
# quelques jours qui comptent.
# ---------------------------------------------------------------------------

locals {
  sizing = {
    off = {
      front = null
      arena = null
      ai    = null
    }

    # Preparation des challenges et inscriptions : seul le front tourne.
    setup = {
      front = "t4g.small" # 2 vCPU ARM / 2 Go
      arena = null
      ai    = null
    }

    # ~300 joueurs. Le front encaisse les soumissions de flags et le scoreboard,
    # l'arena heberge beaucoup d'instances de challenge simultanees.
    preselection = {
      front = "t4g.medium"  # 2 vCPU ARM / 4 Go
      arena = "c6i.4xlarge" # 16 vCPU / 32 Go (c6a absent de Paris et Stockholm)
      ai    = "g4dn.xlarge" # GPU T4 16 Go
    }

    # ~50 joueurs (10 equipes de 4 a 5). Beaucoup plus leger.
    final = {
      front = "t4g.small"
      arena = "c6i.2xlarge" # 8 vCPU / 16 Go
      ai    = "g4dn.xlarge"
    }
  }

  # Surcharge optionnelle du type d'arena (quota vCPU bas) : var.arena_instance_type_override.
  current = merge(
    local.sizing[var.phase],
    var.arena_instance_type_override != "" && local.sizing[var.phase].arena != null
    ? { arena = var.arena_instance_type_override } : {}
  )

  front_enabled = local.current.front != null
  arena_enabled = local.current.arena != null
  # Backend bedrock : la phase garde sa taille mais le noeud GPU n'existe pas.
  ai_enabled = local.current.ai != null && var.ai_backend == "ollama"

  # Le noeud IA est le poste le plus cher a l'heure : on le rappelle dans les
  # sorties pour qu'un oubli d'extinction saute aux yeux.
  hourly_estimate_usd = {
    off          = 0.00
    setup        = 0.02
    preselection = 1.46 # t4g.medium 0.038 + c6i.4xlarge 0.808 + g4dn.xlarge 0.615 (Paris, on-demand)
    final        = 1.04 # t4g.small 0.019 + c6i.2xlarge 0.404 + g4dn.xlarge 0.615
  }
  gpu_hourly_usd = 0.615
  hourly_now_usd = local.hourly_estimate_usd[var.phase] - (
    local.current.ai != null && !local.ai_enabled ? local.gpu_hourly_usd : 0
  )
}
