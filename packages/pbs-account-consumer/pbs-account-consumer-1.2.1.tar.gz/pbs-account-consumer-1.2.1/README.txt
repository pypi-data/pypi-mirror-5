Installation
============
`pip install pbs-account-consumer`

Configuration
=============
1. Add `pbs_account_consumer` to the INSTALLED_APPS section of the settings file.

2. After installing you need to add a couple of params to your settings.py file.

    * **Example param values:**
        - OPENID_SSO_SERVER_URL = 'https://account.pbs.org/cranky'                                                                                                                    
        - OPENID_CREATE_USERS = True                                                                                                                                                     
        - OPENID_UPDATE_DETAILS_FROM_SREG = True                                                                                                                                         
        - OPENID_USE_AS_ADMIN_LOGIN = True                                                                                                                                               
        - OPENID_ADMIN_LOGIN_TEMPLATE = None                                                                                                                                             
        - LOGIN_REDIRECT_URL = '/'    

3. Add the consumer app to the url routing.

    * **For example:**
        - Add `url(r'^openid/', include('pbs_account_consumer.urls'))` to urls.py in your project.

4. Add the proper authentication backend to your project.

    - Add `AUTHENTICATION_BACKENDS = (..., 'pbs_account_consumer.auth.OpenIDBackend',)` to settings.py.

5. Add the proper login link to the admin login template:

    - Add `pbs_accout_consumer.urls` to the main urls.py file of your project.

    - Make the link point to the `login_begin` view, as such: `{% url login_begin %}`

Requirments
===========
1. Python version 2.7 or greater.
2. Django version 1.3 or greater.
