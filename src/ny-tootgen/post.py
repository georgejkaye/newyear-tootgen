from datetime import datetime
import os
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


def post_status(text: str):
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": str(datetime.today().timestamp),
    }
    params = {"status": text}
    url = "https://mastodon.douvk.co.uk/api/v1/statuses"
    requests.post(url, headers=headers, params=params)


def main():
    current_time = datetime.today()
    current_time_file = current_time.strftime("%Y-%m-%d-%H%M")
    if not os.path.isfile(current_time_file):
        print(f"File {current_time_file} not found")
    else:
        with open(current_time_file, "r") as f:
            toot = f.read().replace("\n", "")
        post_status(toot)


if __name__ == "__main__":
    main()
