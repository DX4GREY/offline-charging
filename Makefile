.PHONY: all install uninstall preview test check

all: check

install:
	@sudo ./install.sh

uninstall:
	@sudo ./uninstall.sh

preview:
	@python3 dev/preview.py

test:
	@python3 dev/test_inputs.py

check:
	@python3 -m py_compile bin/offline-charger dev/preview.py dev/test_inputs.py
	@echo "All scripts passed syntax check."
