from CTFd.models import db


class Disclaimers(db.Model):
  __tablename__ = "disclaimers"
  
  # disclaimer id
  id = db.Column(db.Integer, primary_key=True)
  
  # disclaimer content
  content = db.Column(db.Text)

def add(
    content
  ) -> None:
  new_disclaimer = Disclaimers(content=content)
  db.session.add(new_disclaimer)
  db.session.commit()

def remove(disclaimer_id) -> None:
  disclaimer = Disclaimers.query.filter_by(id=disclaimer_id).first()
  if disclaimer:
    db.session.delete(disclaimer)
    db.session.commit()

def remove_all() -> None:
  Disclaimers.query.delete()
  db.session.commit()
  
def get_all():
  return Disclaimers.query.all()
