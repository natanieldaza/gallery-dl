
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python3


all: man completion supportedsites options

clean:
	$(RM) -r build/
	$(RM) -r data/

install: man completion
	$(PYTHON) -m pip install gallery_dl

release: man completion supportedsites
	scripts/release.sh

test:
	scripts/run_tests.py

executable:
	scripts/pyinstaller.py

completion: data/completion/gallery-dl data/completion/_gallery-dl data/completion/gallery-dl.fish

req: requirements
requirements: requirements/docker requirements/windows requirements/linux requirements/macos

man: data/man/gallery-dl.1 data/man/gallery-dl.conf.5

supportedsites: docs/supportedsites.md

options: docs/options.md

.PHONY: all clean install release test executable requirements completion man supportedsites options

docs/supportedsites.md: gallery_dl/*/*.py scripts/supportedsites.py
	$(PYTHON) scripts/supportedsites.py

docs/options.md: gallery_dl/option.py scripts/options.py
	$(PYTHON) scripts/options.py

data/man/gallery-dl.1: gallery_dl/option.py gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

data/man/gallery-dl.conf.5: docs/configuration.rst gallery_dl/version.py scripts/man.py
	$(PYTHON) scripts/man.py

data/completion/gallery-dl: gallery_dl/option.py scripts/completion_bash.py
	$(PYTHON) scripts/completion_bash.py

data/completion/_gallery-dl: gallery_dl/option.py scripts/completion_zsh.py
	$(PYTHON) scripts/completion_zsh.py

data/completion/gallery-dl.fish: gallery_dl/option.py scripts/completion_fish.py
	$(PYTHON) scripts/completion_fish.py

requirements/docker: scripts/requirements.py requirements/versions
	$(PYTHON) scripts/requirements.py -i requirements/versions -D --musl --x64 --arm --py14 -o requirements/docker

requirements/windows: scripts/requirements.py requirements/versions requirements/versions_pyinstaller
	$(PYTHON) scripts/requirements.py -i requirements/versions -i requirements/versions_pyinstaller -D --windows --x64 --py14 -o requirements/windows

requirements/linux: scripts/requirements.py requirements/versions requirements/versions_pyinstaller requirements/versions_secretstorage
	$(PYTHON) scripts/requirements.py -i requirements/versions -i requirements/versions_pyinstaller -i requirements/versions_secretstorage -D --glibc --x64 --py10 --py14 -o requirements/linux

requirements/macos: scripts/requirements.py requirements/versions requirements/versions_pyinstaller
	$(PYTHON) scripts/requirements.py -i requirements/versions -i requirements/versions_pyinstaller -D --macos --x64 --arm64 --py14 -o requirements/macos
