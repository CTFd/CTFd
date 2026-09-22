from CTFd.models import db, Solves, Awards, Challenges, Users, Teams
from CTFd.utils import get_config

from . import config
from . import database


def sync():
  """sync all bloods"""
  
  user_mode = get_config("user_mode")

  # retrieve the current config
  no_bloods = int(config.get_no_bloods() or 3)

  bloods_val = {}
  bloods_titles = {}
  bloods_icons = {}
  
  for i in range(1, no_bloods + 1):
    # blood val
    blood_val_raw = config.get_blood_val(i)
    if blood_val_raw and str(blood_val_raw).isdigit():
      bloods_val[i] = int(blood_val_raw)
    else:
      bloods_val[i] = 0
    
    # blood title
    blood_title_raw = config.get_blood_title(i)
    bloods_titles[i] = blood_title_raw if blood_title_raw is not None else f"{i}th Blood"
    
    # blood icon
    blood_icon_raw = config.get_blood_icon(i)
    bloods_icons[i] = blood_icon_raw if blood_icon_raw is not None else "lightning"

  filter_mode = config.get_filter_mode() or "blacklist"
    
  filter_list_raw = config.get_filter_list()
  filter_list = [name.strip() for name in filter_list_raw.split(",") if name.strip()]
    
  # sync bloods for each chal
  chals = Challenges.query.all()
  for chal in chals:

    # check if this chal has bloods enabled
    has_blood: bool = False
    if filter_mode == "blacklist":
      has_blood = chal.name not in filter_list
    elif filter_mode == "whitelist":
      has_blood = chal.name in filter_list
    else:
      raise ValueError(f"invalid filter mode: {filter_mode}")

    if not has_blood: # chal doesn't have bloods enabled
      # destroy any existing awards (if it has any)
      database.remove_all_for_chal(chal.id)
      
      continue

    # find the solutions for this chal
    query = Solves.query.join(Users, Solves.user_id == Users.id).filter(
      Solves.challenge_id == chal.id,
      Users.banned == False, # user must not be banned
      Users.hidden == False # user must not be hidden
    )

    if user_mode == "teams":
      query = query.join(Teams, Solves.team_id == Teams.id).filter(
        Teams.banned == False, # team must not be banned
        Teams.hidden == False # team must not be hidden
      )

    # find the top solutions (the first solutions)
    top_solves = (
      query.order_by(
        Solves.date.asc(),
        Solves.id.asc()
      ).limit(no_bloods).all()
    )
    top_solves = {i + 1: solve for i, solve in enumerate(top_solves)}

    valid_positions_kept = []

    # destroy or update existing awards
    trackers = database.Bloods.query.filter_by(challenge_id=chal.id).all()
    for tracker in trackers:
      if tracker.position > no_bloods:
        database.remove(tracker)
        continue

      expected_solve = top_solves.get(tracker.position)

      if (
        expected_solve
        and tracker.user_id == expected_solve.user_id
        and tracker.team_id == expected_solve.team_id
      ):
        award = Awards.query.filter_by(id=tracker.award_id).first()
        if award:
          award.name = bloods_titles[tracker.position]
          award.description = f"{chal.name}"
          award.value = bloods_val[tracker.position]
          award.icon = bloods_icons[tracker.position]
          award.date = expected_solve.date
          valid_positions_kept.append(tracker.position)
        else:
          db.session.delete(tracker)
          db.session.commit()
        
      else:
        database.remove(tracker)

    # add missing awards
    for pos, solve in top_solves.items():
      if pos not in valid_positions_kept:
        database.add(
          blood_chal_id=chal.id,
          blood_position=pos,
          solve=solve,
          award_title=bloods_titles[pos],
          award_desc=f"{chal.name}",
          award_value=bloods_val[pos],
          award_icon=bloods_icons[pos],
        )
