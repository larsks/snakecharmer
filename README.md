# snakecharmer

This code is designed to manage the temperature and humidity of a
reptile cage by reading data from a set of temperature and humidity
sensors and controlling a set of relays attached to heating elements
and humidifiers.

## Design

Snakecharmer is implemented as a set of asynchronous coroutines.
There are four tasks:

1. Read the sensors.
1. Manage the LED display.
1. Control the relays based on sensor data.
1. Provide a web interface to sensor, relay, and configuration data.

The tasks are implement in `snakecharmer/tasks.py`, with the
exception of the webserver, which is in `snakecharmer/webserver.py`.

## License

snakecharmer -- reptile cage environmental control  
Copyright (C) 2018 Lars Kellogg-Stedman <lars@oddbit.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
