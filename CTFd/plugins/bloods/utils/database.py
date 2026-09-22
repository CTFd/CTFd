from CTFd.models import db, Solves, Awards, Challenges, Users, Teams


# table name
table_name = "bloods"

class Bloods(db.Model):
  __tablename__ = table_name
  
  # blood id
  id = db.Column(db.Integer, primary_key=True)
  
  # blood position
  position = db.Column(db.Integer)
  
  # associated chal id
  challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"))
  
  # associated user id
  user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
  
  # associated team id
  team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
  
  # associated award id
  award_id = db.Column(db.Integer, db.ForeignKey("awards.id", ondelete="CASCADE"))

def add(
    blood_chal_id: int,
    blood_position: int,
    solve: Solves, 
    award_title: str,
    award_desc: str,
    award_value: int,
    award_icon: str
  ) -> None:
  # create an award
  award = Awards(
    user_id=solve.user_id,
    team_id=solve.team_id,
    name=award_title,
    description=award_desc,
    value=award_value,
    icon=award_icon,
    date=solve.date,
  )
  db.session.add(award)
  db.session.commit()

  # create the blood
  tracker = Bloods(
    challenge_id=blood_chal_id,
    position=blood_position,
    user_id=solve.user_id,
    team_id=solve.team_id,
    award_id=award.id,
  )
  db.session.add(tracker)
  db.session.commit()

def remove(tracker: Bloods) -> None:
  if not tracker: return

  award = Awards.query.filter_by(id=tracker.award_id).first()
  if award:
    db.session.delete(award)

  db.session.delete(tracker)
  db.session.commit()

def remove_all_for_chal(chal_id: int) -> None:
  trackers = Bloods.query.filter_by(challenge_id=chal_id).all()
  for tracker in trackers:
    remove(tracker)
  
  # commit not strictly needed since each call commits
  db.session.commit()

def get_all():
  return db.session.query(
    Bloods.position,
    Challenges.id.label('challenge_id'),
    Challenges.name.label('challenge_name'),
    Users.id.label('user_id'),
    Users.name.label('user_name'),
    Teams.id.label('team_id'),
    Teams.name.label('team_name'),
    Solves.date.label('date')
  ).join(Challenges, Bloods.challenge_id == Challenges.id) \
  .join(Users, Bloods.user_id == Users.id) \
  .outerjoin(Teams, Bloods.team_id == Teams.id) \
  .join(Solves, db.and_(
      Solves.challenge_id == Bloods.challenge_id, 
      Solves.user_id == Bloods.user_id
  )).all()
