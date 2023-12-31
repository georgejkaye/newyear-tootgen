from datetime import datetime
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


def main():
    current_time = datetime.today()
    current_time_file = Path("/app/toots") / current_time.strftime("%Y-%m-%d-%H%M")
    if not os.path.isfile(current_time_file):
        print(f"File {current_time_file} not found")
    else:
        reply_file = Path("/app/toots") / "reply"
        with open(reply_file) as f:
            reply_id = int(f.read().replace("\n", ""))
        with open(current_time_file, "r") as f:
            toot = f.read().replace("\n", "")
        new_id = post_status(toot, reply_id)
        if new_id is not None:
            with open(reply_file, "w") as f:
                f.write(str(new_id))


if __name__ == "__main__":
    main()
