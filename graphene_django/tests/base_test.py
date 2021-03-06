import json

from django.http import HttpResponse
from django.test import Client
from django.test import TestCase


class GraphQLTestCase(TestCase):
    """
    Based on: https://www.sam.today/blog/testing-graphql-with-graphene-django/
    """

    # URL to graphql endpoint
    GRAPHQL_URL = '/graphql/'
    # Here you need to set your graphql schema for the tests
    GRAPHQL_SCHEMA = None

    @classmethod
    def setUpClass(cls):
        super(GraphQLTestCase, cls).setUpClass()

        if not cls.GRAPHQL_SCHEMA:
            raise AttributeError('Variable GRAPHQL_SCHEMA not defined in GraphQLTestCase.')

        cls._client = Client(cls.GRAPHQL_SCHEMA)

    def query(self, query, op_name=None, input_data=None):
        """
        Args:
            query (string)    - GraphQL query to run
            op_name (string)  - If the query is a mutation or named query, you must
                                supply the op_name.  For annon queries ("{ ... }"),
                                should be None (default).
            input_data (dict) - If provided, the $input variable in GraphQL will be set
                                to this value

        Returns:
            Response object from client
        """
        body = {'query': query}
        if op_name:
            body['operation_name'] = op_name
        if input_data:
            body['variables'] = {'input': input_data}

        resp = self._client.post(self.GRAPHQL_URL, json.dumps(body),
                                 content_type='application/json')
        return resp

    def assertResponseNoErrors(self, resp):
        """
        Assert that the call went through correctly. 200 means the syntax is ok, if there are no `errors`,
        the call was fine.
        :resp HttpResponse: Response
        """
        content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('errors', list(content.keys()))

    def assertResponseHasErrors(self, resp):
        """
        Assert that the call was failing. Take care: Even with errors, GraphQL returns status 200!
        :resp HttpResponse: Response
        """
        content = json.loads(resp.content)
        self.assertIn('errors', list(content.keys()))
