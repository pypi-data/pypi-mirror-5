===============
collective.base
===============

collective.base provides base class for adapter with commonly used methods.

Currently tested with
----------------------

- Plone-4.3.1 and Python-2.7.x

Changelog
---------

0.6.1 (2013-09-25)
==================

- Refactor method: ``get_brains``. [taito]
- Tested with Plone-4.3.1. [taito]

0.6 (2013-06-08)
================

- Add base view: ``collective.base.view.BaseView``. [taito]
- Add method: ``membership`` to ``collective.base.adapter.Adapter``. [taito]
- Add method: ``create_viewlet`` to ``collective.base.tests.base.IntegrationTestCase``. [taito]
- Add method: ``available`` to ``collective.base.viewlet.Viewlet``. [taito]
- Add viewlet manger to support repetition of usage of viewlet template. [taito]

0.5.1 (2013-05-11)
==================

- Fix catalog query. [taito]

0.5 (2013-05-09)
================

- Add view: BaseFormView. [taito]
- Add interface: IViewlet. [taito]

0.4 (2013-04-15)
================

- Update for Plone-4.3. [taito]
- Remove dependency from five.grok. [taito]

0.3 (2013-03-11)
================

- Update name of class. [taito]

0.2 (2013-03-09)
================

- Add unrestrictedSearchResults usage as option. [taito]
- Test with Plone-4.2.5. [taito]

0.1 (2013-03-07)
================

- Initial release. [taito]
