from typing import Optional

from pathlib import Path
import sqlite3

import requests
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


import discord_webhook

dotenv_file = Path(__file__).parent / Path('.env')


class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=dotenv_file,
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


class DCWebhookConfig(EnvConfig):
    dc_webhook_url: str


class CTFdWebhookConfig(EnvConfig):
    ctfd_webhook_url: str
    ctfd_webhook_token: str


class DBConfig(EnvConfig):
    db_name: Optional[str] = None


class FirstBloodRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    challenge_id: int
    challenge_name: str
    first_blood_player_id: int
    first_blood_player_name: str
    first_blood_player_team: str
    timestamp: Optional[str] = None


class FirstBloodFilter(BaseModel):
    challenge_id: Optional[int] = None
    challenge_name: Optional[str] = None
    first_blood_player_id: Optional[int] = None
    first_blood_player_name: Optional[str] = None
    first_blood_player_team: Optional[str] = None
    timestamp_start: Optional[str] = None
    timestamp_end: Optional[str] = None


dc_config = DCWebhookConfig()
ctfd_config = CTFdWebhookConfig()
db_config = DBConfig()

conn = sqlite3.connect('notify.db')


def init_db():
    if db_config.db_name is None:
        db_config.db_name = 'db'
    curr = conn.cursor()
    curr.execute("""CREATE TABLE IF NOT EXISTS ? (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenge_id INTEGER NOT NULL,
        challenge_name TEXT NOT NULL,
        first_blood_player_id INTEGER NOT NULL,
        first_blood_player_name TEXT NOT NULL,
        first_blood_player_team TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""", (db_config.db_name))


def create_record(record: FirstBloodRecord) -> None:
    curr = conn.cursor()
    curr.execute("""
        INSERT INTO ? (challenge_id, challenge_name, first_blood_player_id, first_blood_player_name, first_blood_player_team)
        VALUES (?, ?, ?, ?, ?)
    """, (db_config.db_name, record.challenge_id, record.challenge_name, record.first_blood_player_id, record.first_blood_player_name, record.first_blood_player_team))
    conn.commit()


def read_all_records() -> list[FirstBloodRecord]:
    curr = conn.cursor()
    curr.execute("SELECT * FROM ?", (db_config.db_name))
    return [FirstBloodRecord(
        id=row[0],
        challenge_id=row[1],
        challenge_name=row[2],
        first_blood_player_id=row[3],
        first_blood_player_name=row[4],
        first_blood_player_team=row[5],
        timestamp=row[6]
    ) for row in curr.fetchall()]


def read_records_with_filter(filter_params: FirstBloodFilter) -> list[FirstBloodRecord]:
    curr = conn.cursor()
    conditions = []
    values = []

    filter_dict = filter_params.model_dump(exclude_none=True)

    for k, v in filter_dict.items():
        if k == 'timestamp_start':
            conditions.append("timestamp >= ?")
            values.append(v)
        elif k == 'timestamp_end':
            conditions.append("timestamp <= ?")
            values.append(v)
        else:
            conditions.append(f"{k} = ?")
            values.append(v)

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM ? WHERE {where_clause}"
    curr.execute(query, tuple([db_config.db_name] + values))

    return [FirstBloodRecord(
        id=row[0],
        challenge_id=row[1],
        challenge_name=row[2],
        first_blood_player_id=row[3],
        first_blood_player_name=row[4],
        first_blood_player_team=row[5],
        timestamp=row[6]
    ) for row in curr.fetchall()]


def read_by_challenge_id(challenge_id: int) -> Optional[FirstBloodRecord]:
    curr = conn.cursor()
    curr.execute(
        "SELECT * FROM ? WHERE challenge_id = ?", (db_config.db_name, challenge_id,))
    if (row := curr.fetchone()) is not None:
        return FirstBloodRecord(
            id=row[0],
            challenge_id=row[1],
            challenge_name=row[2],
            first_blood_player_id=row[3],
            first_blood_player_name=row[4],
            first_blood_player_team=row[5],
            timestamp=row[6]
        )
    return None


def update_record(record: FirstBloodRecord) -> None:
    if not record.id:
        raise ValueError("Record ID is required for update")

    curr = conn.cursor()
    update_data = record.model_dump(
        exclude={'id', 'timestamp'}, exclude_none=True)
    if not update_data:
        return

    updates = ", ".join([f"{k} = ?" for k in update_data.keys()])
    query = f"UPDATE ? SET {updates} WHERE id = ?"
    curr.execute(query, (db_config.db_name, *update_data.values(), record.id))
    conn.commit()


def fetch_ctfd_first_blood_data() -> list[FirstBloodRecord]:
    headers = {'Authorization': f'Token {ctfd_config.ctfd_webhook_token}'}
    response = requests.get(
        f'{ctfd_config.ctfd_webhook_url}/api/v1/challenges', headers=headers)
    challenges = response.json()['data']

    first_bloods = []
    for challenge in challenges:
        solves_response = requests.get(
            f'{ctfd_config.ctfd_webhook_url}/api/v1/challenges/{
                challenge["id"]}/solves',
            headers=headers
        )
        solves = solves_response.json()['data']
        if solves:
            first_solve = solves[0]  # First solve is the first blood
            first_bloods.append(FirstBloodRecord(
                challenge_id=challenge['id'],
                challenge_name=challenge['name'],
                first_blood_player_id=first_solve['user']['id'],
                first_blood_player_name=first_solve['user']['name'],
                first_blood_player_team=first_solve['team']['name'] if 'team' in first_solve else 'No Team'
            ))
    return first_bloods


def notify_new_first_bloods():
    first_bloods = fetch_ctfd_first_blood_data()
    webhook = discord_webhook.DiscordWebhook(url=dc_config.dc_webhook_url)

    for blood in first_bloods:
        existing = read_by_challenge_id(blood.challenge_id)
        if existing is None:
            create_record(blood)
            embed = discord_webhook.DiscordEmbed(
                title="🩸 New First Blood!",
                description=f"Challenge: {blood.challenge_name}",
                color="ff0000"
            )
            embed.add_field(name="Solver", value=blood.first_blood_player_name)
            embed.add_field(name="Team", value=blood.first_blood_player_team)
            webhook.add_embed(embed)
            webhook.execute()
            webhook.remove_embed(0)  # Clear embed for next iteration


if __name__ == "__main__":
    init_db()
    notify_new_first_bloods()
