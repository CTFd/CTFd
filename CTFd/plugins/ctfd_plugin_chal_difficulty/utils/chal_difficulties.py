from CTFd.models import Challenges

from . import database
from . import config


def sync():
  chals_ids = [chal.id for chal in Challenges.query.order_by(Challenges.category, Challenges.id).all()]
  
  # remove any invalid records
  records = {d.challenge_id: [False, d] for d in database.get_all()}

  for id, data in records.items():
    if id in chals_ids:
      records[id][0] = True

  for id, data in records.items():
    if not data[0]:
      database.remove_record(data[1])
      
  # add missing records
  for chal_id in chals_ids:
    if chal_id not in records:
      database.add(chal_id, 0)

def set(request_form):
  no_difficulties_str = request_form.get("no_difficulties", "3")
  config.set_no_difficulties(no_difficulties_str)
  
  no_difficulties = config.get_no_difficulties()
  
  for key, value_str in request_form.items():
    if key.startswith("chal_"):
      chal_id = int(key.split("_")[1])
      
      record = database.get_by_chal_id(chal_id)

      if value_str == "0" or value_str == "": # if set to 0 or invalid, delete the record to keep the database clean
        if record:
          database.remove_record(record)
      
      else:
        value = int(value_str)
        if value < 0:
          valid_diff = 0
        elif value > no_difficulties:
          valid_diff = no_difficulties
        else:
          valid_diff = value
          
        if record: # record exists, just update the difficulty
          record.difficulty = valid_diff
          
        else: # record doesn't exist, add it
          database.add(chal_id, valid_diff)
