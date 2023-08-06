from __future__ import unicode_literals
from __future__ import absolute_import

import logging

from pypuppetdb.api import BaseAPI
from pypuppetdb.errors import DoesNotComputeError
from pypuppetdb.utils import experimental
from pypuppetdb.types import (
    Node, Fact, Resource,
    Report, Event,
    )

log = logging.getLogger(__name__)


class API(BaseAPI):
    """The API object for version 2 of the PuppetDB API. This object contains
    all v2 specific methods and ways of doing things.

    :param experimental: (optional) Enable experimental features of the API.
    :type experimental: :obj:`bool`
    :param \*\*kwargs: Rest of the keywoard arguments passed on to our parent\
            :class:`~pypuppetdb.api.BaseAPI`.
    """

    def __init__(self, experimental=False, **kwargs):
        """Initialise the API object. We hold on to experimental ourselves
        and pass the rest on to our parent object, BaseAPI. Additionally we
        add a v2 specific endpoint to the list of endpoints."""
        super(API, self).__init__(api_version=2, **kwargs)
        self.experimental = experimental
        self.endpoints['fact-names'] = 'fact-names'
        log.debug('API initialised with {0} and experimental set '
                  'to {1}'.format(kwargs, experimental))

    def node(self, name):
        """Gets a single node from PuppetDB."""
        nodes = self.nodes(name=name)
        return next(node for node in nodes)

    def nodes(self, name=None, query=None):
        """Query for nodes by either name or query. If both aren't
        provided this will return a list of all nodes.

        :param name: (optional)
        :type name: :obj:`None` or :obj:`string`
        :param query: (optional)
        :type query: :obj:`None` or :obj:`string`

        :returns: A generator yieling Nodes.
        :rtype: :class:`pypuppetdb.types.Node`
        """

        nodes = self._query('nodes', path=name, query=query)
        # If we happen to only get one node back it
        # won't be inside a list so iterating over it
        # goes boom. Therefor we wrap a list around it.
        if type(nodes) == dict:
            log.debug("Request returned a single node.")
            nodes = [nodes, ]

        for node in nodes:
            yield Node(self,
                       node['name'],
                       deactivated=node['deactivated'],
                       report_timestamp=node['report_timestamp'],
                       catalog_timestamp=node['catalog_timestamp'],
                       facts_timestamp=node['facts_timestamp'],
                       )

    def facts(self, name=None, value=None, query=None):
        """Query for facts limited by either name, value and/or query.
        This will yield a single Fact object at a ti."""

        log.debug('{0}, {1}, {2}'.format(name, value, query))
        if name is not None and value is not None:
            path = '{0}/{1}'.format(name, value)
        elif name is not None and value is None:
            path = name
        else:
            log.debug("We want to query for all facts.")
            path = None

        facts = self._query('facts', path=path, query=query)
        for fact in facts:
            yield Fact(
                fact['certname'],
                fact['name'],
                fact['value'],
                )

    def fact_names(self):
        """Get a list of all known facts."""

        return self._query('fact-names')

    def resources(self, type_=None, title=None, query=None):
        """Query for resources limited by either type and/or title or query.
        This will yield a Resources object for every returned resource."""

        # Need to capitalize the resource type since PuppetDB doesn't
        # answer to lower case type names.
        # bugs.puppetlabs.com/some_value
        type_ = type_.capitalize()
        if type_ is not None and title is not None:
            path = '{0}/{1}'.format(type_, title)
        elif type_ is not None and title is None:
            path = type_
        else:
            log.debug('Going to query for all resources. This is usually a '
                      'bad idea as it might return enormous amounts of '
                      'resources.')
            path = None

        resources = self._query('resources', path=path, query=query)
        for resource in resources:
            yield Resource(
                resource['certname'],
                resource['title'],
                resource['type'],
                resource['tags'],
                resource['exported'],
                resource['sourcefile'],
                resource['sourceline'],
                resource['parameters'],
                )

    @experimental
    def reports(self, query):
        """Get reports for our infrastructure. Currently reports can only
        be filtered through a query which requests a specific certname.
        If not it will return all reports.

        This yields a Report object for every returned report."""
        reports = self._query('reports', query=query)
        for report in reports:
            yield Report(
                report['certname'],
                report['hash'],
                report['start-time'],
                report['end-time'],
                report['receive-time'],
                report['configuration-version'],
                report['report-format'],
                report['puppet-version'],
                )

    @experimental
    def events(self, query):
        """A report is made up of events. This allows to query for events
        based on the reprt hash.
        This yields an Event object for every returned event."""

        events = self._query('events', query=query)
        for event in events:
            yield Event(
                event['certname'],
                event['status'],
                event['timestamp'],
                event['report'],
                event['resource-title'],
                event['property'],
                event['message'],
                event['new-value'],
                event['old-value'],
                event['resource-type'],
                )
