from CTFd.models import db


# table name
table_name_disabled_chals = "writeups_disabled_chals"

class DisabledChals(db.Model):
  __tablename__ = table_name_disabled_chals
  
  # chal id
  challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True)


def get_all():
  return DisabledChals.query.all()

def set_chal_disabled(chal_id):
  if not chal_id: return
  
  existing = DisabledChals.query.filter_by(challenge_id=chal_id).first()
  
  if not existing:
    # add record
    db.session.add(DisabledChals(challenge_id=chal_id))
    db.session.commit()
    
  # delete any existing writeups for this chal
  # delete_for_chal(chal_id) # Writeups.query.filter_by(challenge_id=chal_id).delete()

def set_chal_enabled(chal_id):
  if not chal_id: return
  
  existing = DisabledChals.query.filter_by(challenge_id=chal_id).first()
  
  if existing:
    # delete the record
    db.session.delete(existing)
    db.session.commit()

# set the chal status (True for enabled, False for disabled)
def set_chal_status(chal_id, status: bool):
  if not chal_id: return

  if not status: set_chal_disabled(chal_id)
  else: set_chal_enabled(chal_id)

# return True is the chal is enabled, False if the chal is disabled
def get_chal_status(chal_id) -> bool:
  return (
    DisabledChals.query.filter_by(challenge_id=chal_id).first()
    is None
  )