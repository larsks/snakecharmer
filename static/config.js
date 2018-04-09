message = document.querySelector('#message')
ssid_menu = document.querySelector('#ssid');
scan_link = document.querySelector('#rescan');
connect_button = document.querySelector('#connect');
reboot_button = document.querySelector('#reboot');
net_status = document.querySelector('#status');

net_state_map = ['unknown', 'connecting', 'failed', 'connected'];

var update_ssid_menu = function(data, xhr) {
    while (ssid_menu.firstChild) {
        ssid_menu.removeChild(ssid_menu.firstChild);
    }

    for (var i=0; i < data.length; i++) {
        if (data[i]['authmode'] != 0)
            label = data[i]['ssid'] + ' (&#x1f512;)';
        else
            label = data[i]['ssid'];

        option = document.createElement('option')
        option.value = data[i]['ssid'];
        option.innerHTML = label;
        ssid_menu.appendChild(option)
    }

    message.innerHTML = '';
}

var scan = function() {
    message.innerHTML = 'Scanning for wifi networks...';
    atomic.ajax({url: '/api/scan'})
        .success(update_ssid_menu);
}

var update_network_config_info = function(data, xhr) {
    net_status.cells[0].innerHTML = net_state_map[data['state']];
    net_status.cells[1].innerHTML = data['sta']['connected'];

    if (data['sta']['connected']) {
        net_status.cells[3].innerHTML = data['sta']['ifconfig'][2];
    }
}

var get_network_config = function() {
    atomic.ajax({url: '/api/status'})
        .success(update_network_config_info);
}

var report_reboot = function() {
    message.innerHTML = ''
}

var reboot = function() {
    message.innerHTML = 'Rebooting...';
    atomic.ajax({url: '/api/reset'})
        .success(report_reboot);
}

var update_connect_state = function(data, xhr) {
    message.innerHTML = data['message'];
}

var connect = function() {
    ssid = document.querySelector('#ssid').value;
    password = document.querySelector('#password').value;

    message.innerHTML = 'Connecting to ' + ssid;
    atomic.ajax({type: 'POST',
        url: '/api/connect',
        data: JSON.stringify({'ssid': ssid, 'password': password})})
        .success(update_connect_state);
}

var update_interval = setInterval(get_network_config, 5000);
scan_link.addEventListener('click', scan);
reboot_button.addEventListener('click', reboot);
connect_button.addEventListener('click', connect);
scan();
