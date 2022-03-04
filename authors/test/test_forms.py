
from django.test import SimpleTestCase

from ..forms import RegisterUserForm

class TestRegisterUserForm(SimpleTestCase):


    def setUp(self):
        form = RegisterUserForm()
        self.username_field = form['username'].field
        self.password_field = form['password1'].field
        self.password2_field = form['password2'].field

    def test_username_field_attrs(self):
        self.assertEqual(
            "widget_style user_form_input",
            self.username_field.widget.attrs['class']
        )

    def test_password_field_attrs(self):
        self.assertEqual(
            "widget_style user_form_input",
            self.password_field.widget.attrs['class']
        )

    def test_password2_field_attrs(self):
        self.assertEqual(
            "widget_style user_form_input",
            self.password2_field.widget.attrs['class']
        )
        self.assertTrue(self.password2_field.widget.attrs['disabled'])
