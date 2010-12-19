"""makeidentifier.pyappscript -- Reserved keywords for py-appscript"""

# Important: the following must be reserved:
#
# - names of properties and methods used in reference.Application and reference.Reference classes
# - names of built-in keyword arguments in reference.Command.__call__

import keyword

kReservedWords = keyword.kwlist + [
	"ID",
	"beginning",
	"end",
	"before",
	"after",
	"previous",
	"next",
	"first",
	"middle",
	"last",
	"any",
	"beginswith",
	"endswith",
	"contains",
	"isin",
	"doesnotbeginwith",
	"doesnotendwith",
	"doesnotcontain",
	"isnotin",
	"AND",
	"NOT",
	"OR",
	"begintransaction",
	"aborttransaction",
	"endtransaction",
	"isrunning",
	"resulttype",
	"ignore",
	"timeout",
	"waitreply",
	"help",
	"as", # not in kwlist before Python 2.5, so defined here to ensure scripts are portable between versions
	"with", # not in kwlist before Python 2.6, so defined here to ensure scripts are portable between versions
	"relaunchmode",
]

