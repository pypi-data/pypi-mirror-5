# django-support-form

[![Build Status](https://travis-ci.org/cbmi/django-support-form.png?branch=master)](https://travis-ci.org/cbmi/django-support-form)
[![Coverage Status](https://coveralls.io/repos/cbmi/django-support-form/badge.png?branch=master)](https://coveralls.io/r/cbmi/django-support-form?branch=master)

Simple contact/support form for Django apps.

## Install

```bash
pip install django-support-form
```

## Setup

Add `supportform` to `INSTALLED_APPS` along with the following Django contrib apps:

```python
INSTALLED_APPS = (
    'supportform',
    ...
)
```

Include the `supportform.urls` in the the `ROOT_URLCONF`:

```python
from django.conf.urls import url, patterns, include

urlpatterns = patterns('',
    url(r'^support/', include('supportform.urls')),
    ...
)
```

## Settings

- `SUPPORT_EMAIL` - The recipient email address the support email will be sent to, e.g. 'support@example.com'. Default is `DEFAULT_FROM_EMAIL` Django setting.
- `SUPPORT_EMAIL_SUBJECT` - Default email subject prepopulated in the support form. Default is 'Support Message'.
- `SUPPORT_WAIT_SEND` - Wait until the email successfully sends. If set to false, the email will be sent in the background (via a thread). Default `True`

## Templates

The templates that come with the django-supportform are functional, but _very_ minimal:

- `supportform/form.html` - Renders the support form omitting the email field is the user is logged in. On submission if the email fails to send, a fallback message will be display to send an email directly to `SUPPORT_EMAIL`.
    - Context received:
        - `form` - `SupportForm` instance
- `supportform/success.html` - Renders a static success/thank you page. This is the page redirected to after successfully sending a message.
    - Context received: (none)

An email template is also provided and can be customized as well:

- `supportform/email_body.txt`
    - Context recieved:
        - `message` - Left by the user
        - `request` - Request object
        - `user` - If the message was left by an authenticated user
