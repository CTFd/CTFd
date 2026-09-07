from datetime import datetime
from CTFd.models import db, Solves
from CTFd.utils import get_config

from . import disabled_chals

# table name
table_name_writeups = "writeups"

class Writeups(db.Model):
  __tablename__ = table_name_writeups
  
  # writeup id
  id = db.Column(db.Integer, primary_key=True)
  
  # associated chal id
  challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"))
  
  # associated user id
  user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
  
  # writeup content
  code = db.Column(db.Text)
  
  # writeups upload time
  submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

  challenge = db.relationship("Challenges", foreign_keys="Writeups.challenge_id")
  user = db.relationship("Users", foreign_keys="Writeups.user_id")


def sync():
  try:
    # get disabled chals
    # disabled_chal_ids = [d.challenge_id for d in disabled_chals.get_all()]

    for writeup in Writeups.query.all():
      # the user doesn't exist anymore
      if not writeup.user:
        db.session.delete(writeup)
        continue

      # the challenge doesn't exist anymore
      if not writeup.challenge:
        db.session.delete(writeup)
        continue

      # the challenge is disabled
      # if writeup.challenge_id in disabled_chal_ids:
      #   db.session.delete(writeup)
      #   continue

      # the user/team doesn't have a solution for the challenge
      user_mode = get_config("user_mode")
      if user_mode == "teams":
        team_id = writeup.user.team_id
        if not team_id:
          db.session.delete(writeup)
          continue
          
        solved = Solves.query.filter_by(
          team_id=team_id, challenge_id=writeup.challenge_id
        ).first()
        
        if not solved:
          db.session.delete(writeup)
        
      else:
        solved = Solves.query.filter_by(
          user_id=writeup.user_id, challenge_id=writeup.challenge_id
        ).first()
        
        if not solved:
          db.session.delete(writeup)

    db.session.commit()

  except Exception as e:
    db.session.rollback()
    print(f"[writeups plugin] Cleanup Error: {e}")


def get_all():
  return Writeups.query.order_by(Writeups.submitted_at.desc()).all()

def get_all_for_chal(chal_id):
  if not chal_id: return []
  
  return Writeups.query.filter_by(challenge_id=chal_id).all()

def delete_writeup(writeup_id):
  if not writeup_id: return

  writeup = Writeups.query.filter_by(id=writeup_id).first()
  if writeup:
    db.session.delete(writeup)
    db.session.commit()
    
def delete_writeup_for_user_and_chal(chal_id, user_id) -> bool:
  existing = Writeups.query.filter_by(
    challenge_id=chal_id, user_id=user_id
  ).first()
  
  if existing:
    # delete the record
    db.session.delete(existing)
    db.session.commit()
    
    return True
  
  else:  
    return False

def delete_all():
  Writeups.query.delete()
  db.session.commit()

def delete_all_for_user(user_id):
  if not user_id: return
  
  Writeups.query.filter_by(user_id=user_id).delete()
  db.session.commit()

def delete_all_for_chal(chal_id):
  if not chal_id: return

  Writeups.query.filter_by(challenge_id=chal_id).delete()
  db.session.commit()

def submit(content, chal_id, user_id) -> bool:
  if not content: return False

  if len(content) > 50000: return False

  existing = Writeups.query.filter_by(
    challenge_id=chal_id, user_id=user_id
  ).first()
  
  # update existing writeup
  if existing:
    existing.code = content
    existing.submitted_at = datetime.utcnow()
  
  # create a new writeups
  else:
    new_writeup = Writeups(challenge_id=chal_id, user_id=user_id, code=content)
    db.session.add(new_writeup)

  db.session.commit()

  return True