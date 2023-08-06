from __future__ import unicode_literals
from __future__ import absolute_import

import logging
from pypuppetdb.utils import json_to_datetime

log = logging.getLogger(__name__)


class Event(object):
    """This object represents an event.

    :param node: The hostname of the node this event fired on.
    :param status: The status for the event.
    :param timestamp: A timestamp of when this event occured.
    :param hash\_: The hash of this event.
    :param title: The resource title this event was fired for.
    :param property\_: The property of the resource this event was fired for.
    :param message: A message associated with this event.
    :param new_value: The new value/state of the resource.
    :param old_value: The old value/state of the resource.
    :param type\_: The type of the resource this event fired for.

    :ivar status: A :obj:`string` of this event's status.
    :ivar failed: The :obj:`bool` equivalent of `status`.
    :ivar timestamp: A :obj:`datetime.datetime` of when this event happend.
    :ivar node: The hostname of the machine this event\
            occured on.
    :ivar hash\_: The hash of this event.
    :ivar item: :obj:`dict` with information about the item/resource this\
            event was triggered for.
    """
    def __init__(self, node, status, timestamp, hash_, title, property_,
                 message, new_value, old_value, type_):
        self.node = node
        self.status = status
        if self.status == 'failure':
            self.failed = True
        else:
            self.failed = False
        self.timestamp = json_to_datetime(timestamp)
        self.hash_ = hash_
        self.item = {}
        self.item['title'] = title
        self.item['type'] = type_
        self.item['property'] = property_
        self.item['message'] = message
        self.item['old'] = old_value
        self.item['new'] = new_value
        self.__string = '{0}[{1}]/{2}'.format(self.item['type'],
                                              self.item['title'],
                                              self.hash_)

    def __repr__(self):
        return str('Event: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}').format(self.__string)

    def __unicode__(self):
        return self.__string


class Report(object):
    """This object represents a report.

    :param node: The hostname of the node this report originated on.
    :param hash\_: A string uniquely identifying this report.
    :param start: The start time of the agent run.
    :type start: :obj:`string` formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param end: The time the agent finished its run.
    :type end: :obj:`string` formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param received: The time PuppetDB received the report.
    :type received: :obj:`string` formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param version: The catalog / configuration version.
    :type version: :obj:`string`
    :param format\_: The catalog format version.
    :type format\_: :obj:`int`
    :param agent_version: The Puppet agent version.
    :type agent_version: :obj:`string`

    :ivar node: The hostname this report originated from.
    :ivar hash\_: Unique identifier of this report.
    :ivar start: :obj:`datetime.datetime` when the Puppet agent run started.
    :ivar end: :obj:`datetime.datetime` when the Puppet agent run ended.
    :ivar received: :obj:`datetime.datetime` when the report finished\
            uploading.
    :ivar version: :obj:`string` catalog configuration version.
    :ivar format\_: :obj:`int` catalog format version.
    :ivar agent_version: :obj:`string` Puppet Agent version.
    :ivar run_time: :obj:`datetime.timedelta` of **end** - **start**.

    """
    def __init__(self, node, hash_, start, end, received, version,
                 format_, agent_version):

        self.node = node
        self.hash_ = hash_
        self.start = json_to_datetime(start)
        self.end = json_to_datetime(end)
        self.received = json_to_datetime(received)
        self.version = version
        self.format_ = format_
        self.agent_version = agent_version
        self.run_time = self.end - self.start
        self.__string = '{0}'.format(self.hash_)

    def __repr__(self):
        return str('Report: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}').format(self.__string)

    def __unicode__(self):
        return self.__string


class Fact(object):
    """his object represents a fact.

    :param node: The hostname this fact was collected from.
    :param name: The fact's name, such as 'osfamily'
    :param value: The fact's value, such as 'Debian'

    :ivar node: :obj:`string` holding the hostname.
    :ivar name: :obj:`string` holding the fact's name.
    :ivar value: :obj:`string` holding the fact's value.
    """
    def __init__(self, node, name, value):
        self.node = node
        self.name = name
        self.value = value
        self.__string = '{0}/{1}'.format(self.name, self.node)

    def __repr__(self):
        return str('Fact: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}').format(self.__string)

    def __unicode__(self):
        return self.__string


class Resource(object):
    """This object represents a resource.

    :param node: The hostname this resource is located on.
    :param name: The name of the resource in the Puppet manifest.
    :param type\_: Type of the Puppet resource.
    :param tags: Tags associated with this resource.
    :type tags: :obj:`list`
    :param exported: If it's an exported resource.
    :type exported: :obj:`bool`
    :param sourcefile: The Puppet manifest this resource is declared in.
    :param sourceline: The line this resource is declared at.
    :param parameters: The parameters this resource has been declared with.
    :type parameters: :obj:`dict`

    :ivar node: The hostname this resources is located on.
    :ivar name: The name of the resource in the Puppet manifest.
    :ivar type\_: The type of Puppet resource.
    :ivar exported: :obj:`bool` if the resource is exported.
    :ivar sourcefile: The Puppet manifest this resource is declared in.
    :ivar sourceline: The line this resource is declared at.
    :ivar parameters: :obj:`dict` with key:value pairs of parameters.
    """
    def __init__(self, node, name, type_, tags, exported, sourcefile,
                 sourceline, parameters={}):
        self.node = node
        self.name = name
        self.type_ = type_
        self.tags = tags
        self.exported = exported
        self.sourcefile = sourcefile
        self.sourceline = sourceline
        self.parameters = parameters
        self.__string = '{0}/{1}'.format(self.name, self.node)

    def __repr__(self):
        return str('<Resource: {0}>').format(self.__string)

    def __str__(self):
        return str('{0}').format(self.__string)

    def __unicode__(self):
        return self.__string


class Node(object):
    """This object represents a node. It additionally has some helper methods
    so that you can query for resources or facts directly from the node scope.

    :param api: API object.
    :param name: Hostname of this node.
    :param deactivated: (default `None`) Time this node was deactivated at.
    :type deactivated: :obj:`string` formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param report_timestamp: (default `None`) Time of the last report.
    :type report_timestamp: :obj:`string` formatted as\
            ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param catalog_timestamp: (default `None`) Time the last time a catalog\
            was compiled.
    :type catalog_timestamp: :obj:`string` formatted as\
            ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param facts_timestamp: (default `None`) Time the last time facts were\
            collected.
    :type facts_timestamp: :obj:`string` formatted as\
            ``%Y-%m-%dT%H:%M:%S.%fZ``

    :ivar name: Hostname of this node.
    :ivar deactivated: :obj:`datetime.datetime` when this host was\
            deactivated or `False`.
    :ivar report_timestamp: :obj:`datetime.datetime` when the last run\
            occured or `None`.
    :ivar catalog_timestamp: :obj:`datetime.datetime` last time a catalog was\
            compiled or `None`.
    :ivar facts_timestamp: :obj:`datetime.datetime` last time when facts were\
            collected or `None`.
    """
    def __init__(self, api, name, deactivated=None, report_timestamp=None,
                 catalog_timestamp=None, facts_timestamp=None):
        self.name = name

        if deactivated is not None:
            self.deactivated = json_to_datetime(deactivated)
        else:
            self.deactivated = False
        if report_timestamp is not None:
            self.report_timestamp = json_to_datetime(report_timestamp)
        else:
            self.report_timestamp = report_timestamp
        if facts_timestamp is not None:
            self.facts_timestamp = json_to_datetime(facts_timestamp)
        else:
            self.facts_timestamp = facts_timestamp
        if catalog_timestamp is not None:
            self.catalog_timestamp = json_to_datetime(catalog_timestamp)
        else:
            self.catalog_timestamp = catalog_timestmap

        self.__api = api
        self.__query_scope = '["=", "certname", "{0}"]'.format(self.name)
        self.__string = self.name

    def __repr__(self):
        return str('<Node: {0}>').format(self.__string)

    def __str__(self):
        return str('{0}').format(self.__string)

    def __unicode__(self):
        return self.__string

    def facts(self):
        """Get all facts of this node."""
        return self.__api.facts(query=self.__query_scope)

    def fact(self, name):
        """Get a single fact from this node."""
        facts = self.__api.facts(name=name, query=self.__query_scope)
        return next(fact for fact in facts)

    def resources(self, type_=None):
        """Get all resources of this node or all resources of the specified
        type."""
        if type_ is None:
            resources = self.__api.resources(query=self.__query_scope)
        else:
            resources = self.__api.resources(type_=type_,
                                             query=self.__query_scope)
        return resources

    def resource(self, type_, title):
        """Get a resource matching the supplied type and title."""
        resources = self.__api.resources(type_=type_, title=title,
                                         query=self.__query_scope)
        return next(resource for resource in resources)

    def reports(self):
        """Get all reports for this node."""
        return self.__api.reports(self.__query_scope)
