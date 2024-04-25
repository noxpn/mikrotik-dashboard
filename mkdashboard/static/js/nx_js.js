
//# Unused example
function makeGetRequest(path) {
    axios.get(path).then(
        (response) => {
            var result = response.data;
            console.log(result);
        },
        (error) => {
            console.log(error);
        }
    );
}


const debug = true;
document.documentElement.style.overflow = "scroll";

// Request to fill brief table
function makeBriefInfoRequest(path, queryObj) {
    document.getElementById(queryObj.id).className = 'animated-gradient';
    axios.post(path, queryObj).then(
        (response) => {
            var result = response.data;
            if (result.hasOwnProperty('ERR')){
                fill_err_info(queryObj.id, result);
                fill_br_err_info(queryObj.id, result);
            } else {
                fill_brief_table(queryObj.id, result);
            }
        },
        (error) => {
            fill_err_info(queryObj.id, {'ERR': error.message});
        }
    );
}

// toggle buttons on request time
function toggleButtons(id){
    document.getElementById(id).className = 'animated-gradient';
    var button_div = document.getElementById('buttons-'+id);
    button_div.disabled = !button_div.disabled;
    var buttons = button_div.getElementsByTagName('BUTTON');
    for(var i = 0; i < buttons.length; i++){
         buttons[i].disabled = !buttons[i].disabled;
    }
}

// ----------
function makeRequest(path, queryObj) {
    toggleButtons(queryObj.id);
    axios.post(path, queryObj).then(
        (response) => {
            var result = response.data;
            var knownObject = false;
            toggleButtons(queryObj.id);
            if (result.hasOwnProperty('ERR')){
                fill_err_info(queryObj.id, result);
            } else {
                for (var i = 0; i < target_objects.length; i++){
                    if (queryObj.cmd == target_objects[i].cmd){
                        knownObject = true;
                        switch(target_objects[i].type){
                        case '1':
                            fill_table_complex(queryObj.id,
                                                result,
                                                target_objects[i].main_headers,
                                                target_objects[i].col2_headers,
                                                target_objects[i].col3_headers);
                            break;
                        case '2':
                            fill_table_flat(queryObj.id, result);
                            break;
                        case '3':
                            fill_ping_table_data(queryObj.id, result);
                            break;
                        case '4':
                            fill_log_data(queryObj.id, result);
                            break;
                        default:
                            fill_err_info(queryObj.id, {'ERR': 'NO_SHAPE_MATCH', 'host_id': queryObj.id});
                        }
                    }
                }
                if (!knownObject) {
                    fill_err_info(queryObj.id, {'ERR': 'NO_OBJECT', 'host_id': queryObj.id});
                }
            }
        },
        (error) => {
            fill_err_info(queryObj.id, {'ERR': error.message});
        }
    );
}

// Debug request without checks
function makeDebugRequest(path, queryObj) {
    toggleButtons(queryObj.id);
    axios.post(path, queryObj).then(
        (response) => {
            var result = response.data;
            toggleButtons(queryObj.id);
            if (result.hasOwnProperty('ERR')){
                fill_err_info(queryObj.id, result);
            } else {
                fill_table_complex(queryObj.id,result);
            }
        },
        (error) => {
            fill_err_info(queryObj.id, {'ERR': error.message});
        }
    );
}

// parse log from rb
function fill_log_data(id, data_array, topic, page){
    var last_data_elem = data_array[data_array.length-1];
    var topics_array = ['empty'];
    if (last_data_elem.hasOwnProperty('all_topics')){
        topics_array = last_data_elem['all_topics'];
    }
    if (topic == undefined){
        topic = 'all';
    }
    if (page == undefined){
        page = 0;
    }

    color_error(id, data_array);
    const div_id = 'c-'+id;
    var element = document.getElementById(div_id);
    if (element == null){
        console.log('Get lost with tossing IDs');
        return;
    }
    element.innerHTML = '';
// -- make row container
    var row_div = document.createElement("div");
    row_div.id = 'p-row'+id.slice(0,8);
    row_div.className = 'row';
    element.appendChild(row_div);
    var topicID = '';

// -- insert header items in row container
    for (key in data_array[0]){
        var key_div = document.createElement("div");
        key_div.id = key+id.slice(0,8);

        if (key == 'message'){
            key_div.className = 'col-7 border';
        }
        else if (key == 'topics'){
            topicID = key_div.id;
            key_div.className = 'col-2 border';
        } else {
            key_div.className = 'col-1 border';
        }
        //rude fix
        if (key == 'time'){
            key_div.className = 'col-2 border';
        }
        key_div.innerText = key;
        row_div.appendChild(key_div);
   }

// -- insert data rows
    var cnt = 0;
    var entries_array = [];
    for(object_item in data_array){

        var skip = true;
        var entry_div = document.createElement("div");
        entry_div.id = 'e-row'+id.slice(0,8)+object_item;
        entry_div.className = 'row';

// -- insert entries in data rows
        for (key in data_array[object_item]){
            var val_div = document.createElement("div");
            val_div.id = key+id.slice(0,8)+object_item;
            if (key == 'message'){
                val_div.className = 'col-7 border';
                val_div.innerText = data_array[object_item][key];
            } else if (key == 'topics') {
                entry_topic = data_array[object_item][key];
                topic_arr = entry_topic.split(',');
                if (topic_arr.includes(topic)){
                   skip = false;
                } else if (topic == 'all') {
                   skip = false;
                } else {
                   skip = true;
                }
                val_div.className = 'col-2 border';
                  val_div.innerText = entry_topic;
            }
            else if (key == 'id') {
            val_div.className = 'col-1 border';
            val_div.innerText = data_array[object_item][key];
            }
            else {
                val_div.className = 'col-1 border';
                val_div.innerText = data_array[object_item][key];
            }
            //rude fix
            if (key == 'time'){
                val_div.className = 'col-2 border';
            }
            entry_div.appendChild(val_div);
        }
        if (skip != true){
                entries_array.push(entry_div);
        }
    }
    print_pages_entries(entries_array, element, page);
    append_pages_elem(entries_array, element, id, topic, data_array, page);


// find items to replace
    var topic_list = document.getElementById(topicID);
//var page = 0;
    var topic_menu = add_menu(id, data_array, topics_array, page);
// Add new menu replacing 'row div'
    row_div.replaceChild(topic_menu ,topic_list);
// select selected item in menu
    for (opt in topic_menu.options){
        if (topic_menu.options[opt].value == topic){
            topic_menu.options[opt].selected = true;
        }
    }
}

//-------------------------------
// PAGINATION

function get_pages(elem_array, elem_on_page){
    const all_entries = elem_array.length;
    const rest_pages = all_entries%elem_on_page;
    const round_pages = ( all_entries - rest_pages ) / elem_on_page;
    var pages = [0,];
    var marker = 0;
    for(var i = 0 ; i < round_pages; i++){
        pages.push(marker+=elem_on_page);
    }
    // pages.push(marker += rest_pages); // useful for indexing all entries
    return pages;
}

// prod - print log entries per page
function print_pages_entries(elem_array, anchor_elem, page){
    var start_entry = parseInt(page);
    var end_entry = parseInt(page)+records_per_page;

    if (end_entry > elem_array.length){
        end_entry = elem_array.length;
    }
    var show_elems = elem_array.slice(start_entry, end_entry);
    for(e in show_elems){
        anchor_elem.appendChild(show_elems[e]);
    }
}

// prod - append pages bottom of log
function append_pages_elem(elem_array, anchor_elem, id, topic, data_array, page){
    const pages = get_pages(elem_array, records_per_page);
    var end_list_div = document.createElement('div');
    end_list_div.className = 'row';
    end_list_div.id = 'end_log';

    for (p in pages){
        var end_int_div = document.createElement('div');
        end_int_div.id = 'end_log_col-' + pages[p];
        // colorize current page marker
        end_int_div.className = 'col col-1 text-center border';
        if (pages[p] == page){
            end_int_div.className += ' bg-warning';
        }
        end_int_div.innerText = pages[p];
        end_int_div.onclick = function(){
            fill_log_data(id, data_array, topic, this.id.split('-')[1]);
        }
        end_list_div.appendChild(end_int_div);
    }
    anchor_elem.appendChild(end_list_div);
}


//prod
// Add menu from topics
function add_menu(id, data_array, topicSet, page){
    var btn_grp = document.createElement("select");
        btn_grp.className = "col-2";
        // chrome crutch
        if (navigator.userAgent.indexOf("Chrome") !== -1){
            btn_grp.onclick = function(){
            if (typeof(this.selectedIndex) != 'undefined'){
                fill_log_data(id, data_array, this.value, 0)};
            }
        }
        btn_grp.id = "topics_col";

    var h_option = document.createElement("option");
        h_option.value = 'all';
        h_option.innerText = 'all topics';
        h_option.onclick = function(){fill_log_data(id, data_array, 'all', 0)};
        btn_grp.appendChild(h_option);

    for (let item of topicSet) {
        var l_option = document.createElement("option");
            l_option.value = item;
            l_option.innerText = item;
            l_option.onclick = function(){fill_log_data(id, data_array, item, 0)};
            btn_grp.appendChild(l_option);
        }
    return btn_grp;
}
//------------- log section end -------------
//# prod
// fill table from ping|trace
function fill_ping_table_data(id, data_array){
    color_error(id, data_array);
    const div_id = 'c-'+id;
    var element = document.getElementById(div_id);
    if (element == null){
        console.log('Get lost with tossing IDs');
        return;
    }
    element.innerHTML = '';
// -- make row container
    var row_div = document.createElement("div");
    row_div.id = 'p-row'+id.slice(0,8);
    row_div.className = 'row';
    element.appendChild(row_div);

// -- insert header items in row container
    for (key in data_array[0]){
        var key_div = document.createElement("div");
        key_div.id = key+id.slice(0,8);
        if (key == '.section'){
           continue;
        }

        if (key == 'host' || key == 'address' || key == 'status'){
            key_div.className = 'col-2 border';
        } else {
            key_div.className = 'col-1 border';
        }
        key_div.innerText = key;
        row_div.appendChild(key_div);
   }

// -- insert data rows
    for(object_item in data_array){
        var entry_div = document.createElement("div");
        entry_div.id = 'e-row'+id.slice(0,8)+object_item;
        entry_div.className = 'row';
        element.appendChild(entry_div);
// -- insert entries in data rows
        for (key in data_array[object_item]){
            var val_div = document.createElement("div");
            val_div.id = key+id.slice(0,8)+object_item;
            if (key == '.section'){
                continue;
            }

            if (key == 'host' || key == 'address' || key == 'status'){
                val_div.className = 'col-2 border';
            } else {
                val_div.className = 'col-1 border';
            }
            val_div.innerText = data_array[object_item][key];
            entry_div.appendChild(val_div);
        }
    }
}

// prod
// fill init table
function fill_brief_table(id, data){
    var row = document.getElementById(id);
    if (row == null){
        console.log('Get lost with tossing IDs');
        return;
    }
    var t_board = document.getElementById('board-'+id);
    var t_fware = document.getElementById('fware-'+id);
    var t_mem = document.getElementById('mem-'+id);
    var t_uptime = document.getElementById('uptime-'+id);
    var t_hdd = document.getElementById('fhdd-'+id);
    if ('ERR' in data) {
        row.className = 'clickable table-danger'
        t_mem.textContent = 'ERR:'
        t_uptime.textContent = data['ERR'];
    } else {
        row.className = 'clickable table-success';
        t_board.textContent = data['board-name'];
        t_fware.textContent = data['version'];
        t_hdd.textContent = data['free-hdd'] + ' %';
        t_uptime.textContent = data['uptime'];
        let mem = parseInt(data['free-memory'], 10);
        t_mem.textContent = mem+' %';

        if (mem <= err_t.freemem_t){
            t_mem.className = 'text-danger';
        }
        if ( parseInt(data['free-hdd']) <= err_t.freehdd_t){
            t_hdd.className = 'text-danger';
        }
        if (parseInt(data['bad-blocks']) > 0){
            t_hdd.className = 'text-danger font-weight-bold';
        }
        if (data['fw_mismatch'] == '1'){
            t_fware.className = 'text-danger';
        }
        t_uptime.textContent = data['uptime'];
    }
}

//PROD
// color row in br table
function color_error(id,data){
        var row = document.getElementById(id);
        if ('ERR' in data) {
            row.className = 'clickable table-danger';
        } else {
            row.className = 'clickable table-success';
        }
}

// PROD
// Print err code in br table one time in br request
function fill_br_err_info(id,data){
    const headers = ['board', 'fware', 'mem', 'fhdd'];
    for(h in headers){
        document.getElementById(headers[h]+'-'+id).innerText = '-';
    }
    const br_err_field = document.getElementById('uptime-'+id);
    br_err_field.innerText = data['ERR'];
    br_err_field.className = 'text-danger text-right';
}

// PROD
// handle err data and fill brief table and add err table
function fill_err_info(id, data){
        data['uniq_id'] = Math.random();
        var row = document.getElementById(id);
        if (row == null){
            console.log('Get lost with tossing IDs');
            return;
        }
        color_error(id, data);

        const div_id = 'c-'+id;
        var element = document.getElementById(div_id);
        element.innerHTML = '';
        var i = 0;

        for ( key in data )  {
            if(key == 'host_id'){
//                continue;
            }
            var row_div = document.createElement("div");
            row_div.id = 'row'+id.slice(0,8)+i;
            row_div.className = 'row';

            var key_div = document.createElement("div");
            key_div.id = key+id.slice(0,8);
            key_div.className = 'col-4 border';
            key_div.innerText = key;

            var val_div = document.createElement("div");
            val_div.id = data[key]+id.slice(0,8);
            val_div.className = 'col-5 border';
            val_div.innerText = data[key];

            element.appendChild(row_div);
            row_div.appendChild(key_div);
            row_div.appendChild(val_div);
            i++
    }
}

//prod
// fill simple 2 row table
function fill_table_flat(id, data_raw){
        var data = data_raw[0];
        var row = document.getElementById(id);
        if (row == null){
            console.log('Get lost with tossing IDs');
            return;
        }
        color_error(id, data);

        const div_id = 'c-'+id;
        var element = document.getElementById(div_id);
        element.innerHTML = '';
        var i = 0;

        for ( key in data )  {
            if(key == 'host_id'){
//                continue;
            }
            var row_div = document.createElement("div");
            row_div.id = 'row'+id.slice(0,8)+i;
            row_div.className = 'row';

            var key_div = document.createElement("div");
            key_div.id = key+id.slice(0,8);
            key_div.className = 'col-4 border';
            key_div.innerText = key;

            var val_div = document.createElement("div");
            val_div.id = data[key]+id.slice(0,8);
            val_div.className = 'col-5 border';
            val_div.innerText = data[key];

            element.appendChild(row_div);
            row_div.appendChild(key_div);
            row_div.appendChild(val_div);
            i++
    }
}

// PROD
// get value from html form
function getValueFromInput(id){
    var elem = document.getElementById(id);
    console.log("IP:" + elem.value)
    return elem.value;
}

//PROD
// Fill table with hidden data and PRE DEFINED cols
function fill_table_complex(id, data_array, main_table_headers, col2_headers, col3_headers){
    console.log(data_array);
    var all_headers = Object.getOwnPropertyNames(data_array[0]);
    if (main_table_headers == undefined){
        main_table_headers = all_headers;
        console.log('DEBUG:all_headers:');
        console.log(all_headers);
    }

    if (col2_headers == undefined){
        col2_headers = [];
    }
    if (col3_headers == undefined){
        col3_headers = [];
    }
    var all_headers = Object.getOwnPropertyNames(data_array[0]);
    const div_id = 'c-'+id;
    var element = document.getElementById(div_id);
    if (element == null){
        console.log('Get lost with tossing IDs');
        return;
    }
    color_error(id, data_array);
    //-------------------------------------
    element.innerHTML = '';
    // -- make row container
    var row_div = document.createElement("div");
    row_div.id = 'p-row'+id.slice(0,8);
    row_div.className = 'row';
    element.appendChild(row_div);
    // ---------- статичная колонка с плюсиком---------
    var key_div = document.createElement("div");
    key_div.id = 'compact'+id.slice(0,8);
    key_div.innerText = '#';
    key_div.className = 'col border bg-iface-table col-1';
    row_div.appendChild(key_div);
    // ---------- столбик с плюсиком---------
    // Fill Main headers
    for (i in main_table_headers){
        var key_div = document.createElement("div");
        key_div.id = main_table_headers[i]+id.slice(0,8);
        key_div.innerText = main_table_headers[i];
        key_div.className = 'col border bg-iface-table col-1';

        if(col2_headers.includes(main_table_headers[i])){
            key_div.className = 'col border bg-iface-table col-2';
        }
        if(col3_headers.includes(main_table_headers[i])){
            key_div.className = 'col border bg-iface-table col-3';
        }
        row_div.appendChild(key_div);
    }
//------------------ header end---------------------
// --

for(object_item in data_array){
//console.log('Parsing DATA entrie:' + object_item + '----------------------');
// --- add data rows ------------
    var entry_div = document.createElement("div");
    entry_div.id = 'e-row'+id.slice(0,8)+object_item;
    entry_div.className = 'row';
    entry_div.setAttribute('data-toggle' , 'collapse');
    entry_div.setAttribute('data-target' , '#h-row'+id.slice(0,8)+object_item);
    entry_div.setAttribute('aria-expanded' , false);
    // add hidden row
    var hidden_row = document.createElement("div");
    hidden_row.id = 'h-row'+id.slice(0,8)+object_item;
    hidden_row.className = 'collapse';
// ----------------------------

    // -- insert entries in data rows
    // распихиваем данные
    // ---------- столбик с плюсиком---------
    var val_div = document.createElement("div");
    val_div.id = 'comp'+id.slice(0,8)+object_item;
    val_div.innerText = '+';
    val_div.className = 'col border col-1';
    entry_div.appendChild(val_div);
    // ---------------------------------------------
    // перебераем все главные заголовки
    for ( elem in main_table_headers){
        var val_div = document.createElement("div");
        val_div.id = main_table_headers[elem]+id.slice(0,8)+object_item;
        val_div.innerText = data_array[object_item][main_table_headers[elem]];
        val_div.className = 'col border col-1';

        if(col2_headers.includes(main_table_headers[elem])){
            val_div.className = 'col border col-2';
        }
        if (col3_headers.includes(main_table_headers[elem])){
            val_div.className = 'col border col-3';
        }
        entry_div.appendChild(val_div);
    }

    // перебераем остальные заголовки
    for ( elem in all_headers){
//        console.log('parsing elem:', all_headers[elem]);
        var h_row = document.createElement("div");
        h_row.id = 'hr-'+all_headers[elem]+id.slice(0,8)+object_item;
        h_row.className = 'row br-hidden-rows';

        var h_div = document.createElement("div");
        h_div.id = all_headers[elem]+id.slice(0,8)+object_item;
//        h_div.innerText = data_array[object_item][all_headers[elem]];
//            Если в заголовке главной таблички есть такой столбец то скипаем и не красим строчку
        if (main_table_headers.includes(all_headers[elem])){
            continue;
        }
        else if (all_headers[elem] == 'disabled'){
            if (data_array[object_item][all_headers[elem]] == 'true'){
                // skip '+' column
                for (let i = 1; i < entry_div.childNodes.length; i++){
                    entry_div.childNodes[i].className += ' text-disabled';
                }
            } else {
                continue;
            }
          }
        else if (all_headers[elem] == 'running' || all_headers[elem] == 'active'){
            if (data_array[object_item][all_headers[elem]] == 'false'){
                entry_div.className += ' text-not-running';
            } else {
                continue;
            }
        }
        else if (all_headers[elem] == 'inactive'){
//            console.log('got inactive');
            if (data_array[object_item][all_headers[elem]] == 'true'){
                entry_div.className += ' text-not-running';
            } else {
                continue;
            }
        }

        else {

            h_div.className = 'col-3 border';
            h_div.innerText = all_headers[elem];

            var v_div = document.createElement("div");
            v_div.className = 'col-5 border';
            v_div.innerText = data_array[object_item][all_headers[elem]];

            h_row.appendChild(h_div);
            h_row.appendChild(v_div);
            hidden_row.appendChild(h_row);
        }
    }
    element.appendChild(entry_div);
    element.appendChild(hidden_row);
  }
}


