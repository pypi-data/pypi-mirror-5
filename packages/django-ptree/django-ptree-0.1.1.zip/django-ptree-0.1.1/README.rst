=====
pTree
=====

pTree is a Django toolset that makes it easy to create and administer social science experiments to online participants.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "ptree" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'ptree',
      )

2. Create another variable in settings.py called GAME_LABELS and set it to the list of games in your project::

    GAME_LABELS = ['dictator', 'donation', 'grading', 'prisoner', 'publicgoods', 'trust', 'ultimatum']
    INSTALLED_APPS += GAME_LABELS

3. Enable the Bootstrap visual design by setting::
    CRISPY_TEMPLATE_PACK = 'bootstrap3'
