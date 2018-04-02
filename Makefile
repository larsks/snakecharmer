PORT = /dev/ttyUSB0
BAUD = 115200
AMPY = ampy -p $(PORT) -b $(BAUD)
MPYCROSS = mpy-cross

CONFIG = config.json
SRCS = \
	control.py \
	hardware.py \
	tasks.py \
	utils.py \
	tm1637.py \
	webserver.py

OBJS = $(SRCS:.py=.mpy)

%.mpy: %.py
	$(MPYCROSS) $<

all: $(OBJS)

check:
	tox

install: .lastinstall

.lastinstall: $(OBJS)
	for src in $?; do \
		$(AMPY) put $$src; \
	done && date > $@

clean:
	rm -f .lastinstall $(OBJS)
