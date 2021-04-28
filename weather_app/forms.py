from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django.contrib.auth.forms import UserCreationForm

from weather_app.models import User


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'h6 font-weight-light'
        self.helper.layout = Layout(
            Fieldset(
                '',
                'email',
                'password1',
                'password2',
            ),
            ButtonHolder(
                Submit('submit', 'Sign up', css_class='btn btn-primary btn-lg btn-block'),
            ),
        )
