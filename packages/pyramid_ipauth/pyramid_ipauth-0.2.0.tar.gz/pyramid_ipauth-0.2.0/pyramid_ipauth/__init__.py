# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
"""
IP-based authentication policy for pyramid.
"""

__ver_major__ = 0
__ver_minor__ = 2
__ver_patch__ = 0
__ver_sub__ = ""
__ver_tuple__ = (__ver_major__, __ver_minor__, __ver_patch__, __ver_sub__)
__version__ = "%d.%d.%d%s" % __ver_tuple__


from zope.interface import implements

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.settings import aslist
from pyramid.path import DottedNameResolver

from pyramid_ipauth.utils import make_ip_set, check_ip_address, get_ip_address


class IPAuthenticationPolicy(object):
    """An IP-based authentication policy for pyramid.

    This pyramid authentication policy assigns userid and/or effective
    principals based on the originating IP address of the request.

    You must specify a set of IP addresses against which to match, and may
    specify a userid and/or list of principals to apply.  For example, the
    following would authenticate all requests from the 192.168.0.* range as
    userid "myuser":

        IPAuthenticationPolicy(["192.168.0.0/24"], "myuser")

    The following would not authenticate as a particular userid, but would add
    "local" as an effective principal for the request (along with Everyone
    and Authenticated):

        IPAuthenticationPolicy(["127.0.0.0/24"], principals=["local"])

    By default this policy does not respect the X-Forwarded-For header since
    it can be easily spoofed.  If you want to respect X-Forwarded-For then you
    must specify a list of trusted proxies, and only forwarding declarations
    from these proxies will be respected:

        IPAuthenticationPolicy(["192.168.0.0/24"], "myuser",
                               proxies=["192.168.0.2"])
                               
    Instead of given the IP addresses, userid and principals at configuration time.
    we can also compute these at runtime.

        def get_userid(ipaddr):
            "compute a userid based on the request"
            if str(ipaddr).startswith('192'):
                return 'LAN-user'
            return 'WAN-user'
        def get_principals(userid, ipaddr):
            "return a list of principals"
            if userid == 'WAN-user':
                return ['view']
            if userid == 'LAN-user':
                return ['view', 'edit']
            return []
        IPAuthenticationPolicy(get_userid=get_userid, get_principals=get_principals)

    """

    implements(IAuthenticationPolicy)

    def __init__(self, ipaddrs, userid=None, principals=None, proxies=None, get_userid=None, get_principals=None):
        r = DottedNameResolver()
        self.get_userid = r.maybe_resolve(get_userid)
        self.get_principals = r.maybe_resolve(get_principals)
        self.ipaddrs = make_ip_set(ipaddrs)
        self.userid = userid
        if isinstance(principals, basestring):
            self.principals = aslist(principals)
        else:
            self.principals = principals
        self.proxies = make_ip_set(proxies)

    @classmethod
    def from_settings(cls, settings={}, prefix="ipauth.", **kwds):
        """Construct an IPAuthenticationPolicy from deployment settings."""
        # Grab out all the settings keys that start with our prefix.
        ipauth_settings = {}
        for name, value in settings.iteritems():
            if not name.startswith(prefix):
                continue
            ipauth_settings[name[len(prefix):]] = value
        # Update with any additional keyword arguments.
        ipauth_settings.update(kwds)
        # Now look for specific keys of interest.
        ipaddrs = ipauth_settings.get("ipaddrs", "")
        userid = ipauth_settings.get("userid", None)
        principals = aslist(ipauth_settings.get("principals", ""))
        proxies = ipauth_settings.get("proxies", None)
        get_userid = ipauth_settings.get("get_userid", None)
        get_principals = ipauth_settings.get("get_principals", None)
        # The constructor uses make_ip_set to parse out strings,
        # so we're free to just pass them on in.
        return cls(ipaddrs, userid, principals, proxies, get_userid, get_principals)

    def authenticated_userid(self, request):
        return self.unauthenticated_userid(request)

    def unauthenticated_userid(self, request):
        if not check_ip_address(request, self.ipaddrs, self.proxies):
            return None
        if self.get_userid is not None:
            userid = self.get_userid(get_ip_address(request, self.proxies))
        else:
            userid = self.userid
        return userid

    def effective_principals(self, request):
        principals = [Everyone]
        if not check_ip_address(request, self.ipaddrs, self.proxies):
            return principals
        
        if self.get_userid is not None:
            userid = self.get_userid(get_ip_address(request, self.proxies))
        else:
            userid = self.userid

        if userid is not None:
            principals.insert(0, userid)
            principals.append(Authenticated)
            
        if self.get_principals is not None:
            addr = get_ip_address(request, self.proxies)
            principals.extend(self.get_principals(userid, addr))
        elif self.principals is not None:
            principals.extend(self.principals)
                
        return principals

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []


def includeme(config):
    """Include default ipauth settings into a pyramid config.

    This function provides a hook for pyramid to include the default settings
    for ip-based auth.  Activate it like so:

        config.include("pyramid_ipauth")

    This will activate an IPAuthenticationPolicy instance with settings taken
    from the the application settings as follows:

        * ipauth.ipaddrs:     list of ip addresses to authenticate
        * ipauth.userid:      the userid as which to authenticate
        * ipauth.principals:  additional principals as which to authenticate
        * ipauth.proxies:     list of ip addresses to trust as proxies
        * ipauth.get_userid:    a (dotted name to a) callable which receive 
                                the ip address to compute the userid
        * ipauth.get_principals:    a (dotted name to a) callable which receive 
                                the ip address to compute the principals

    IP addresses can be specified in a variety of formats, including single
    addresses ("1.2.3.4"), networks ("1.2.3.0/16"), and globs ("1.2.3.*").
    You can also provide a whitespace-separated list of addresses to handle
    discontiguous ranges.
    """
    # Grab the pyramid-wide settings, to look for any auth config.
    settings = config.get_settings().copy()
    # Hook up a default AuthorizationPolicy.
    # ACLAuthorizationPolicy is usually what you want.
    # If the app configures one explicitly then this will get overridden.
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    # Use the settings to construct an AuthenticationPolicy.
    authn_policy = IPAuthenticationPolicy.from_settings(settings)
    config.set_authentication_policy(authn_policy)
