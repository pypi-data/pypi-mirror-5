A simple python client for the Icelandic government authentication service Íslykill (www.islykill.is)
You must apply for access before using this library.

Usage
=====

Just remember to set the `username`, `password` and `service_id` as your own.
`service_id` is the ID you are given from the national registry of Iceland (www.skra.is), e.g. for 
www.betraisland.is the id is `betraisland.is` and the Íslykill authentication url is 
`https://innskraning.island.is/?id=betraisland.is`

    >>> import islykill
    >>> islykill.username = "Your-username-here"
    >>> islykill.password = "Your-password-here"
    >>> islykill.service_id = "dev.roddfolksins.is"
    >>> token = 'Some-received-token' # the token received from island.is
    >>> ip_address = '1.1.1.1' # remote user ip address
    >>> result = islykill.generate_saml_from_token(token, ip_address)
    >>> print result
    {'ssn': '1234567890', 'ip_address': '1.1.1.1', 'name': u'Jon Jonsson'}

If an error occurs, the result from `generate_saml_from_token` will return a dictionary with the 
key "error" with the body of the error as value, e.g.

    >>> print result
    {'error': 'HTTPError = 500'}

500 usually mean that you can make the request again immediately, just a glitch in the
webservice.

    >>> print result
    {'error': 'Unable to find SAML assertion from token.'}

"Unable to find SAML assertion from token" means that the token is invalid or expired somehow, 
which means the user has to authenticate again.