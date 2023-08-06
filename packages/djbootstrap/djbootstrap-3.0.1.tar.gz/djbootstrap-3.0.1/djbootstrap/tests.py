
from django import forms
from django import template
from django import test

from djbootstrap.templatetags.bootstrap_tags import activate, bootstrapped_form

class ActivateTemplateTagTests(test.TestCase):

    def test_returns_active_when_request_is_same_path(self):
        t = template.Template("""
            {% load bootstrap_tags %}

            <a href="/my/path/" class="{% activate '/my/path/' %}">Nav Tab</a>
        """)
        request = test.RequestFactory().get('/my/path/')
        context = template.RequestContext(request)
        response = t.render(context)
        self.assertEqual('<a href="/my/path/" class="active">Nav Tab</a>', response.strip())

    def test_returns_empty_string_when_nav_tab_is_not_current_request(self):
        t = template.Template("""
            {% load bootstrap_tags %}

            <a href="/home/page/" class="{% activate '/home/page/' %}">Nav Tab</a>
        """)
        request = test.RequestFactory().get('/other/path/')
        context = template.RequestContext(request)
        response = t.render(context)
        self.assertEqual('<a href="/home/page/" class="">Nav Tab</a>', response.strip())

    def test_returns_empty_string_when_doesnt_have_request_context(self):
        context = template.Context({})
        result = activate(context, "/")
        self.assertEqual("", result)


class TestForm(forms.Form):
    one = forms.CharField(max_length=10)


class BootstrapFormTests(test.TestCase):

    def test_returns_dict_of_form(self):
        f = TestForm()
        self.assertEqual({'form': f}, bootstrapped_form(f))


