# Copyright (C) 2007-2010 Samuel Abels.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
When imported, this module catches KeyboardInterrupt (SIGINT).
It is a convenience wrapper around sigint.SigIntWatcher()
such that all that is required for the change to take effect
is the following statement::

  import Exscript.util.sigintcatcher

Be warned that this way of importing breaks on some systems, because a
fork during an import may cause the following error::

  RuntimeError: not holding the import lock

So in general it is recommended to use the L{sigint.SigIntWatcher()}
class directly.
"""
from __future__ import unicode_literals
from Exscript.util.sigint import SigIntWatcher
_watcher = SigIntWatcher()
