# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/11/04
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

# TODO: come up with a better way to do engine aliasing...

from .genshic import fixate_genshic, fixate_genshic_dryrun

fixate_genshi_compile_dryrun = fixate_genshic_dryrun
fixate_genshi_compile        = fixate_genshic

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
