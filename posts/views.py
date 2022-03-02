
from django.views.generic.base import TemplateView

from .forms import SearchForm

# Create your views here.

class Page(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['search_form'] = SearchForm()
        return context



class QuestionListingPage(Page):

    template_name = "posts/main.html"
    extra_context = {
        "title": "Top Questions",
        "query_buttons": ["Interesting", "Hot", "Week", "Month"]
    }
