===================================
Mashery Authentication for Requests
===================================

Simple class for making authenticated requests to Mashery APIs using the `requests <http://python-requests.org>`_ library.


Example
=======

    import requests
    from requests_auth_mashery import MasheryAuth


    def main():
        api_key = 'EXAMPLE'
        api_secret = 'EXAMPLE'

        mashery_auth = MasheryAuth(api_key, api_secret)

        payload = {
            'entitytype': 'artist',
            'query': 'weezer',
            'format': 'json',
        }
        url = 'http://api.rovicorp.com/search/v2.1/music/search'
        r = requests.get(url, auth=mashery_auth, params=payload)

        print r.content


    if __name__ == '__main__':
        main()
