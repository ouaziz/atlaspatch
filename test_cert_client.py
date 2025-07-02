import requests
try:
    r = requests.post(
        "https://atlaspatch.local/api/v1/heartbeat/",
        json={"hello": "world"},
        cert=("certs/agent1.crt", "certs/agent1.key"),
        verify="certs/ca.crt",
    timeout=10,
    )
except Exception as e:
    print(e)
    exit(1)
print(r.status_code, r.text)
