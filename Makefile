PORT = /dev/ttyUSB0
BAUD = 115200
AMPY = ampy -p $(PORT) -b $(BAUD)
MPYCROSS = mpy-cross

CONFIG = config.json
SRCS = \
	snakecharmer/__init__.py \
	snakecharmer/main.py \
	snakecharmer/control.py \
	snakecharmer/tasks.py \
	snakecharmer/utils.py \
	snakecharmer/webserver.py \
	hardware.py \
	tm1637.py

STATIC = \
	static/snakecharmer.js \
	static/snakecharmer.css \
	static/status.html \
	static/toggleswitch.css \
	static/atomic.js \
	config.json

OBJS = $(SRCS:.py=.mpy)

%.mpy: %.py
	$(MPYCROSS) $<

all: $(OBJS)

check:
	tox

install: .lastinstall

.lastinstall: $(OBJS) $(STATIC)
	@$(AMPY) mkdir --exists-okay snakecharmer && \
	$(AMPY) mkdir --exists-okay static && \
	for src in $?; do \
		echo "install $$src"; \
		$(AMPY) put $$src $$src; \
		sleep 1; \
	done && date > $@

clean:
	rm -f .lastinstall $(OBJS)
