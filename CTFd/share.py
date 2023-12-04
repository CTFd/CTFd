import pathlib
import tempfile

from flask import Blueprint, abort, render_template, send_from_directory, url_for
from PIL import Image, ImageDraw, ImageFont

from CTFd.models import Solves
from CTFd.utils import get_config
from CTFd.utils.challenges import get_solve_counts_for_challenges
from CTFd.utils.config import is_teams_mode
from CTFd.utils.formatters import safe_format
from CTFd.utils.humanize.words import pluralize
from CTFd.utils.security.signing import hmac
from CTFd.utils.uploads import get_uploader

social = Blueprint("social", __name__)

BASE_TEMPLATE = """
<div class="container">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <img class="w-100 mx-auto d-block" style="max-width: 500px;padding: 50px;padding-top: 14vh;" src="{ctf_banner_url}">
            <h3 class="text-center">{ctf_name}</h3>
            <h3 class="text-center">{user_name} has solved {challenge_name}</h3>
            <br>
            <h4 class="text-center">{challenge_name} has {solve_count_word}</h4>
        </div>
    </div>
</div>
"""


def get_logo():
    uploader = get_uploader()
    logo = get_config("ctf_logo")
    return uploader.get(logo, mode="rb")


@social.route("/share/assets/<type>/<int:id>/<path>")
def assets(type, id, path):
    if type != "solves":
        abort(404)

    target = pathlib.Path(tempfile.gettempdir()) / path
    if target.exists():
        return send_from_directory(tempfile.gettempdir(), path)

    WIDTH = 700
    HEIGHT = 360
    BG_COLOR = "#ffffff"

    solve = Solves.query.filter_by(id=id).first_or_404()
    challenge = solve.challenge

    # Challenge information
    challenge_id = challenge.id
    challenge_name = challenge.name
    challenge_value = challenge.value
    solves_count = get_solve_counts_for_challenges(challenge_id=challenge_id)
    solve_count = solves_count.get(challenge_id, 0)
    solve_count_word = str(solve_count) + pluralize(solves_count, " solve", " solves")

    # Account information
    user_name = solve.user.name
    team_name = solve.team.name if is_teams_mode() else None

    # init image
    img = Image.new("RGBA", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    font_lg = ImageFont.truetype("Arial Bold.ttf", 40)
    font_md = ImageFont.truetype("Arial Bold.ttf", 25)
    font_sm = ImageFont.truetype("Arial Bold.ttf", 15)

    # fmt: off
    # Draw user name
    _, _, w, h1 = draw.textbbox((0, 0), user_name, font=font_lg)
    draw.text(((WIDTH-w)/2, 15), user_name, font=font_lg, fill=(0,0,0,255))

    # Draw user sub text
    _, _, w, h = draw.textbbox((0, 0), "has solved", font=font_md)
    draw.text(((WIDTH-w)/2, h1 + 35), "has solved", font=font_md, fill=(194, 194, 194,255))

    # Draw challenge name
    _, _, w, h = draw.textbbox((0, 0), challenge_name, font=font_lg)
    draw.text(((WIDTH-w)/2, (HEIGHT-h)/2), challenge_name, font=font_lg, fill=(0,0,0,255))

    # Draw solve count
    _, _, w, h = draw.textbbox((0, 0), solve_count_word, font=font_md)
    draw.text(((WIDTH-w)/2, ((HEIGHT-h)/2) + 35), solve_count_word, font=font_md, fill=(194, 194, 194, 255))

    # Draw point value
    _, _, w, h = draw.textbbox((0, 0), f"+{challenge_value} points", font=font_md)
    draw.text(((WIDTH-w)/2, (HEIGHT-(h + 15))), f"+{challenge_value} points", font=font_md, fill=(194, 194, 194,255))

    # Draw logo
    fp = get_logo()
    logo = Image.open(fp)
    logo.thumbnail((150, 150))
    img.alpha_composite(logo, (30, 30))
    # fmt: on

    img.save(target)
    return send_from_directory(tempfile.gettempdir(), path)


# Not sure I like the fact that this is numeric. We could probably do something better
# Maybe someone could brute force out which user solved what
@social.route("/share/<type>/<int:id>/<mac>")
def share(type, id, mac):
    if type != "solves":
        abort(404)

    result_mac = hmac(f"{type}-{id}")
    if mac != result_mac:
        abort(403)

    solve = Solves.query.filter_by(id=id).first_or_404()
    challenge = solve.challenge

    # Challenge information
    challenge_id = challenge.id
    challenge_name = challenge.name
    solves_count = get_solve_counts_for_challenges(challenge_id=challenge_id)
    solve_count = solves_count.get(challenge_id, 0)

    # Account information
    user_name = solve.user.name
    team_name = solve.team.name if is_teams_mode() else None

    # Instance information
    ctf_name = get_config("ctf_name")
    ctf_description = get_config("ctf_description")
    ctf_banner = get_config("ctf_banner")
    ctf_banner_url = url_for("views.files", path=ctf_banner)

    template = get_config("social_share_solve_template", BASE_TEMPLATE)
    title = f"{user_name} has solved {challenge_name}"
    content = safe_format(
        template,
        ctf_name=ctf_name,
        ctf_banner_url=ctf_banner_url,
        ctf_description=ctf_description,
        challenge_name=challenge_name,
        user_name=user_name,
        team_name=team_name,
        solve_count=solve_count,
        solve_count_word=str(solve_count)
        + pluralize(solves_count, " solve", " solves"),
    )
    asset_url = url_for("social.assets", type="solves", id=id, path=mac + ".png")
    meta = f"""
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{ctf_description}" />
<meta property="og:image" content="{asset_url}" />
"""
    return render_template("page.html", meta=meta, content=content, title=title)
