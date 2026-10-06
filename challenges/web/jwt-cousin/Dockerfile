# ctf-jwt-cousin:latest
#
# Build:  docker build -t ctf-jwt-cousin:latest .
# Run:    docker run --rm -p 8080:8080 \
#             -e SIGNING_KEY="$(openssl rand -hex 16)" \
#             -e TEAM_SECRET="<per-team-secret>" \
#             ctf-jwt-cousin:latest
#
# SIGNING_KEY is optional: when absent the app derives it from CHALLENGE_SECRET/FLAG.
# No secret is baked into the image.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /srv

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

# non-root
RUN useradd --no-create-home --uid 10001 appuser
USER appuser

EXPOSE 8080

# 2 workers is plenty for this challenge; shared in-process state (the
# rotation counter) is not security-relevant, so worker count doesn't matter.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "30", "app:app"]
