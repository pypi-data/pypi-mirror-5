geventhttpclient-oauthlib
=========================

synopsis: Add OAUTH 1 support for geventhttpclient using oauthlib.

Usage
---------
```python
from geventhttpclient_oauthlib import OAUTH1HTTPClient

r = OAUTH1HTTPClient.from_oauth_params('http://localhost:8000/', u'access_key')

response = r.get('http://localhost:8000')
```
