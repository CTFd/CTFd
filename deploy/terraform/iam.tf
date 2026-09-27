# ---------------------------------------------------------------------------
# Role IAM de l'arena : lecture seule des images de challenge dans le bucket
# d'archives.
#
# Le perimetre est volontairement etroit. Un challenge pwn donne par
# construction l'execution de code sur l'arena ; si ce role pouvait ecrire dans
# le bucket ou lire le prefixe backups/, un joueur pourrait respectivement
# empoisonner les images de l'edition suivante et exfiltrer la base de donnees.
# ---------------------------------------------------------------------------

resource "aws_iam_role" "arena" {
  name = "${var.project_name}-arena"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "arena_images" {
  name = "read-challenge-images"
  role = aws_iam_role.arena.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListImagesPrefixOnly"
        Effect   = "Allow"
        Action   = "s3:ListBucket"
        Resource = aws_s3_bucket.archive.arn
        Condition = {
          StringLike = { "s3:prefix" = ["images/*", "images"] }
        }
      },
      {
        Sid      = "ReadImagesOnly"
        Effect   = "Allow"
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.archive.arn}/images/*"
      },
      {
        # L'arena peut aussi PUBLIER une image qu'elle a construite sur place
        # (deploy/scripts/arena-build-images.sh PUSH=1) : ecriture limitee au
        # prefixe images/, jamais de suppression.
        Sid      = "PublishBuiltImages"
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.archive.arn}/images/*"
      },
    ]
  })
}

resource "aws_iam_instance_profile" "arena" {
  name = "${var.project_name}-arena"
  role = aws_iam_role.arena.name
}

# ---------------------------------------------------------------------------
# Role IAM du front : la sauvegarde automatique (deploy/scripts/backup.sh,
# timer systemd) envoie les dumps dans backups/. Ecriture seule : ni lecture ni
# listing, pour qu'une compromission du front ne permette pas de relire les
# dumps precedents (le front porte deja la base vivante, pas son historique).
# ---------------------------------------------------------------------------

resource "aws_iam_role" "front" {
  name = "${var.project_name}-front"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "front_backups" {
  name = "write-backups-only"
  role = aws_iam_role.front.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "PutBackupsOnly"
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:AbortMultipartUpload"]
        Resource = "${aws_s3_bucket.archive.arn}/backups/*"
      },
    ]
  })
}

# Backend bedrock : la passerelle IA (conteneur ai-gateway du front) invoque
# les modeles avec ce role. InvokeModel seulement : ni gestion des modeles,
# ni lecture des journaux d'invocation. Les profils d'inference "eu." routent
# vers plusieurs regions, d'ou le foundation-model en wildcard de region.
resource "aws_iam_role_policy" "front_bedrock" {
  count = var.ai_backend == "bedrock" ? 1 : 0
  name  = "invoke-bedrock-models"
  role  = aws_iam_role.front.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "InvokeOnly"
        Effect = "Allow"
        Action = ["bedrock:InvokeModel"]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*",
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:inference-profile/*",
        ]
      },
    ]
  })
}

resource "aws_iam_instance_profile" "front" {
  name = "${var.project_name}-front"
  role = aws_iam_role.front.name
}

# Acces operateur de secours par AWS Systems Manager (Run Command / Session
# Manager, via HTTPS) : quand le SSH admin est inutilisable (CGNAT, blackhole
# PMTU...), l'operateur garde une voie vers le front. Politique geree AWS,
# aucune permission sur les donnees du CTF.
resource "aws_iam_role_policy_attachment" "front_ssm" {
  role       = aws_iam_role.front.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
