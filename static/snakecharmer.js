lastupdate = document.querySelector('#lastupdate');
sensor_table = document.querySelector('#sensors');
relay_table = document.querySelector('#relays');
config_table = document.querySelector('#config');
temp_f = document.querySelector('#temp_f');

var update_sensor_table = function(data, xhr) {
    console.log('updating sensor table')

    for (var sensor_id in data) {
        sensor = data[sensor_id]

        var row = document.evaluate('//tr[@id="' + sensor_id + '"]',
            document, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (!row) {
            row = document.createElement('tr');
            row.id = sensor_id;

            for (i=0; i < 3; i++) {
                cell = document.createElement('td');
                row.appendChild(cell);
            }

            row.cells[0].innerHTML = sensor_id
            sensor_table.appendChild(row);
        }

        if (sensor.t) {
            if (temp_f.checked)
                t = sensor.t * 1.8 + 32;
            else
                t = sensor.t;

            row.cells[1].innerHTML = parseFloat(t).toFixed(2);
        }
        if (sensor.h)
            row.cells[2].innerHTML = parseFloat(sensor.h).toFixed(2);
    }
}

var update_relay_table = function(data, xhr) {
    console.log('updating relay table')

    for (var relay_id in data) {
        relay_state = data[relay_id]

        var row = document.evaluate('//tr[@id="' + relay_id + '"]',
            document, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (!row) {
            row = document.createElement('tr');
            row.id = relay_id;

            for (i=0; i < 2; i++) {
                cell = document.createElement('td');
                row.appendChild(cell);
            }

            row.cells[0].innerHTML = relay_id
            relay_table.appendChild(row);
        }

        row.cells[1].innerHTML = relay_state
    }
}

var get_sensors = function() {
    atomic.ajax({url: '/sensors'})
        .success(update_sensor_table);
};

var get_relays = function() {
    atomic.ajax({url: '/relays'})
        .success(update_relay_table);
};

var update_all = function() {
    get_sensors();
    get_relays();

    var now = new Date();
    lastupdate.innerHTML = now.toTimeString();
}

var update_interval = setInterval(update_all, 10000);
update_all();
