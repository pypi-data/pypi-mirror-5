dendrite, social connectivity as a library
==========================================

Barebones social connection library. Tries to not do everything so you
can do anything. Only OAuth2 currently. Python 3 compatible.

Usage
-----

Dendrite doesn't give you any models, URLS or finished views. It's up to
you to define the behaviour, URLs and models. An example using Instagram
follows.

**``models.py``**

We copy the full Instagram profile. If you don't want the full profile,
you can change the behaviour of ``OAuth2CallbackView.create_profile`` in
your views.

::

    class InstagramProfile(models.Model):
        id              = models.CharField(max_length=255, primary_key=True)
        username        = models.CharField(max_length=255, blank=True)
        full_name       = models.CharField(max_length=255, blank=True)
        profile_picture = models.URLField(blank=True)
        bio             = models.TextField(blank=True)
        website         = models.URLField(blank=True)
        user            = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='instagram_profiles')
        access_token    = models.CharField(max_length=255, blank=True)

        def __unicode__(self):
            return self.full_name

**``views.py``**

Create views to handle connection. You can customize the views to behave
differently.

::

    from dendrite.views import OAuth2Mixin, OAuth2ConnectView, OAuth2CallbackView

    from .models import InstagramProfile

    class InstagramMixin(OAuth2Mixin):
        client_id         = settings.INSTAGRAM_CLIENT_ID
        client_secret     = settings.INSTAGRAM_CLIENT_SECRET
        site              = 'https://api.instagram.com'
        authorization_url = 'https://api.instagram.com/oauth/authorize/'
        token_url         = 'https://api.instagram.com/oauth/access_token'
        redirect_uri      = 'callback' # Name or full URL

        profile_class     = InstagramProfile
        scope             = "basic"

        
    class InstagramConnectView(InstagramMixin, OAuth2ConnectView):
        pass

    class InstagramCallbackView(InstagramMixin, OAuth2CallbackView):
        def get_remote_profile(self, request, token):
            return token["user"]

**``urls.py``**

Include *your* social views into your urls.

::

    urlpatterns = patterns(
        '',
        url('^social/instagram/connect/$', InstagramConnectView.as_view(), name='connect'),
        url('^social/instagram/callback/$', InstagramCallbackView.as_view(), name='callback'),
    )

**``backends.py``**

Create an additional `authentication
backend <https://docs.djangoproject.com/en/1.5/topics/auth/customizing/#other-authentication-sources>`_
that uses ``InstagramProfile``.

``DendriteBackend`` objects receive the profile class and the full
profile information returned by
``InstagramCallbackView.get_remote_profile``.

::

    from dendrite.backends import DendriteBackend

    from .models import InstagramProfile

    class InstagramBackend(DendriteBackend):
        profile_class = InstagramProfile

**``settings.py``**

Adding API keys and authentication backend.

::

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'app.InstagramBackend',

    )

    INSTAGRAM_CLIENT_ID = os.environ.get('INSTAGRAM_CLIENT_ID', '')
    INSTAGRAM_CLIENT_SECRET = os.environ.get('INSTAGRAM_CLIENT_SECRET, '')

