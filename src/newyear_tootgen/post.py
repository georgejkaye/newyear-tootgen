from datetime import datetime
import json
import os
from pathlib import Path
from typing import Optional
import requests


def get_env_var(key: str) -> str:
    val = os.getenv(key)
    if val is None:
        raise RuntimeError(f"Could not get environment variable {key}")
    return val


def get_secret(key: str) -> str:
    file = get_env_var(key)
    with open(file, "r") as f:
        val = f.read().replace("\n", "")
    return val


def get_token():
    return get_secret("MASTODON_OAUTH_TOKEN")


def post_status(text: str, reply_to: Optional[int] = None) -> Optional[int]:
    print(f"Posting status\n\n{text}")
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": str(datetime.today().timestamp),
    }
    params = {"status": text, "in_reply_to_id": reply_to}
    url = "https://mastodon.douvk.co.uk/api/v1/statuses"
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        json = response.json()
        id = int(json["id"])
        return id
    else:
        return None


def post_toot(toot: str, set_reply: bool = False) -> Optional[int]:
    reply_id = get_reply_id()
    new_id = post_status(toot, reply_id)
    if new_id is not None and set_reply:
        set_reply_id(new_id)
    return new_id


toots_dir = Path(get_env_var("TOOTS_DIR"))
reply_file = toots_dir / "reply"


def get_reply_id() -> Optional[int]:
    if os.path.isfile(reply_file):
        with open(reply_file) as f:
            reply_id = int(f.read().replace("\n", ""))
        return reply_id
    return None


def set_reply_id(new_id: int):
    with open(reply_file, "w") as f:
        f.write(str(new_id))


def read_toots(file: str | Path) -> list[str]:
    with open(file, "r") as f:
        toot = json.load(f)
    return toot


def main():
    current_time = datetime.today()
    current_time_file = toots_dir / current_time.strftime("%Y-%m-%d-%H%M")
    if not os.path.isfile(current_time_file):
        print(f"File {current_time_file} not found")
    else:
        toots = read_toots(current_time_file)
        for toot in toots:
            response = post_toot(toot, True)
            if response is None:
                break


if __name__ == "__main__":
    main()
