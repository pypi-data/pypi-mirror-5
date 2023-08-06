OVERVIEW
---------
jinja2_alchemy_starter is a scaffold for getting started with a pyramid project using Jinja2 Templating Engine and SQLAlchemy ORM

INSTALLATION
-------------
Install it in your existing python installation (`virtualenv` is recommended)

If you have source file available locally::

	$ /opt/py_env/bin/easy_install jinja2_alchemy_starter-X.tar.gz
	
Or to download and install from PyPI::
	
	$ /opt/py_env/bin/easy_install jinja2_alchemy_starter

After successful installation, `pcreate` will also list `jinja2_alchemy_starter` as available scaffold::
	
	$ /opt/py_env/bin/pcreate -l
		Available scaffolds:
		  alchemy:                 Pyramid SQLAlchemy project using url dispatch
		  jinja2_alchemy_starter:  Pyramid project with Jinja2 and SQLAlchemy
		  pyramid_jinja2_starter:  pyramid jinja2 starter project
		  starter:                 Pyramid starter project
		  zodb:                    Pyramid ZODB project using traversal


USAGE
------
To create a new pyramid project using `jinja2_alchemy_starter` just pass that as `-s` argument::
	
	$ /opt/py_env/bin/pcreate -s jinja2_alchemy_starter MyProject
	
This will create MyProject directory in your working directory. 

PUT IT TO WORK
---------------
- Edit development.ini to reflect your DB settings.
- Edit rest of the files



