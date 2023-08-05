# django-salesforce
#
# by Phil Christensen
# (c) 2012-2013 Freelancers Union (http://www.freelancersunion.org)
# See LICENSE.md for details
#

"""
Salesforce object manager.

Use a custom QuerySet to generate SOQL queries and results.
"""

from django.db import connections
from django.db.models import manager

from salesforce import router

class SalesforceManager(manager.Manager):
	use_for_related_fields = True
	
	def get_query_set(self):
		"""
		Returns a QuerySet which access remote SF objects.
		"""
		if router.is_testing(self.db):
			return super(SalesforceManager, self).get_query_set()
		else:
			from salesforce.backend import query, compiler
			q = query.SalesforceQuery(self.model, where=compiler.SalesforceWhereNode)
			return query.SalesforceQuerySet(self.model, query=q, using=self.db)

