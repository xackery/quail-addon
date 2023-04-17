VERSION ?= 2.0.4

comma := ,
COMMA_VERSION := $(subst .,${comma} ,${VERSION})

build:
	@echo "build: packing and building"
	@mkdir -p bin
	@-rm -rf bin/*
	cd /src/quail && make build-windows && cp bin/quail-win-x64.exe quail.exe
	sed -i '' 's/"version": (1, 0, 0),/"version": (${COMMA_VERSION}),/' __init__.py
	zip bin/quail-${VERSION}.zip quail.exe LICENSE README.md eqg/*.py s3d/*.py common/*.py *.py
	sed -i '' 's/"version": (${COMMA_VERSION}),/"version": (1, 0, 0),/' __init__.py