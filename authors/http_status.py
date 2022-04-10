
from http import HTTPStatus

from django.http import HttpResponseRedirect

class SeeOtherHTTPRedirect(HttpResponseRedirect):

    status_code = HTTPStatus.SEE_OTHER
