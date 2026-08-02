import requests
from tests.conftest import BASE_URL

def test_add_days(get_timedelta):
	status, body = get_timedelta(
		timestamp="2026-08-02T12:00:00.000Z",
		operation="add",
		value=5,
		unit="days"
	)

	assert status == 200
	assert body ["OriginalTimestamp"] == "2026-08-02T12:00:00.000Z"
	assert body ["Value"] == 5
	assert body ["Unit"] == "days"
	assert body ["ResultingTimestamp"] == "2026-08-07T12:00:00.000Z"
	assert body ["Summary"] == "5 days after 2026-08-02T12:00:00.000Z is 2026-08-07T12:00:00.000Z"

def test_add_hours(get_timedelta):
	status, body = get_timedelta(
		timestamp= "2026-08-02T12:00:00.000Z",
		operation="add",
		value=3,
		unit="hours"
	)

	assert status == 200
	assert body["Unit"] == "hours"
	assert body["ResultingTimestamp"] == "2026-08-02T15:00:00.000Z"
	assert "3 hours after" in body["Summary"]

def test_add_minutes(get_timedelta):
	status, body = get_timedelta(
		timestamp= "2026-08-02T12:00:00.000Z",
		operation="add",
		value=30,
		unit="minutes"
	)

	assert status == 200
	assert body["Unit"] == "minutes"
	assert body["ResultingTimestamp"] == "2026-08-02T12:30:00.000Z"
	assert "30 minutes after" in body["Summary"]

def test_add_seconds(get_timedelta):
	status, body = get_timedelta(
		timestamp="2026-08-02T12:00:00.000Z",
		operation="add",
		value=45,
		unit="seconds"
	)

	assert status == 200
	assert body["Value"] == 45
	assert body["ResultingTimestamp"] == "2026-08-02T12:00:45.000Z"
	assert "45 seconds after" in body["Summary"]

def test_negative_value(get_timedelta):
	"""Make sure that a negative value makes a summary of before."""
	status, body = get_timedelta(
		timestamp="2026-08-02T12:00:00.000Z",
		operation= "add",
		value=-5,
		unit= "days"
	)

	assert status == 200
	assert body["Value"] == -5
	assert body["ResultingTimestamp"] == "2026-07-28T12:00:00.000Z"
	assert body["Summary"] == "5 days before 2026-08-02T12:00:00.000Z is 2026-07-28T12:00:00.000Z"

#Error handling

def test_missing_required_params():
	"""Test that a 400 is returned for a missing parameters."""
	response = requests.get(
		f"{BASE_URL}/timedelta", 
		params = {"timestamp": "2026-08-02T12:00:00.000z", "operation": "add", "value": 5}
	)
	assert response.status_code == 400
	body = response.json()
	assert "Error" in body

def test_invalid_timestamp(get_timedelta):
	status, body = get_timedelta(
		timestamp="not-a-timestamp",
		operation= "add",
		value=5,
		unit="days"
	)

	assert status == 400
	assert body["Error"] == "Invalid timestamp. The timestamp must be an ISO-formatted timestamp."

def test_invalid_operation(get_timedelta):
	status,body = get_timedelta(
		timestamp= "2026-08-02T12:00:00.000Z",
		operation= "subtract",
		value= 5,
		unit="days"
	)

	assert status == 400
	assert body["Error"] == "Invalid operation. Currently, only add is supported."

def test_invalid_unit(get_timedelta):
	status, body = get_timedelta(
		timestamp= "2026-08-02T12:00:00.000Z",
		operation= "add",
		value=5,
		unit="weeks"
	)

	assert status == 400
	assert body["Error"] == "Invalid unit. The unit must be one of days, hours, minutes, or seconds."

def test_invalid_value_string():
	"""Test if a non-integer value returns 400"""
	response = requests.get(
		f"{BASE_URL}/timedelta",
		params={
			"timestamp": "2026-08-02T12:00:00.000Z",
			"operation": "add",
			"value": "five",
			"unit": "days"
		}
	)		
	assert response.status_code == 400
	body = response.json()
	assert body["Error"] == "Invalid value. The value must be an integer."

def test_timestamp_case_sensitivity(get_timedelta):
	"""Test that z is require for the UTC"""
	status, body = get_timedelta(
		timestamp= "2026-08-02T12:00:00.000z",
		operation = "add",
		value = 1,
		unit="days"
	)

	assert status == 400
	assert body["Error"] == "Invalid timestamp. The timestamp must be an ISO-formatted timestamp."