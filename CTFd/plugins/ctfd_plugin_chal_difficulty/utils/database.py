from CTFd.models import db


class ChalDifficulties(db.Model):
  __tablename__ = "chal_difficulties"
  
  # chal difficulty id
  id = db.Column(db.Integer, primary_key=True)

  # associated chal id  
  challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"))
  
  # difficulty
  difficulty = db.Column(db.String(32))

def add(
    challenge_id,
    difficulty
  ) -> None:
  new_chal_difficulty = ChalDifficulties(challenge_id=challenge_id, difficulty=difficulty)
  db.session.add(new_chal_difficulty)
  db.session.commit()

def remove(chal_difficulty_id) -> None:
  chal_difficulty = ChalDifficulties.query.filter_by(id=chal_difficulty_id).first()
  if chal_difficulty:
    db.session.delete(chal_difficulty)
    db.session.commit()
    
def remove_record(record) -> None:
  db.session.delete(record)
  db.session.commit()

def remove_all() -> None:
  ChalDifficulties.query.delete()
  db.session.commit()

def get_by_chal_id(chal_id):
  return ChalDifficulties.query.filter_by(
    challenge_id=chal_id
  ).first()

def get_all():
  return ChalDifficulties.query.all()
