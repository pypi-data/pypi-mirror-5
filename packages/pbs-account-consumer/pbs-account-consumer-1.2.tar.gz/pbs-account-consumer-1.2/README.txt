Installation
============
`pip install pbs-account-consumer`

Configuration
=============
1. After installing you need to add a couple of params to your settings.py file.

    * **Example param values:**
        - OPENID_SSO_SERVER_URL = 'https://account.pbs.org/cranky'                                                                                                                    
        - OPENID_CREATE_USERS = True                                                                                                                                                     
        - OPENID_UPDATE_DETAILS_FROM_SREG = True                                                                                                                                         
        - OPENID_USE_AS_ADMIN_LOGIN = True                                                                                                                                               
        - OPENID_ADMIN_LOGIN_TEMPLATE = None                                                                                                                                             
        - LOGIN_REDIRECT_URL = '/'    

2. Add the consumer app to the url routing.

    * **For example:**
        - Add `url(r'^openid/', include('pbs_account_consumer.urls'))` to urls.py in your project.

3. Add the proper authentication backend to your project.

    - Add `AUTHENTICATION_BACKENDS = (..., 'pbs_account_consumer.auth.OpenIDBackend',)` to settings.py.
