import os
import pathlib
import tempfile

from flask import current_app, render_template, request, send_from_directory, url_for
from PIL import Image, ImageDraw, ImageFont

from CTFd.models import Solves, Users
from CTFd.utils import get_config
from CTFd.utils.config import is_teams_mode
from CTFd.utils.formatters import safe_html_format
from CTFd.utils.humanize.words import pluralize
from CTFd.utils.security.signing import hmac
from CTFd.utils.uploads import get_uploader

BASE_TEMPLATE = """
<div class="container">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <h3 class="text-center">{ctf_name}</h3>
            <h3 class="text-center">{account_name} has solved {challenge_name}</h3>
            <br>
            <h4 class="text-center">+{challenge_value} points</h4>
        </div>
    </div>
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <h6 class="text-center">
                Want to try? Register at <a href="{register_url}">{register_url}</a>
            </h6>
        </div>
    </div>
</div>
"""


def get_logo():
    uploader = get_uploader()
    logo = get_config("ctf_logo")
    if logo is None:
        return None
    return uploader.open(logo, mode="rb")


class SolveSocialShare(object):
    def __init__(self, user_id=None, challenge_id=None):
        self.user_id = (
            user_id or request.args.get("user_id") or request.json.get("user_id")
        )
        self.challenge_id = (
            challenge_id
            or request.args.get("challenge_id")
            or request.json.get("challenge_id")
        )
        self.type = "solve"

    @property
    def url(self):
        return url_for(
            "social.share",
            type=self.type,
            user_id=self.user_id,
            challenge_id=self.challenge_id,
            mac=self.mac,
            _external=True,
        )

    @property
    def mac(self):
        return hmac(f"{self.type}-{self.user_id}-{self.challenge_id}")

    @property
    def content(self):
        from CTFd.utils.challenges import get_solve_counts_for_challenges

        user = Users.query.filter_by(id=self.user_id).first()
        solve = Solves.query.filter_by(
            account_id=user.account_id, challenge_id=self.challenge_id
        ).first()
        challenge = solve.challenge

        # Challenge information
        challenge_id = challenge.id
        challenge_name = challenge.name
        challenge_value = challenge.value
        solves_count = get_solve_counts_for_challenges(challenge_id=challenge_id)
        solve_count = solves_count.get(challenge_id, 0)

        # Account information
        user_name = solve.user.name
        team_name = solve.team.name if solve.team else None
        account_name = team_name if is_teams_mode() else user_name

        # Instance information
        ctf_name = get_config("ctf_name", "")
        ctf_description = get_config("ctf_description", "")
        register_url = url_for("auth.register", _external=True)

        template = get_config("social_share_solve_template", BASE_TEMPLATE)

        content = safe_html_format(
            template,
            ctf_name=ctf_name,
            ctf_description=ctf_description,
            register_url=register_url,
            challenge_name=challenge_name,
            challenge_value=challenge_value,
            account_name=account_name,
            user_name=user_name,
            team_name=team_name,
            solve_count=solve_count,
            solve_count_word=str(solve_count)
            + pluralize(solves_count, " solve", " solves"),
        )
        asset_url = url_for(
            "social.assets",
            type=self.type,
            path=self.mac + ".png",
            user_id=self.user_id,
            challenge_id=self.challenge_id,
            _external=True,
        )
        meta = (
            '<meta property="og:title" content="{title}" />'
            '<meta property="og:description" content="{ctf_description}" />'
            '<meta property="og:image" content="{asset_url}" />'
        )
        title = safe_html_format(
            "{account_name} has solved {challenge_name}",
            account_name=account_name,
            challenge_name=challenge_name,
        )
        meta = safe_html_format(
            meta,
            title=title,
            ctf_description=ctf_description,
            asset_url=asset_url,
        )
        return render_template("page.html", meta=meta, content=content, title=title)

    def asset(self, path):
        from CTFd.utils.challenges import get_solve_counts_for_challenges

        target = pathlib.Path(tempfile.gettempdir()) / path
        if target.exists():
            return send_from_directory(tempfile.gettempdir(), path)

        WIDTH = 700
        HEIGHT = 360
        BG_COLOR = "#ffffff"

        user = Users.query.filter_by(id=self.user_id).first()
        solve = Solves.query.filter_by(
            account_id=user.account_id, challenge_id=self.challenge_id
        ).first()
        challenge = solve.challenge

        # Challenge information
        challenge_id = challenge.id
        challenge_name = challenge.name
        challenge_value = challenge.value
        solves_count = get_solve_counts_for_challenges(challenge_id=challenge_id)
        solve_count = solves_count.get(challenge_id, 0)
        solve_count_word = str(solve_count) + pluralize(
            solves_count, " solve", " solves"
        )

        # Account information
        account_name = solve.team.name if is_teams_mode() else solve.user.name

        # init image
        img = Image.new("RGBA", (WIDTH, HEIGHT), color=BG_COLOR)
        draw = ImageDraw.Draw(img)
        font_path = os.path.join(current_app.root_path, "fonts", "OpenSans-Bold.ttf")
        font_lg = ImageFont.truetype(font_path, 40)
        font_md = ImageFont.truetype(font_path, 25)

        # fmt: off
        # Draw user name
        _, _, w, h1 = draw.textbbox((0, 0), account_name, font=font_lg)
        draw.text(((WIDTH-w)/2, 15), account_name, font=font_lg, fill=(0,0,0,255))

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
        if fp:
            logo = Image.open(fp)
            logo.thumbnail((150, 150))
            img.alpha_composite(logo, (30, 30))
        # fmt: on

        img.save(target)
        return send_from_directory(tempfile.gettempdir(), path)


SOCIAL_SHARES = {"solve": SolveSocialShare}


def get_social_share(type):
    return SOCIAL_SHARES.get(type)
