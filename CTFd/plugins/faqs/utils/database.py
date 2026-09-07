from CTFd.models import db


class Faqs(db.Model):
  __tablename__ = "faqs"
  
  # faq id
  id = db.Column(db.Integer, primary_key=True)
  
  # faq question
  question = db.Column(db.Text)
  
  # faq answer
  answer = db.Column(db.Text)

def add(
    question,
    answer
  ) -> None:
  new_faq = Faqs(question=question, answer=answer)
  db.session.add(new_faq)
  db.session.commit()

def remove(faq_id) -> None:
  faq = Faqs.query.filter_by(id=faq_id).first()
  if faq:
    db.session.delete(faq)
    db.session.commit()

def remove_all() -> None:
  Faqs.query.delete()
  db.session.commit()
  
def get_all():
  return Faqs.query.all()
