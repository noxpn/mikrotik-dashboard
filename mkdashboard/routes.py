import sqlalchemy
from Crypto.Hash import SHA3_256
from flask import render_template, url_for, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mkdashboard.nx_dataset as nx_dataset
import mkdashboard.nx_helpers as nx_helpers
import mkdashboard.nx_rosapi as rosapi
from mkdashboard import db, app
from mkdashboard.models import User, RouterBoard


@app.errorhandler(404)
def page_not_found(err):
    return render_template("404.html"), 404


@app.route('/')
def route_index():
    if 'hash' in session and session['hash']:
        return redirect(url_for('rb_dashboard'))
    else:
        return redirect(url_for('user_login'))


# -----------------USER Section--------------------
# get users
@app.route('/user/list')
def user_list():
    if 'hash' in session and session['hash']:
        if 'rw' in session and session['rw'] == 1:
            users = User.query.order_by(User.date.desc()).all()
            return render_template('user_list.html', users=users)
        else:
            return render_template('placeholder_with_mgs.html', msg='NO ADMIN RIGHTS')
    else:
        return render_template('placeholder_with_mgs.html', msg='NO ACCESS RIGHTS')


# add new user
@app.route('/user/add', methods=['POST', 'GET'])
def user_add():
    if request.method == 'POST':
        email = request.form['email']
        if User.query.filter_by(email=email).first() is None:
            raw_pwd = request.form['pwd']
            enc_pwd = generate_password_hash(raw_pwd)
            user_hash = SHA3_256.new()
            user_hash.update(enc_pwd.encode())
            u_hash = user_hash.hexdigest()
            # set 1st registered user to admin
            if User.query.all():
                admin = False
            else:
                admin = True
            user = User(email=email, admin=admin, pwd=enc_pwd, hash=u_hash)
            try:
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('user_login'))
            except Exception as e:
                return render_template('placeholder_with_mgs.html', msg=e)
        else:
            return render_template('placeholder_with_mgs.html', msg='User exist')
    else:
        return render_template('user_add.html')


# user delete
@app.route('/user/<string:u_hash>/delete')
def user_delete(u_hash):
    if 'rw' in session and session['rw'] == 1:
        try:
            user = User.query.get_or_404(u_hash)
            # delete all user rb's also
            devices = RouterBoard.query.filter_by(owner=u_hash).all()
            for d in devices:
                db.session.delete(d)
                db.session.commit()
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('user_list'))
        except Exception:
            return "Some error in user delete"
    else:
        return render_template('placeholder.html')


# user login
@app.route('/user/login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pwd']
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if check_password_hash(user.pwd, pwd) is True:
                session['user'] = user.email
                session['hash'] = user.hash
                key_str = user.hash + user.email
                key_hash = SHA3_256.new()
                key_hash.update(key_str.encode())
                # cut key to 32 bits
                session['key'] = key_hash.hexdigest()[10:42]
                if user.admin:
                    session['rw'] = 1
                else:
                    session['rw'] = 0
                return redirect(url_for('rb_dashboard'))
            else:
                return render_template('placeholder_with_mgs.html', msg='Wrong Pass')
        else:
            return render_template('placeholder_with_mgs.html', msg='No User')
    else:
        if 'hash' in session and len(session['hash']) > 0:
            return redirect(url_for('user_edit'))
        else:
            return render_template('user_login.html')


# user edit
@app.route('/user/edit', methods=['POST', 'GET'])
def user_edit():
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if request.method == 'POST':
            plain_pwd = request.form['pwd']
            enc_pwd = generate_password_hash(plain_pwd)
            user.pwd = enc_pwd
            try:
                db.session.commit()
                return redirect(url_for('user_logout'))
            except Exception as e:
                return render_template('placeholder_with_mgs.html', msg=e)
        else:
            return render_template('user_edit.html', user=user)
    else:
        return render_template('placeholder_with_mgs.html', msg='No User')


# user logout
@app.route('/user/logout')
def user_logout():
    session['user'] = ''
    session['rw'] = ''
    session['hash'] = ''
    session['key'] = ''
    return redirect(url_for('route_index'))
# --------------- END USER SECTION ---------------------------------------------------------------


# -- RB INVENTORY SECTION -----------------------------
# add mikrotik device
@app.route('/rb/add',  methods=['POST', 'GET'])
def rb_add():
    if 'hash' in session and session['hash']:
        if request.method == 'POST':
            name = request.form['h_name']
            ip = request.form['h_ip']
            if not nx_helpers.chk_ip_addr(ip):
                return render_template('placeholder_with_mgs.html', msg='IP_FORMAT_ERR')
            port = request.form['h_port']
            try:
                int(port)
            except ValueError:
                return render_template('placeholder_with_mgs.html', msg='PORT_FORMAT_ERR')
            login = request.form['h_login']
            pwd = request.form['h_pwd']
            owner = session['hash']
            loc = request.form['h_loc']
            isp = request.form['h_isp']
            # ----
            hash_str = ip+login+pwd+owner+name
            rb_hash = SHA3_256.new()
            rb_hash.update(hash_str.encode())
            h_hash = rb_hash.hexdigest()[:32]
            # ---
            enc_pwd = nx_helpers.pwd_encode(pwd)
            if enc_pwd == 'pwd-not-encrypted':
                return render_template('placeholder_with_mgs.html', msg='PWD_ENC_ERR')
            rb_device = RouterBoard(name=name,
                                    ip=ip,
                                    port=port,
                                    login=login,
                                    enc_pwd=enc_pwd,
                                    owner=owner,
                                    isp=isp,
                                    loc=loc,
                                    enabled=nx_helpers.check_to_boolean('h_enabled', request.form),
                                    hash=h_hash)
            try:
                db.session.add(rb_device)
                db.session.commit()
                return redirect(url_for('rb_list'))
            except sqlalchemy.exc.IntegrityError as e:
                return render_template('placeholder_with_mgs.html', msg='DUPE_ENTRY_ERR')
            except Exception:
                return render_template('placeholder_with_mgs.html', msg='OTHER_ERR')
        else:
            return render_template('rb_add.html')
    else:
        return render_template('placeholder_with_mgs.html', msg='ACCESS_RIGHTS_ERR')


# list mikrotik device
@app.route('/rb/list')
def rb_list():
    if 'hash' in session and session['hash']:
        devices = RouterBoard.query.filter_by(owner=session['hash']).all()
        return render_template('rb_list.html', devices=devices)
    else:
        return render_template('placeholder_with_mgs.html', msg='list err')


#  delete mikrotik device
@app.route('/rb/<string:rb_hash>/delete')
def rb_delete(rb_hash):
    if 'hash' in session and session['hash']:
        rb = RouterBoard.query.filter_by(hash=rb_hash).first_or_404()
        if str(rb.owner) == session['hash']:
            try:
                db.session.delete(rb)
                db.session.commit()
                return redirect(url_for('rb_list'))
            except Exception as e:
                return render_template('placeholder_with_mgs.html', msg=e)
        else:
            return render_template('placeholder_with_mgs.html', msg='not owner')
    else:
        return render_template('placeholder_with_mgs.html', msg='access error')


# edit mikrotik device
@app.route('/rb/<string:rb_hash>/edit', methods=['POST', 'GET'])
def rb_edit(rb_hash):
    if 'hash' in session and session['hash']:
        rb = RouterBoard.query.filter_by(hash=rb_hash).first_or_404()
        if str(rb.owner) == session['hash']:
            if request.method == 'POST':
                rb.name = request.form['h_name']
                rb.ip = request.form['h_ip']
                rb.port = request.form['h_port']
                rb.login = request.form['h_login']
                # check if pwd is new
                if request.form['h_pwd'] != 'no_pwd':
                    rb.enc_pwd = nx_helpers.pwd_encode(request.form['h_pwd'])
                rb.loc = request.form['h_loc']
                rb.isp = request.form['h_isp']
                rb.enabled = nx_helpers.check_to_boolean('h_enabled', request.form)
                try:
                    db.session.commit()
                    return redirect(url_for('rb_list'))
                except Exception as e:
                    return render_template('placeholder_with_mgs.html', msg=e)
            else:
                return render_template('rb_edit.html', rb=rb, pwd='no_pwd')
        else:
            return render_template('placeholder_with_mgs.html', msg='not your own device')
    else:
        return render_template('placeholder_with_mgs.html', msg='no powah to edit')


# dashboard list
@app.route('/dashboard')
def rb_dashboard():
    host_list = nx_helpers.get_dev_list_safe()
    return render_template('rb_dashboard.html', host_list=host_list, a_url=nx_dataset.a_url)


# endpoint universal diag cmd
@app.route('/rb/exec', methods=['POST', 'GET'])
def rb_exec():
    if 'hash' not in session or not session['hash']:
        return jsonify({'ERR': 'AUTH'})
    # check param request
    rb_id = get_param_from_request(request, 'id')
    cmd = get_param_from_request(request, 'cmd')
    if 'ERR' in rb_id:
        return jsonify(rb_id)
    if 'ERR' in cmd:
        return jsonify(cmd)

    # check allowed command
    if not nx_helpers.validate_cmd(cmd):
        return jsonify({'ERR': 'CMD_INVALID'})

    raw_data = get_raw_data(rb_id, cmd)
    data_action = nx_dataset.command_list[cmd]
    if data_action == 0:
        result = nx_helpers.normalize_data_headers(raw_data)
    elif data_action == 1:
        normalized_data = nx_helpers.normalize_data_headers(raw_data)
        collapsed_data = nx_helpers.collapse_data(normalized_data)
        result = collapsed_data
    elif data_action == 4:
        result = nx_helpers.parse_log_result(raw_data)
    else:
        return jsonify({'ERR': 'DATA_CORRUPT'})
    return jsonify(result)


# Endpoint for brief table
@app.route('/rb/exec/brinfo', methods=['POST', 'GET'])
def rb_exec_brinfo():
    rb_id = get_param_from_request(request, 'id')
    if isinstance(rb_id, dict):
        return jsonify(rb_id)
    else:
        device = nx_helpers.get_rb_by_id(rb_id)
        if 'ERR' in device:
            return jsonify(device)
        else:
            resource_res = rosapi.exec_simple_cmd_on_rb(device, '/system/resource')
            resource_nfo = rosapi.exec_simple_cmd_on_rb(device, '/system/routerboard')

            if 'ERR' in resource_res:
                return jsonify(resource_res)
            if 'ERR' in resource_nfo:
                return jsonify(resource_nfo)

            free_mem = round(int(resource_res['free-memory'])*100/int(resource_res['total-memory']))
            free_hdd = round(int(resource_res['free-hdd-space'])*100/int(resource_res['total-hdd-space']))
            sum_result = dict()
            sum_result['uptime'] = nx_helpers.parse_uptime(resource_res['uptime'])
            sum_result['free-memory'] = free_mem
            # fix for rb4011 - no bad block info in fw
            if 'bad-blocks' in resource_res.keys():
                sum_result['bad-blocks'] = resource_res['bad-blocks']
            else:
                sum_result['bad-blocks'] = 'no-data'
            # fix for rb4011: RB4011iGS+5HacQ2HnD - too long for brief table
            sum_result['board-name'] = resource_res['board-name'][:10]
            sum_result['version'] = resource_res['version']
            sum_result['free-hdd'] = free_hdd
            sum_result['id'] = rb_id

            if resource_nfo['upgrade-firmware'] != resource_nfo['current-firmware']:
                sum_result['fw_mismatch'] = 1
            else:
                sum_result['fw_mismatch'] = 0

            result = sum_result
            return jsonify(result)


# ping|trace
@app.route('/rb/exec/diag', methods=['POST', 'GET'])
def rb_exec_diag():
    rb_id = get_param_from_request(request, 'id')
    if isinstance(rb_id, dict):
        return jsonify(rb_id)
    else:
        target = get_param_from_request(request, 'target')
        count = get_param_from_request(request, 'count')
        cmd = get_param_from_request(request, 'cmd')
        device = nx_helpers.get_rb_by_id(rb_id)
        try:
            result = rosapi.exec_icmp_diag_on_rb(device, cmd, target, count)
            print(f'_routes_ result: {result}')
            # nx_helpers.parse_raw_data(result)
            if cmd == '/ping':
                ros_res = nx_helpers.parse_ping_output(result)
            elif cmd == '/tool/traceroute':
                ros_res = nx_helpers.parse_tracert_output(result)
            else:
                ros_res = {'ERR': 'PARSE'}
            return jsonify(ros_res)
        except Exception as e:
            return render_template('placeholder_with_mgs.html', msg=e)


# Test endpoint
# testing any command - admin mode
@app.route('/rb/exec/test', methods=['POST', 'GET'])
def rb_exec_test():
    rb_id = get_param_from_request(request, 'id')
    cmd = get_param_from_request(request, 'cmd')
    if 'rw' in session and session['rw'] == 1:
        data = get_raw_data(rb_id, cmd)
        result = nx_helpers.normalize_data_headers(data)
        return jsonify(result)
    else:
        return {'ERR': 'ACC'}


# prod
def get_param_from_request(req, param):
    if req.method == 'POST':
        if param in req.json:
            return request.json[param]
        else:
            return {'ERR': '31 POST no param: <' + param + '>'}
    elif request.method == 'GET':
        if param in request.args:
            return request.args[param]
        else:
            return {'ERR': '32 GET no param: <' + param + '>'}
    else:
        return {'ERR': '33'}


# route request
# prod
def get_raw_data(rb_id, command):
    if isinstance(rb_id, dict):
        return rb_id
    else:
        try:
            device = nx_helpers.get_rb_by_id(rb_id)
            if 'ERR' in device:
                return device
            else:
                return rosapi.exec_simple_cmd_on_rb(device, command)
        except Exception as e:
            print(f'Exception <get_raw_data>: {e}')
            return e


