import os
from pyramid.httpexceptions import HTTPFound
from pyramid_simpleform.renderers import FormRenderer
from factored.utils import CombinedDict
import urllib
from factored.plugins import getFactoredPlugin, getFactoredPlugins
from factored.plugins import getPluginForRequest


class AuthView(object):
    name = None
    path = None
    content_renderer = "templates/auth.pt"

    def __init__(self, req):
        self.req = req
        self.plugin = getPluginForRequest(req)
        self.allow_code_reminder = self.plugin.allow_code_reminder
        self.uform = self.plugin.uform
        self.cform = self.plugin.cform
        self.formtext = self.plugin.formtext
        self.send_submitted = self.validate_submitted = False
        self.auth_timeout = req.registry['settings']['auth_timeout']
        self.auth_remember_timeout = \
            req.registry['settings']['auth_remember_timeout']
        rto = self.auth_remember_timeout / 60
        if rto > 60:
            rto = rto / 60
            if rto > 24:
                rto = '%i days' % (rto / 24)
            else:
                rto = '%i hours' % rto
        else:
            rto = '%i minutes' % rto
        self.remember_duration = rto
        self.combined_formtext = CombinedDict(
            req.registry['formtext'], self.formtext)

    @property
    def requesting_code_reminder(self):
        return self.req.POST.get('submit', '') == self.formtext['button']['codereminder'] \
                and self.plugin.allow_code_reminder

    def send_out_code_reminder(self):
        self.validate_submitted = True
        self.cform.validate()
        self.cform.errors['code'] = self.error_code_reminder
        username = self.cform.data['username']
        user = self.plugin.get_user(username)
        if 'username' not in self.cform.errors and user is not None:
            self.plugin.send_code_reminder(user)

    @property
    def requesting_user_form(self):
        return self.req.POST.get('submit', '') == self.formtext['button']['username']

    def submit_user_form(self):
        if self.uform.validate():
            username = self.uform.data['username']
            self.cform.data['username'] = username
            user = self.plugin.get_user(username)
            if user is None:
                self.uform.errors['username'] = \
                    self.formtext['error']['invalid_username']
            else:
                self.send_submitted = True
                self.plugin.user_form_submitted_successfully(user)

    @property
    def requesting_authentication(self):
        return self.req.POST.get('submit', '') == self.formtext['button']['authenticate']

    def submit_authentication(self):
        self.validate_submitted = True
        if self.cform.validate():
            user = self.plugin.get_user(self.cform.data['username'])
            if user is None:
                self.cform.errors['code'] = \
                    self.formtext['error']['invalid_username_code']
            else:
                if self.plugin.check_code(user):
                    userid = self.cform.data['username']
                    if self.cform.data['remember']:
                        max_age = self.auth_remember_timeout
                    else:
                        max_age = self.auth_timeout
                    auth = self.req.environ['auth']
                    headers = auth.remember(userid, max_age=max_age)
                    referrer = self.cform.data.get('referrer')
                    if not referrer:
                        referrer = '/'
                    raise HTTPFound(location=referrer, headers=headers)
                else:
                    self.cform.errors['code'] = self.formtext['error']['invalid_code']
                    self.cform.data['code'] = u''

    def update_referrer(self):
        referrer = self.cform.data.get('referrer',
            self.uform.data.get('referrer', self.req.params.get('referrer', '')))
        if not referrer:
            referrer = self.req.path_url
        # strip off auth url
        parts = self.req.environ['PATH_INFO'].rsplit('/')
        referrer = referrer.rstrip('/')
        if parts[-1] == self.plugin.path and referrer.endswith(self.plugin.path):
            referrer = referrer[:-len(self.plugin.path)]
            parts.remove(self.plugin.path)
        referrer = referrer.rstrip('/')
        if referrer.endswith(parts[-1]):
            referrer = referrer[:-len(parts[-1])]
        self.uform.data.update({'referrer': referrer})
        self.cform.data.update({'referrer': referrer})

    def __call__(self):
        req = self.req
        if req.method == "POST":
            if self.requesting_code_reminder:
                self.send_out_code_reminder()
            elif self.requesting_user_form:
                self.submit_user_form()
            elif self.requesting_authentication:
                self.submit_authentication()
        self.update_referrer()
        return dict(uform=FormRenderer(self.uform),
            cform=FormRenderer(self.cform), send_submitted=self.send_submitted,
            validate_submitted=self.validate_submitted,
            content_renderer=self.content_renderer,
            formtext=self.combined_formtext,
            remember_duration=self.remember_duration)


def notfound(req):
    return HTTPFound(location="%s?%s" % (
        req.registry['settings']['base_auth_url'],
        urllib.urlencode({'referrer': req.url})))


def auth_chooser(req):
    auth_types = []
    settings = req.registry['settings']
    base_path = settings['base_auth_url']
    supported_types = settings['supported_auth_schemes']
    if len(supported_types) == 1:
        plugin = getFactoredPlugin(supported_types[0])
        referrer = urllib.urlencode(
            {'referrer': req.params.get('referrer', '')})
        raise HTTPFound(location="%s/%s?%s" % (base_path, plugin.path,
                                               referrer))
    for plugin in getFactoredPlugins():
        if plugin.name in supported_types:
            auth_types.append({
                'name': plugin.name,
                'url': os.path.join(base_path, plugin.path)
                })
    return dict(auth_types=auth_types,
                referrer=req.params.get('referrer', ''))
