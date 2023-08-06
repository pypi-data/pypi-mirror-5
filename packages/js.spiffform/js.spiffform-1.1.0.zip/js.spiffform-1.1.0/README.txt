Introduction
============

This library packages `SpiffForm`_ for `fanstatic`_. It is aware of SpiffForm's
structure.

.. _`fanstatic`: http://fanstatic.org
.. _`SpiffForm`: https://github.com/knipknap/SpiffForm

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory) are published to some URL.

Git subtree of SpiffForm
------------------------

We use git `subtree`_ to get SpiffForm.

.. _`subtree`: https://help.github.com/articles/working-with-subtree-merge

How::
    
    $ git remote add -f spiffform https://github.com/lugensa/SpiffForm.git
    $ git merge -s ours --no-commit spiffform/master
    $ git read-tree --prefix=js/spiffform/resources/ -u spiffform/master
    $ git commit -m "Subtree merged in js/spiffform/resources/"

Pull changes::

    $ git pull -s subtree #this only works if we use not nested prefix name 
    $ git pull --squash -s subtree https://github.com/lugensa/SpiffForm.git
master
