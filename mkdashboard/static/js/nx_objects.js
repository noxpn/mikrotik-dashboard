const err_t = {'freemem_t': 30, 'freehdd_t': 5};
const records_per_page = 30; // for pagination

/***
/* Example object
var object_name= {
    name: 'description',
    cmd: 'routerOS command',
    type: 'process type', 0 - simple table, 1 - complex table
    extra: 'extra data',
    main_headers: [main headers array],
    col2_headers: [ optional col2 header array ],
    col3_headers: [ optional col3 header array ],
};
*/

const rb_interface = {
    name: 'interface info',
    cmd: '/interface',
    type: '1',
    extra: '',
    main_headers: ['name', 'type', 'mac-address', 'link-downs'],
    col2_headers: ['name', 'mac-address', 'link-downs'],
    col3_headers: ['name'],
};
const rb_route = {
    name: 'ip routes info',
    cmd: '/ip/route',
    type: '1',
    extra: '',
    main_headers: ['abr','dst-address', 'gateway', 'distance', 'pref-src'],
    col2_headers: ['dst-address', 'gateway', 'routing-mark', 'pref-src'],
};
const rb_br = {
    name: 'Bridge interface info',
    cmd: '/interface/bridge',
    type: '1',
    extra: '',
    main_headers: ['name', 'mac-address', 'vlan-filtering', 'protocol-mode'],
    col2_headers: ['mac-address', 'protocol-mode', 'vlan-filtering'],

}
const rb_br_pr = {
    name: 'Bridge ports info',
    cmd: '/interface/bridge/port',
    type: '1',
    extra: '',
    main_headers: ['interface', 'bridge', 'pvid',  'status', 'port-number' ],
    col2_headers: ['interface', 'status', 'port-number' ],

}
const rb_br_vl = {
    name: 'Bridge vlans info',
    cmd: '/interface/bridge/vlan',
    type: '1',
    extra: '',
    main_headers: ['bridge', 'vlan-ids', 'tagged', 'untagged', 'current-tagged', 'current-untagged'],
    col2_headers: ['vlan-ids', 'current-tagged', 'current-untagged'],
    col3_headers: ['tagged'],
}
const rb_ip_addr = {
    name: 'Ip Addresses list',
    cmd: '/ip/address',
    type: '1',
    extra: '',
    main_headers: ['abr', 'address', 'network', 'interface', 'actual-interface'],
    col2_headers: ['address', 'network', 'interface', 'actual-interface'],
}
const rb_ip_svc  = {
    name: 'IP Services list',
    cmd: '/ip/service',
    type: '1',
    extra: '',
    main_headers: ['name', 'port', 'address', 'certificate', 'tls-version'],
    col2_headers: ['name', 'address', 'certificate', 'tls-version'],
}
const rb_sw_prt = {
    name: 'switch ports',
    cmd: '/interface/ethernet/switch/port',
    type: '1',
    extra: '',
    main_headers: ['name','switch', 'rx-bytes', 'tx-bytes', ],
    col2_headers: ['name','rx-bytes', 'tx-bytes', ],

}
const rb_sw_vl = {
    name: 'switch vlans',
    cmd: '/interface/ethernet/switch/vlan',
    type: '1',
    extra: '',
    main_headers: ['ports', 'vlan-id', 'switch' ],
    col2_headers: ['ports', 'vlan-id', 'switch' ],
    col3_headers: ['ports'],

}
const rb_users = {
    name: 'system users list',
    cmd: '/user',
    type: '1',
    extra: '',
    main_headers: ['name', 'group', 'address', 'last-logged-in'],
    col2_headers: ['name',],
    col3_headers: [ 'address', 'last-logged-in'],
}
const rb_ssh_key = {
    name: 'users ssh keys',
    cmd: '/user/ssh-keys',
    type: '1',
    extra: '',
    main_headers: ['user', 'key-owner'],
    col2_headers: ['user'],
    col3_headers: ['key-owner'],

}
const rb_sched = {
    name: 'system scheduler tasks',
    cmd: '/system/scheduler',
    type: '1',
    extra: '',
    main_headers: ['name', 'start-date', 'interval', 'owner'],
    col2_headers: ['start-date', 'interval', 'owner'],
    col3_headers: ['name'],
}

const rb_info = {
    name: '',
    cmd: '/system/routerboard',
    type: '2',
    extra: '',
}
const rb_health = {
    name: 'System health',
    cmd: '/system/health',
    type: '2',
    extra: '',
}
const rb_res = {
    name: 'Routerboard resources',
    cmd: '/system/resource',
    type: '2',
    extra: '',
}
const rb_clock = {
    name: 'Clock and timezone',
    cmd: '/system/clock',
    type: '2',
    extra: '',
}

const rb_log = {
    name: 'Log',
    cmd: '/log',
    type: '4',
    extra: '',
}

const rb_ping = {
    name: 'Ping',
    cmd: '/ping',
    type: '3',
    extra: '',
}
const rb_tracert = {
    name: 'Traceroute',
    cmd: '/tool/traceroute',
    type: '3',
    extra: '',
}


const target_objects = [rb_interface,
                        rb_route,
                        rb_br,
                        rb_sched,
                        rb_ssh_key,
                        rb_users,
                        rb_sw_vl,
                        rb_sw_prt,
                        rb_ip_svc,
                        rb_ip_addr,
                        rb_br_vl,
                        rb_br_pr,
                        rb_info,
                        rb_health,
                        rb_clock,
                        rb_res,
                        rb_log,
                        rb_ping,
                        rb_tracert,
                     ];
