from zope.container  import contained
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from Acquisition import aq_inner

from five.customerize.zpt import TTWViewTemplateRenderer

from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView as base

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer

from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key

from plone.app.portlets.interfaces import IPortletPermissionChecker

from plone.portlets.interfaces import IPortletAssignmentSettings


class PortletManagerKSS(base):
    """Opertions on portlets done using KSS
    """
    implements(IPloneKSSView)

    def move_portlet_up(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context,
                        info['manager'], info['category'], info['key'])

        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        keys = list(assignments.keys())
        name = info['name']
        idx = keys.index(name)
        del keys[idx]
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)

        return self._render_column(info, viewname)

    def move_portlet_down(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context,
                        info['manager'], info['category'], info['key'])

        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        keys = list(assignments.keys())
        name = info['name']
        idx = keys.index(name)
        del keys[idx]
        keys.insert(idx+1, name)
        assignments.updateOrder(keys)

        return self._render_column(info, viewname)

    def delete_portlet(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context,
                        info['manager'], info['category'], info['key'])

        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        # set fixing_up to True to let zope.container.contained
        # know that our object doesn't have __name__ and __parent__
        fixing_up = contained.fixing_up
        contained.fixing_up = True

        del assignments[info['name']]

        # revert our fixing_up customization
        contained.fixing_up = fixing_up

        return self._render_column(info, viewname)

    def toggle_visibility(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context,
                        info['manager'], info['category'], info['key'])

        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        assignment = assignments[info['name']]
        settings = IPortletAssignmentSettings(assignment)
        visible = settings.get('visible', True)
        settings['visible'] = not visible
        return self._render_column(info, viewname)

    def _render_column(self, info, view_name):
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('div#portletmanager-' + info['manager'].replace('.', '-'))

        context = aq_inner(self.context)
        request = aq_inner(self.request)
        view = getMultiAdapter((context, request), name=view_name)
        # view can have been customized TTW, see #11409
        if isinstance(view, TTWViewTemplateRenderer):
            view = view._getView()

        manager = getUtility(IPortletManager, name=info['manager'])

        request['key'] = info['key']

        request['viewname'] = view_name
        renderer = getMultiAdapter((context, request, view, manager), IPortletManagerRenderer)
        renderer.update()
        ksscore.replaceInnerHTML(selector, renderer.__of__(context).render())
        return self.render()
