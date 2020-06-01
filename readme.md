To use the War Dragons API, please follow these directions. This API is in **_BETA_** and may change or even disappear without notice. The API may not be used by paid apps or sites.


# Getting Started

The simplest way to use the API is to just make API calls for your own player. Let's dive in!


## Creating an Application

First create a developer account and register an application to use the API:

1. [Register for a War Dragons Developer Account](https://api-dot-pgdragonsong.appspot.com/api/console/login) using your Pocket ID.
1. Verify your e-mail address by clicking the link in a confirmation e-mail you should receive.
1. [Register your Application](https://api-dot-pgdragonsong.appspot.com/api/console/apps) (the confirmation e-mail should take you here). You can omit the server URL if you only want to use the API for your own player.

***


# Building an Application for Other Players

If you only want to use the API for yourself, then you don't need to go any further. But if you'd like to create a website or app for other players, then you'll need to learn how to get permission from other players. This will allow your app to use the API on behalf of other players (e.g., maybe your site helps players plan attacks from their castles).

## Authentication Flow Overview

War Dragons API requests are always made on behalf of a player. That player could be the creator of an application which uses the War Dragons API, or other players who grant an application permission to use the API on their behalf. This uses the standard [OAuth2](https://www.digitalocean.com/community/tutorials/an-introduction-to-oauth-2) flow.

1. You create an application which uses the War Dragons API (see below).
1. A user comes to your site.
1. Your applications directs them to a War Dragons page to authenticate their identity. This page redirects to your server with an `auth_code`.
1. Your application uses its `client_secret` and the `auth_code` to retrieve an API Key from the War Dragons API. This API Key can be used to make API calls on behalf of the player who authenticated.


### Ask permission
To ask a user to give your application permission to make API calls on their behalf, send them to:
    https://api-dot-pgdragonsong.appspot.com/api/authorize?client_id=YOURCLIENTID&scopes=atlas.read,player.public.read

The `scopes` query string parameter tells the player and War Dragons which kinds of APIs you'd like access to. Right now, there are only these two scopes.


### Receive permission
If the player chooses to grant you API access, then your application will be sent a request to the `auth_url` you created when you registered the application. The HTTP request to your `auth_url` will include a two query string parameters:
    1. `auth_code` - a unique code your application (and only your application) can use to retrieve an API Key to access the War Dragons API on behalf of the user who just granted your application permission.
    1. `player_id` - the unique ID of the player who just granted your application permission.


### Retrieve API Key
After your application receives permission, you need to use the `auth_code` to retrieve an API Key. The API Key can be used to make requests on behalf of the player who granted you permission. Each player who grants your application permission will have a unique API Key. API keys will cease to work if your application is disabled, the player is banned, or the player revokes permission for your application. To retrieve the API key, make a request for:

    https://api-dot-pgdragonsong.appspot.com/api/dev/retrieve_token?auth_code=AUTHCODE&client_id=CLIENT_ID&client_secret=CLIENT_SECRET

You can find the client ID and client secret on [your developer console](https://api-dot-pgdragonsong.appspot.com/api/console/). The response body will be JSON-encoded and include the `api_key` field.

Once you have a player's API Key, store it (you should not ask for it more than once).


### Authenticating requests
Once you have an app and a player's API Key, you can authenticate requests. In order to do so, you must provide the following headers:

    X-WarDragons-APIKey: [key of player using your app]
    X-WarDragons-Request-Timestamp: [timestamp of request, should be standard epoch in seconds]
    X-WarDragons-Signature: [signature of request]
    
The Signature will be defined as the base64 encoding of sha256 on 

    [your client secret] + ':' + [X-WarDragons-APIKey] + ':' + [X-WarDragons-Request-Timestamp] 

# Demo Application

This GitHub project is intended to serve as a simple reference example of how to create an application which authenticates users and enables them to interact with the War Dragons API through your site or app. It includes just three HTTP URLs:

 * /auth_callback - This is the URL path we input when registering our War Dragons API application.
 * /authorize - This is a simple handler to ask a player for their permission to call APIs on their behalf.
 * /.* - All other requests are interpreted as requests to the API. For ease of use, it also accepts the API Key as a query string parameter (instead of a header).


To test it out:

1. Go to [https://war-dragons-api-demo.appspot.com/authorize](https://war-dragons-api-demo.appspot.com/authorize) and signin to get your API Key. Be sure to copy it to your computer!
1. Try calling an API through the demo app by using the following URL (but fill in your API Key!): https://war-dragons-api-demo.appspot.com/player/public/my_profile?apikey=PASTE_YOUR_KEY_HERE
