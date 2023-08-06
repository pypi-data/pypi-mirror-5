The initdotpy package makes it simple to write __init__.py files that automatically include the package contents.

For example if you have an __init__.py that looks like:

import submodule1 
import submodule2 
import submodule3 
import subpackage1
import subpackage2
import subpackage3

You can replace it with:

from initdotpy import auto_import
auto_import()

and it will automatically import all the modules/packages contained in the package and stay up to date when you make changes to the package contents.

Or if you prefer to import the contents of the submodules/subpackages, e.g.:

from submodule1 import *
from submodule2 import *
from submodule3 import *
from subpackage1 import *
from subpackage2 import *
from subpackage3 import *

You can just write your __init__.py as:

from initdotpy import auto_import_contents
auto_import_contents()

In this case every submodule/subpackage must have an __ALL__ defined and there must not be duplicate definitions of the same name. Again this __init__.py automatically stays up to date so you need never edit it again.