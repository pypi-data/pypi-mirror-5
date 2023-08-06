py2=2.7
py3=3.3
user_install=~/.local
local_pip2_home=$(user_install)/lib/python$(py2)/site-packages
local_pip3_home=$(user_install)/lib/python$(py3)/site-packages
name=facct
version=0.1.2
project_version_named=$(name)-$(version)

local-pip-install:zip
	pip install  dist/$(project_version_named).tar.gz --user
local-pip3-install:zip3
	python3-pip install  dist/$(project_version_named).tar.gz --user
zip3:clean3
	python3 setup.py sdist
zip:clean
	python setup.py sdist
clean:
	rm -rf dist/ $(name).egg-info/ \
		$(local_pip2_home)/$(project_version_named)-py$(py2).egg-info \
		$(local_pip2_home)/$(name) $(user_install)/$(name)
clean3:
	rm -rf dist/ $(name).egg-info/ \
		$(local_pip3_home)/$(project_version_named)-py$(py3).egg-info \
		$(local_pip3_home)/$(name) $(user_install)/$(name)
register:
	python setup.py register sdist upload

deploy_test=import $(name).bench;$(name).bench.main('corp_ref', False)
test3:local-pip3-install
rpm_test:rpm_install
	env PWD=/ python3 -c "$(deploy_test)"

test2:local-pip-install
	env PWD=/ python2 -c "$(deploy_test)"

uninstall:
	pip              uninstall $(name)   ;\
	python3-pip      uninstall $(name)   ;\
	sudo pip         uninstall $(name)   ;\
	sudo python3-pip uninstall $(name)

rpm_name=python-$(name)
rpm_py3_name=python3-$(name)
release=1
rpm_version_named=$(rpm_name)-$(version)
rpm_version3_named=$(rpm_py3_name)-$(version)

py_files=$(shell find $(name) -type f -name "*.py")
bdist:dist/$(project_version_named).tar.gz
dist/$(project_version_named).tar.gz:$(name).spec $(py_files)
	rm -rf ~/rpm/SOURCES
	python setup.py bdist --formats=rpm
	
rpmbuild:dist/$(project_version_named).tar.gz
	mkdir -p dist && \
	cp $(name).spec dist/$(rpm_name).spec && \
	cp $(name).spec dist/$(rpm_py3_name).spec && \
	cd dist &&\
	mkdir -p ~/rpm/SOURCES ;\
	cp $(project_version_named).tar.gz ~/rpm/SOURCES/ &&\
	rpmbuild -v -ba --clean $(rpm_name).spec \

rpmlint:rpmbuild
	rpmlint $(HOME)/rpm/RPMS/noarch/$(rpm_version_named)-$(release).noarch.rpm dist/$(rpm_name).spec
	rpmlint $(HOME)/rpm/SRPMS/$(rpm_version_named)-$(release).src.rpm dist/$(rpm_name).spec
	rpmlint $(HOME)/rpm/RPMS/noarch/$(rpm_version3_named)-$(release).noarch.rpm dist/$(rpm_py3_name).spec
mock:rpmlint
	mock --verbose  $(HOME)/rpm/SRPMS/$(rpm_version_named)-$(release).src.rpm
win_pkg:
	@if [ ! "`uname`" = "Linux" ]; then \
		python setup.py bdist --formats=wininst ;\
	else \
		echo "Not a windows platform, sorry." >&2 ;\
	fi
rpm_install:rpmbuild
	sudo rpm -ivh $(HOME)/rpm/RPMS/noarch/$(rpm_version_named)-$(release).noarch.rpm
	@#sudo rpm -ivh dist/$(name)-$(version)-$(release).noarch.rpm
