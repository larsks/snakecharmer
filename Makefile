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

OBJS = $(SRCS:.py=.mpy) config.json status.html

%.mpy: %.py
	$(MPYCROSS) $<

all: $(OBJS)

check:
	tox

install: .lastinstall

.lastinstall: $(OBJS)
	$(AMPY) mkdir --exists-okay snakecharmer && \
	for src in $?; do \
		$(AMPY) put $$src $$src; \
	done && date > $@

clean:
	rm -f .lastinstall $(OBJS)
