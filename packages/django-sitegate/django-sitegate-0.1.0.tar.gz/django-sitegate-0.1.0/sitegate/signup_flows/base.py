from django.shortcuts import redirect

from ..flows_base import FlowsBase
from ..signals import sig_user_signup_success, sig_user_signup_fail


class SignupFlow(FlowsBase):
    """Base class for signup flows."""

    flow_type = 'signup'
    auto_login = True

    def handle_form_valid(self, request, form):
        flow_name = self.get_flow_name()
        signup_result = self.add_user(request, form)
        if signup_result:
            sig_user_signup_success.send(self, signup_result=signup_result, flow=flow_name, request=request)
            auto_login = self.flow_args.pop('auto_login', self.auto_login)
            if auto_login:
                self.sign_in(request, form, signup_result)
            redirect_to = self.flow_args.pop('redirect_to', self.redirect_to)
            if redirect_to:  # TODO Handle lambda variant with user as arg.
                return redirect(redirect_to)
        else:
            sig_user_signup_fail.send(self, signup_result=signup_result, flow=flow_name, request=request)

    def add_user(self, request, form):
        """Adds (creates) user using form data."""
        raise NotImplementedError('Please implement `add_user()` method in your `%s` class.' % self.__class__.__name__)

    def sign_in(self, request, form, signup_result):
        """Signs in a user."""
        raise NotImplementedError('Please implement `login()` method in your `%s` class.' % self.__class__.__name__)
