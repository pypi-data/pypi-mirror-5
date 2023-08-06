# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base import QueryOperation
from params import SingleParam, StaticParam
from utils import OperationExample


#class GetFeedbackV4(QueryOperation):
#    """
#    This API is no longer available (on en or de wikipedia).  As of
#    3/9/2013, this API does not even appear in the documentation at:
#    http://en.wikipedia.org/w/api.php
#    """
#    field_prefix = 'af'
#    input_field = SingleParam('pageid')
#    fields = [StaticParam('list', 'articlefeedback')]
#    output_type = list
#
#    def extract_results(self, query_resp):
#        ret = query_resp['articlefeedback'][0].get('ratings', [])
#        return ret


_FV5_KNOWN_FILTERS = ['*', 'featured', 'unreviewed', 'helpful', 'unhelpful',
                      'flagged', 'useful', 'resolved', 'noaction',
                      'inappropriate', 'archived', 'allcomment', 'hidden',
                      'requested', 'declined', 'oversighted', 'all']


class GetFeedbackV5(QueryOperation):
    """
    article feedback v5 breaks standards in a couple ways.
      * the various v5 APIs use different prefixes (af/afvf)
      * it doesn't put its results under 'query', requiring a custom
      post_process_response()
    """
    field_prefix = 'afvf'
    input_field = SingleParam('pageid')
    fields = [StaticParam('list', 'articlefeedbackv5-view-feedback'),
              SingleParam('filter', default='featured')]
    output_type = list
    examples = [OperationExample('604727')]

    def post_process_response(self, response):
        if not response.results:
            return {}
        return dict(response.results)

    def extract_results(self, query_resp):
        count = query_resp['articlefeedbackv5-view-feedback']['count']
        return ['TODO'] * int(count)
