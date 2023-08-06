from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import AuthenticationForm


class CrispyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CrispyAuthenticationForm, self).__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_class = 'form-horizontal form_without_actions_decoration'
        helper.form_method = 'post'
        helper.form_action = '.'
        helper.add_input(Submit('submit', 'Ingresar'))

        self.helper = helper
