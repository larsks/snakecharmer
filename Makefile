PORT = /dev/ttyUSB0
BAUD = 115200
AMPY = ampy -p $(PORT) -b $(BAUD)
MPYCROSS = mpy-cross

CONFIG = config.json
SRCS = \
	snakecharmer/__init__.py \
	snakecharmer/main.py \
	snakecharmer/mode_control.py \
	snakecharmer/utils.py \
	snakecharmer/logging.py \
	snakecharmer/hardware.py \
	snakecharmer/config.py \
	snakecharmer/mode_config.py \
	snakecharmer/webserver.py

STATIC = \
	static/snakecharmer.js \
	static/snakecharmer.css \
	static/status.html \
	static/config.html \
	static/config.js \
	static/atomic.js

OBJS = $(SRCS:.py=.mpy)

%.mpy: %.py
	$(MPYCROSS) $<

all: $(OBJS)

check:
	tox

install: install-code install-static
	
install-code: .install-code

install-static: .install-static

install-main: .install-main

.install-main: main.py
	$(AMPY) put main.py && date > $@

.install-code: $(OBJS)
	@$(AMPY) mkdir --exists-okay snakecharmer && \
	for src in $?; do \
		echo "install $$src"; \
		$(AMPY) put $$src $$src; \
		sleep 1; \
	done && date > $@

.install-static: $(STATIC)
	@$(AMPY) mkdir --exists-okay static && \
	for src in $?; do \
		echo "install $$src"; \
		$(AMPY) put $$src $$src; \
		sleep 1; \
	done && date > $@

clean:
	rm -f .lastinstall $(OBJS)
