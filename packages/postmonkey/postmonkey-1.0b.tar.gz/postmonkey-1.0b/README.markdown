`PostMonkey` is a simple Python (2.6+) wrapper for MailChimp's API
version 1.3.


Features
========

1. 100% unit test and code coverage
2. Connections handled by [Requests](http://docs.python-requests.org>)
3. Configurable timeout
4. Simple `Exceptions`


Basic Usage
===========

Once you create a `PostMonkey` instance with your MailChimp API key,
you can use it to call MailChimp's API methods directly:

```python
    from postmonkey import PostMonkey
    pm = PostMonkey('your_api_key')
    pm.ping() # returns u"Everything's Chimpy!"
```

If the MailChimp method call accepts parameters, you can supply them in the form
of keyword arguments. See `Examples` for common use cases, and refer to the
[MailChimp API v1.3 official documentation](http://apidocs.mailchimp.com/api/rtfm/)
for a complete list of method calls, parameters, and response objects.

MailChimp has established guidelines/limits for API usage, so please refer
to their [FAQ](http://apidocs.mailchimp.com/api/faq/) for information.

**Note**: it is the caller's responsibility to supply valid method names and any
required parameters. If MailChimp receives an invalid request, `PostMonkey`
will raise a `postmonkey.exceptions.MailChimpException` containing the
error code and message. See
[MailChimp API v1.3 - Exceptions](http://apidocs.mailchimp.com/api/1.3/exceptions.field.php)
for additional details.


Examples
========

Create a new `PostMonkey` instance with a 10 second timeout for requests:

```python
    from postmonkey import PostMonkey
    pm = PostMonkey('your_api_key', timeout=10)
```

Get the IDs for your campaign lists:

```python
    lists = pm.lists()

    # print the ID and name of each list
    for list in lists['data']:
        print list['id'], list['name']
```

Subscribe "emailaddress" to list ID 5:

```python
    pm.listSubscribe(id=5, email_address="emailaddress")
```

Catch an exception returned by MailChimp (invalid list ID):

```python
    from postmonkey import MailChimpException
    try:
        pm.listSubscribe(id=42, email_address="emailaddress")
    except MailChimpException, e:
        print e.code  # 200
        print e.error # u'Invalid MailChimp List ID: 42'
```

Get campaign data for all "sent" campaigns:

```python
    campaigns = pm.campaigns(filters=[{'status': 'sent'}])

    # print the name and count of emails sent for each campaign
    for c in campaigns['data']:
        print c['title'], c['emails_sent']
```
