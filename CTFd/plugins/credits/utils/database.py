from CTFd.models import db


class Credits(db.Model):
  __tablename__ = "credits"
  
  # credit id
  id = db.Column(db.Integer, primary_key=True)
  
  # credit content
  content = db.Column(db.Text)

def add(
    content
  ) -> None:
  new_credit = Credits(content=content)
  db.session.add(new_credit)
  db.session.commit()

def remove(credit_id) -> None:
  credit = Credits.query.filter_by(id=credit_id).first()
  if credit:
    db.session.delete(credit)
    db.session.commit()

def remove_all() -> None:
  Credits.query.delete()
  db.session.commit()
  
def get_all():
  return Credits.query.all()
