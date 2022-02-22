
from django.views.generic.base import TemplateView

# Create your views here.


class QuestionListingPage(TemplateView):

    template_name = "posts/home_questions.html"
    extra_context = {
        "title": "All Questions",
        "query_buttons": ["Interesting", "Hot", "Week", "Month"]
    }
