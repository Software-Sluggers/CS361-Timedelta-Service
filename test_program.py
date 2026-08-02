import requests

payload = {
	"timestamp": "2026-08-02T12:00:00.000Z",
	"operation": "add",
	"value": 5,
	"unit": "days"
}

response = requests.get(
	"http://localhost:5000/timedelta",
	params=payload,
	timeout=5,
)

print("Status:", response.status_code)
print("Response:", response.json())