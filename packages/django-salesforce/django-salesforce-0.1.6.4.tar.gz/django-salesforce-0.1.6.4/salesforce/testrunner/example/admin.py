# django-salesforce
#
# by Phil Christensen
# (c) 2012-2013 Freelancers Union (http://www.freelancersunion.org)
# See LICENSE.md for details
#

from django.contrib import admin
from django.db import models
from django.forms import widgets
from django.http import HttpResponse

from salesforce.testrunner.example import models
from salesforce.admin import RoutedModelAdmin

class AccountAdmin(RoutedModelAdmin):
	list_display = ('Salutation', 'FirstName', 'LastName', 'PersonEmail')
admin.site.register(models.Account, AccountAdmin)
