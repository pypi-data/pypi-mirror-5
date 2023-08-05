import trac.core

import trac.ticket.api
import trac.wiki.api
import trac.versioncontrol.api

import socket
import fedmsg

# If fedmsg was already initialized, let's not re-do that.
if not getattr(getattr(fedmsg, '__local', None), '__context', None):
    hostname = socket.gethostname().split('.', 1)[0]
    fedmsg.init(name="trac." + hostname)


def env2dict(env):
    """ Utility method to format the trac environment for fedmsg. """
    return dict(
        base_url=env.base_url,
        project_name=env.project_name,
        project_description=env.project_description,
        project_url=env.project_url,
        project_icon=env.project_icon,
    )


def wikipage2dict(page):
    attrs = ['version', 'time', 'author', 'text', 'comment', 'readonly']
    return dict([(attr, getattr(page, attr)) for attr in attrs])


class FedmsgPlugin(trac.core.Component):
    """ The trac fedmsg plugin.

    This plugin simply listens for trac events and
    rebroadcasts them to a fedmsg message bus.
    """
    trac.core.implements(
        trac.ticket.api.ITicketChangeListener,
        trac.wiki.api.IWikiChangeListener,
        trac.versioncontrol.api.IRepositoryChangeListener,
    )

    def publish(self, topic, **msg):
        """ Inner workhorse method.  Publish arguments to fedmsg. """
        msg['instance'] = env2dict(self.env)
        fedmsg.publish(modname='trac', topic=topic, msg=msg)

    def ticket_created(self, ticket):
        """Called when a ticket is created."""
        self.publish(topic='ticket.new', ticket=ticket.values)

    def ticket_changed(self, ticket, comment, author, old_values):
        """Called when a ticket is modified.

        `old_values` is a dictionary containing the previous values of the
        fields that have changed.
        """
        self.publish(
            topic='ticket.update',
            ticket=ticket.values,
            comment=comment,
            author=author,
            old_values=old_values,
        )

    def ticket_deleted(self, ticket):
        """Called when a ticket is deleted."""
        self.publish(topic='ticket.delete', ticket=ticket.values)

    def wiki_page_added(self, page):
        """Called whenever a new Wiki page is added."""
        self.publish(topic='wiki.page.new', page=wikipage2dict(page))

    def wiki_page_changed(self, page, version, t, comment, author, ipnr):
        """Called when a page has been modified."""
        self.publish(
            topic='wiki.page.update',
            page=wikipage2dict(page),
            version=version,
            t=t,
            comment=comment,
            author=author,
            #ipnr=ipnr,  # Don't broadcast IP addresses.  Poor form.
        )

    def wiki_page_deleted(self, page):
        """Called when a page has been deleted."""
        self.publish(topic='wiki.page.delete', page=wikipage2dict(page))

    def wiki_page_version_deleted(self, page):
        """Called when a version of a page has been deleted."""
        self.publish(topic='wiki.page.version.delete',
                     page=wikipage2dict(page))

    def wiki_page_renamed(self, page, old_name):
        """Called when a page has been renamed."""
        self.publish(
            topic='wiki.page.rename',
            page=wikipage2dict(page),
            old_name=old_name
        )

    def changeset_added(self, repos, changeset):
        """Called after a changeset has been added to a repository."""
        self.publish(
            topic='changeset.new',
            repos=[repo.name for repo in repos],
            changeset=changeset.get_properties(),
        )

    def changeset_modified(self, repos, changeset, old_changeset):
        """Called after a changeset has been modified in a repository.

        The `old_changeset` argument contains the metadata of the changeset
        prior to the modification. It is `None` if the old metadata cannot
        be retrieved.
        """
        self.publish(
            topic='changeset.update',
            repos=[repo.name for repo in repos],
            changeset=changeset.get_properties(),
            old_changeset=old_changeset.get_properties(),
        )
