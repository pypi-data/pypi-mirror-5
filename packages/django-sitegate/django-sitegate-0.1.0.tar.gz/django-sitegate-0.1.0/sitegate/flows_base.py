from django import forms
from collections import OrderedDict

from django.contrib.auth import authenticate, login

from .utils import apply_attrs_to_form_widgets


class FlowsBase(object):
    """Base class for signup and sign in flows."""

    flow_type = None
    form_template = 'sitegate/%s/form_as_p.html'
    redirect_to = '/'

    def __init__(self, **kwargs):
        if not getattr(self, 'form', False):
            raise NotImplementedError('Please define `form` attribute in your `%s` class.' % self.__class__.__name__)
        # Build default template real path.
        self.form_template = self.form_template % self.flow_type
        self.flow_args = kwargs

    def handle_form_valid(self, request, form):
        """"""
        raise NotImplementedError('Please implement `handle_form_valid` method in your `%s` class.' % self.__class__.__name__)

    def process_request(self, request, view_function, *args, **kwargs):
        """Makes the given request ready to handle sign ups and handles them."""

        form = self.get_requested_form(request)
        if form.is_valid():
            result = self.handle_form_valid(request, form)
            if result:
                return result

        self.update_request(request, form)
        return view_function(request, *args, **kwargs)

    def update_request(self, request, form):
        """Updates Request object with flows forms."""
        forms_key = '%s_forms' % self.flow_type

        # Use ordered forms dict in case _formNode wants to fetch the first defined.
        flow_dict = OrderedDict()
        try:
            flow_dict = request.sitegate[forms_key]
        except AttributeError:
            request.sitegate = {}
        except KeyError:
            pass

        flow_dict[self.get_flow_name()] = form
        request.sitegate[forms_key] = flow_dict

    @classmethod
    def get_flow_name(cls):
        """Returns sign up flow identifier from flow class name.
        Example: `classic` for `ClassicSignup`.

        """
        return cls.__name__

    @staticmethod
    def login_generic(request, username, password):
        """Helper method. Generic login with username and password."""
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return True
        return False

    def get_requested_form(self, request):
        """Returns an instance of a form requested."""
        flow_name = self.get_flow_name()
        flow_key = '%s_flow' % self.flow_type
        form_data = None

        if request.method == 'POST' and request.POST.get(flow_key, False) and request.POST[flow_key] == flow_name:
            form_data = request.POST

        form = self.init_form(form_data, widget_attrs=self.flow_args.pop('widget_attrs', None), template=self.flow_args.pop('template', None))
        # Attach flow identifying field to differentiate among several possible forms.
        form.fields[flow_key] = forms.CharField(required=True, initial=flow_name, widget=forms.HiddenInput)
        return form

    def init_form(self, form_data, widget_attrs=None, template=None):
        """Constructs, populates and returns a form."""
        form = self.form(data=form_data)
        if template is not None:
            form.template = template
        else:
            form.template = self.form_template
        if widget_attrs is not None:
            apply_attrs_to_form_widgets(form, widget_attrs)
        return form
