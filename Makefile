# =====================================
# Makefile for the Sundial bundle
# =====================================
#
# [GUIDE] How to install from source:
#  - https://Sundial.readthedocs.io/en/latest/installing-from-source.html
#
# We recommend creating and activating a Python virtualenv before building.
# Instructions on how to do this can be found in the guide linked above.
export RELEASE_VERSION=1.4.0

.PHONY: build install test clean clean_all

# Generate version.py
github_version:

	@echo "RELEASE VERSION $(RELEASE_VERSION)"

	@echo Generating version.py...
	@echo GIT_COMMIT=\"$(shell git rev-parse --short HEAD)\" > sd-server/sd_server/version.py
	
	@echo RELEASE_VERSION=\"$$RELEASE_VERSION\" > sd-core/sd_core/version.py

	python -c "import secrets; open('sd-core/sd_core/salt_file.py', 'w').write(f'MY_SALT = \"{secrets.token_hex(32)}\"\n')"	
	python sd-core/sd_core/setup.py build_ext --inplace
	python sd-server/sd_server/setup.py build_ext --inplace
	python sd-pixel-engine/sd_pixel_engine/setup.py build_ext --inplace
	python sd-watcher-afk/sd_watcher_afk/setup.py build_ext --inplace
	python sd-ocr-activity/sd_ocr_activity/setup.py build_ext --inplace
	python sd-watcher-window/sd_watcher_window/setup.py build_ext --inplace
	python sd-qt/sd_qt/setup.py build_ext --inplace

	rm -rfv sd-server/sd_server/credentials.py


SHELL := /usr/bin/env bash

SUBMODULES := sd-ocr-activity sd-pixel-engine sd-core sd-client sd-server sd-watcher-afk sd-watcher-window sd-qt 

# Include extras if sd_EXTRAS is true
ifeq ($(sd_EXTRAS),true)
	SUBMODULES := $(SUBMODULES) sd-notify sd-watcher-input
endif

# A function that checks if a target exists in a Makefile
# Usage: $(call has_target,<dir>,<target>)
define has_target
$(shell make -q -C $1 $2 >/dev/null 2>&1; if [ $$? -eq 0 -o $$? -eq 1 ]; then echo $1; fi)
endef

# Submodules with test/package/lint/typecheck targets
TESTABLES := $(foreach dir,$(SUBMODULES),$(call has_target,$(dir),test))
PACKAGEABLES := $(foreach dir,$(SUBMODULES),$(call has_target,$(dir),package))
LINTABLES := $(foreach dir,$(SUBMODULES),$(call has_target,$(dir),lint))
TYPECHECKABLES := $(foreach dir,$(SUBMODULES),$(call has_target,$(dir),typecheck))

# The `build` target
# ------------------
#
# What it does:
#  - Installs all the Python modules
#  - Builds the web UI and bundles it with sd-server
build: github_version
	if [ -e "sd-core/.git" ]; then \
		echo "Submodules seem to already be initialized, continuing..."; \
	else \
		git submodule update --init --recursive; \
	fi
#	needed due to https://github.com/pypa/setuptools/issues/1963
#	would ordinarily be specified in pyproject.toml, but is not respected due to https://github.com/pypa/setuptools/issues/1963
	pip install 'setuptools>49.1.1'
	for module in $(SUBMODULES); do \
		echo "Building $$module"; \
		make --directory=$$module build SKIP_WEBUI=$(SKIP_WEBUI); \
	done
#   The below is needed due to: https://github.com/Sundial/Sundial/issues/173
	make --directory=sd-client build
	make --directory=sd-core build
#	Needed to ensure that the server has the correct version set
	python -c "import sd_server; print(sd_server.__version__)"


# Install
# -------
#
# Installs things like desktop/menu shortcuts.
# Might in the future configure autostart on the system.
install:
	make --directory=sd-qt install
# Installation is already happening in the `make build` step currently.
# We might want to change this.
# We should also add some option to install as user (pip3 install --user)

# Update
# ------
#
# Pulls the latest version, updates all the submodules, then runs `make build`.
update:
	git pull
	git submodule update --init --recursive
	make build


lint:
	@for module in $(LINTABLES); do \
		echo "Linting $$module"; \
		make --directory=$$module lint || { echo "Error in $$module lint"; exit 2; }; \
	done

typecheck:
	@for module in $(TYPECHECKABLES); do \
		echo "Typechecking $$module"; \
		make --directory=$$module typecheck || { echo "Error in $$module typecheck"; exit 2; }; \
	done

# Uninstall
# ---------
#
# Uninstalls all the Python modules.
uninstall:
	modules=$$(pip3 list --format=legacy | grep 'sd-' | grep -o '^sd-[^ ]*'); \
	for module in $$modules; do \
		echo "Uninstalling $$module"; \
		pip3 uninstall -y $$module; \
	done

test:
	@for module in $(TESTABLES); do \
		echo "Running tests for $$module"; \
		poetry run make -C $$module test || { echo "Error in $$module tests"; exit 2; }; \
    done

test-integration:
	# TODO: Move "integration tests" to sd-client
	# FIXME: For whatever reason the script stalls on Appveyor
	#        Example: https://ci.appveyor.com/project/ErikBjare/Sundial/build/1.0.167/job/k1ulexsc5ar5uv4v
	# sd-server-python
	@echo "== Integration testing sd-server =="
	@pytest ./scripts/tests/integration_tests.py ./sd-server/tests/ -v

ICON := "sd-qt/media/logo/logo.png"

sd-qt/media/logo/logo.icns:
	mkdir -p build/MyIcon.iconset
	sips -z 16 16     $(ICON) --out build/MyIcon.iconset/icon_16x16.png
	sips -z 32 32     $(ICON) --out build/MyIcon.iconset/icon_16x16@2x.png
	sips -z 32 32     $(ICON) --out build/MyIcon.iconset/icon_32x32.png
	sips -z 64 64     $(ICON) --out build/MyIcon.iconset/icon_32x32@2x.png
	sips -z 128 128   $(ICON) --out build/MyIcon.iconset/icon_128x128.png
	sips -z 256 256   $(ICON) --out build/MyIcon.iconset/icon_128x128@2x.png
	sips -z 256 256   $(ICON) --out build/MyIcon.iconset/icon_256x256.png
	sips -z 512 512   $(ICON) --out build/MyIcon.iconset/icon_256x256@2x.png
	sips -z 512 512   $(ICON) --out build/MyIcon.iconset/icon_512x512.png
	cp				  $(ICON)       build/MyIcon.iconset/icon_512x512@2x.png
	iconutil -c icns build/MyIcon.iconset
	rm -R build/MyIcon.iconset
	mv build/MyIcon.icns sd-qt/media/logo/logo.icns

dist/Sundial.app: sd-qt/media/logo/logo.icns
	pyinstaller --clean --noconfirm sd.spec

dist/Sundial.dmg: dist/Sundial.app
	# NOTE: This does not codesign the dmg, that is done in the CI config
	pip install dmgbuild
	dmgbuild -s scripts/package/dmgbuild-settings.py -D app=dist/Sundial.app "Sundial" dist/Sundial.dmg

dist/notarize:
	./scripts/notarize.sh

package: github_version
	rm -rf dist
	find . -type d -name "build" -prune -exec rm -rf {} \;
	find . -type d -name "dist" -prune -exec rm -rf {} \;
	mkdir -p dist/Sundial	
	
	for dir in $(PACKAGEABLES); do \
		make --directory=$$dir build; \
		make --directory=$$dir package; \
		if [ "$$dir" = "sd-ocr-activity" ]; then \
			python sd-ocr-activity/scripts/test.py; \
			make --directory=sd-core build; \
			make --directory=sd-client build; \
		fi; \
		cp -r $$dir/dist/$$dir/* dist/Sundial; \
# 		if [ "$$dir" = "sd-server" ]; then \
# 			pyinstaller --onefile --additional-hooks-dir=hooks --noconsole sd-server/sd_server/credential.py; \
# 		fi; \
	done	

# Remove problem-causing binaries
	rm -f dist/Sundial/libdrm.so.2       # see: https://github.com/Sundial/Sundial/issues/161
	rm -f dist/Sundial/libharfbuzz.so.0  # see: https://github.com/Sundial/Sundial/issues/660#issuecomment-959889230
# These should be provided by the distro itself
# Had to be removed due to otherwise causing the error:
#   sd-qt: symbol lookup error: /opt/Sundial/libQt5XcbQpa.so.5: undefined symbol: FT_Get_Font_Format
	rm -f dist/Sundial/libfontconfig.so.1
	rm -f dist/Sundial/libfreetype.so.6
# Remove unnecessary files

	pyinstaller \
		--onefile \
		--noconsole \
		--hidden-import=json \
		--hidden-import=json.decoder \
		--hidden-import=json.encoder \
		--hidden-import=requests \
		sd-server/sd_server/credential.py

	rm -rfv dist_obf 
	pyarmor gen -O dist_obf tls-generator/tls_generator.py	
	python -m PyInstaller \
		--clean \
		--onefile \
		--collect-all cryptography \
		--name tls-generator \
		dist_obf/tls_generator.py

	
	rm -rf dist/Sundial/PySide6/qml
# 	rm -rf dist/Sundial/jsonschema
	rm -rf dist/Sundial/jsonschema-4.19.1.dist-info
	rm -rf dist/Sundial/menuarkupsafe
# 	rm -rf dist/Sundial/werkzeug-2.3.7.dist-info
	rm -rf dist/Sundial/importlib_metadata-6.8.0.dist-info
	rm -rf dist/Sundial/cryptography-41.0.5.dist-info
# 	rm -rf dist/Sundial/flask-2.3.3.dist-info
	
	rm -rf dist/Sundial/attrs-23.1.0.dist-info
	rm -rf dist/Sundial/PySide6/translations/*.qm
	cp dist/Sundial/PySide6/translations/qtwebengine_locales/en-US.pak dist/Sundial/PySide6/translations/qtwebengine_locales/en-US.tmp
	rm -rf dist/Sundial/PySide6/translations/qtwebengine_locales/*.pak 
	cp dist/Sundial/PySide6/translations/qtwebengine_locales/en-US.tmp dist/Sundial/PySide6/translations/qtwebengine_locales/en-US.pak
	rm -rf dist/Sundial/PySide6/translations/qtwebengine_locales/*.tmp
	rm -rf dist/Sundial/sd-qt.desktop
	mv dist/Sundial/sd-qt.exe dist/Sundial/sd-main.exe
	mv dist/credential.exe dist/Sundial/
	cp dist/tls-generator.exe dist/Sundial/

	
	 
# Builds zips and setups
	bash scripts/package/package-all.sh


	@echo "Release version: $(RELEASE_VERSION)"
	@cd "$(shell pwd)"
	@cd sd-server; \
	git checkout -- sd_server/credentials.py; \

sign:
	bash scripts/package/package-signed.sh

clean:
	rm -rf build dist

# Clean all subprojects
clean_all: clean
	for dir in $(SUBMODULES); do \
		make --directory=$$dir clean; \
	done

clean-auto:
	rm -rIv **/sd-android/mobile/build
	rm -rIfv **/node_modules


