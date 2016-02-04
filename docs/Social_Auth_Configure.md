**This document assumes hostname as 'localhost' and port as '8000'.**

Once 'settings.py' is updated with 'python_social_auth' related code,
Sync database to create needed models:

 `python manage.py syncdb`

To run and test Social Authentication, you need to configure:
Facebook Login and Google Login. 
Also, you need to use the following URL locally:

`http://localhost:8000/approval_polls`

How to Configure Facebook Login 
--------------------------------

- Go to http://developers.facebook.com/setup/
- Login and Click 'Create a New App'.
- Enter 'Display Name', Select a category, and click 'Create App ID'.
- Copy the following values into local_settings.py:
    * SOCIAL_AUTH_FACEBOOK_KEY -> App ID
    * SOCIAL_AUTH_FACEBOOK_SECRET -> App Secret
- Select 'Settings' Tab.
- Enter 'Contact Email'.
- Click 'Add Platform' -> Select 'Website'.
- Enter the following URL in Site URL: http://localhost:8000/complete/facebook/
- Click 'Save Changes'.
- Navigate to 'App Review/Status and Review'.
- Change button to 'yes' on the following: 'Do you want to make this app and all its live features available to the general public?'


How to Configure Google Login 
------------------------------

- Go to https://console.developers.google.com/ and Create a New Application.
- Click on 'Create an Empty Project'.
- Enter Project Name and Click 'Create'.
- Once you click 'Create', you will be redirected to 'Dashboard'.
- Click 'Enable and Manage APIs' button.
- Click 'Google+ API' link.
- Click 'Enable API' button.
- Navigate to 'Credentials' tab.
- Click 'OAuth Consent Screen'.
- Enter Product Name and Click 'Save'
- Select 'OAuth Client ID' from New Credentials dropdown.
- Click 'Web Application'.
- Enter the following URL in Authorized redirect URIs: http://localhost:8000/complete/google-oauth2/
- Copy the following values into local_settings.py:
    * SOCIAL_AUTH_GOOGLE_OAUTH2_KEY -> this is client ID before '.apps...'
    * SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET -> this is client secret
