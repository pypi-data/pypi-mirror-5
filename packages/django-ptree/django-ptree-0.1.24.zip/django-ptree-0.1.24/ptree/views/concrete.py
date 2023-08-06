__doc__ = """This module contains views that are shared across many game types. 
They are ready to be included in your  Just import this module,
and include these classes in your Treatment's sequence() method."""


from django.shortcuts import render_to_response

from django.conf import settings

import ptree.views.abstract
import ptree.forms

from ptree.models.common import Symbols, PayNotYetKnownError

class ViewInThisApp(object):
    url_base = 'shared'

class RedirectToPageUserShouldBeOn(ptree.views.abstract.View, ViewInThisApp):
    """Redirect to this page when you can't do a redirect with the redirect_to_current_view method that increments the view index.
    Use cases: redirects from external websites, or from Django FormView, etc.
    """
    def get(self, request, *args, **kwargs):
        return self.redirect_to_page_the_user_should_be_on()

    @classmethod
    def url(cls):
        return '/{}/{}/'.format(cls.get_url_base(), cls.__name__)


    @classmethod
    def url_pattern(cls):
        return r'^{}/{}/$'.format(cls.get_url_base(), cls.__name__)

class RedemptionCode(ptree.views.abstract.FormView, ViewInThisApp):

    template_name = 'RedemptionCode.html'

    def get_variables_for_template(self):

        return {'redemption_code': self.participant.code,
                'base_pay': self.treatment.base_pay,
                'bonus': self.participant.bonus(),
                'total_pay': self.participant.total_pay()}