Python-Stackato
===============

A wrapper to the Stackato Client API. Allows users to make requests to the Stackato API. Easy Peasy Lemon Squeezy.

To read up more on the Stackato Client API, please see the documentation [here](http://docs.stackato.com/api/client.html).

## Installation

    pip install python-stackato

## Usage

Take a look at the examples/ folder for some real-life examples.

### Logging into the client

```python
from stackato import Session

s = Session("https://api.stackato-xxxx.local/", "username", "password")
s.login()
```

### Passwordless Authentication

This is for when you have previously logged in and the token is stored
within your client token file (hidden at ~/.stackato/client/token)

```python
from stackato import Session
s = Session("https://api.stacka.to")
if s.login():
    print(s._get('info'))
```

### Storing the authentication token locally, and deleting an app

```python
from stackato import Session

# Spot the difference!
s = Session("https://api.stackato-xxxx.local/", "username", "password")

if s.login(True):
    s.delete_app('demo')
```

### Lisng all services bound to an app

```python
from stackato import Session

s = Session("https://api.stackato-xxxx.local/", "username", "password")

if s.login():
    print(s.get_app('demo').services)
```

### Forcing your app to increase its number of instances by one

```python
from stackato import Session

s = Session("https://api.stackato-xxxx.local/", "username", "password")

if s.login():
    app = s.get_app('demo')
    app['instances'] += 1
        
    # make a PUT request to the application
    if s.put_app('demo', app):
        print('added one more instance to this application.')
```

### Making a custom GET request

This will also work with _post(), _put(), and _delete(). You can also take a look at _request() if you want to make your own custom request call.

```python
from stackato import Session

s = Session("https://api.stackato-xxxx.local/", "username", "password")

if s.login():
    print(s._get('stackato/usage?all=1'))
```
