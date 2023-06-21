import requests
import json

# Cognos REST API endpoint URL
api_url = 'http://your-cognos-server/rest/cognos/api/v1'

# credentials
username = 'your-username'
password = 'your-password'

# Report execution request
report_id = 'report-id'
output_format = 'PDF'
recipient_email = 'recipient@example.com'

# Authenticate and retrieve access token
auth_data = {
    'grant_type': 'password',
    'username': username,
    'password': password
}
auth_url = f'{api_url}/login'
response = requests.post(auth_url, data=auth_data)
access_token = response.json().get('access_token')

# Set authorization headers
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Trigger report execution
execution_url = f'{api_url}/reports/{report_id}/execute'
response = requests.post(execution_url, headers=headers)

if response.status_code == 201:
    execution_id = response.json().get('executionId')
    print(f'Report execution started. Execution ID: {execution_id}')
else:
    print('Failed to start report execution.')

# Wait for the report execution to complete (optional)
# You can check the execution status and wait until it is finished

# Export the report
export_url = f'{api_url}/executions/{execution_id}/exports'
export_data = {
    'outputFormat': output_format
}
response = requests.post(export_url, headers=headers, data=json.dumps(export_data))

if response.status_code == 201:
    export_id = response.json().get('exportId')
    print(f'Report export started. Export ID: {export_id}')
else:
    print('Failed to start report export.')

# Wait for the report export to complete (optional)
# You can check the export status and wait until it is finished

# Email the exported report
email_url = f'{api_url}/exports/{export_id}/email'
email_data = {
    'recipients': [recipient_email],
    'subject': 'Cognos Report',
    'body': 'Please find attached the Cognos report.',
    'sendWith': 'link'  # or 'attachment' to send the report as an attachment
}
response = requests.post(email_url, headers=headers, data=json.dumps(email_data))

if response.status_code == 204:
    print('Report email sent successfully.')
else:
    print('Failed to send report email.')

# Logout and invalidate the access token
logout_url = f'{api_url}/logout'
requests.post(logout_url, headers=headers)
