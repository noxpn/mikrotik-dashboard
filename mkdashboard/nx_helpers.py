import socket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import session

from mkdashboard.models import RouterBoard
import mkdashboard.nx_dataset as nx_dataset


def get_dev_list_fast():
    """
    ONLY FOR TESTING
    :return: tuple of user devices NO FILTER
    """
    hosts = []
    # if 'rw' in session and session['rw'] == 1:
    if 'hash' in session:
        devices = RouterBoard.query.filter_by(owner=session['hash']).all()
        hosts = tuple([{'host': d.ip, 'port': d.port, 'login': d.login, 'pwd': pwd_decode(d.enc_pwd)} for d in devices])
    return hosts


def get_dev_list_slow():
    """
    Check Valid IP and Enabled NO FILTER
    :return: () of user devices OR empty ()
    """
    hosts = []
    if 'rw' in session and session['rw'] == 1:
        devices = RouterBoard.query.filter_by(owner=session['hash']).all()
        for d in devices:
            if d.enabled:
                if chk_ip_addr(d.ip):
                    decoded_pwd = pwd_decode(d.enc_pwd)
                    device_dict = {'host': d.ip, 'port': d.port, 'login': d.login, 'pwd': decoded_pwd, 'id': d.hash}
                    hosts.append(device_dict)
    return tuple(hosts)


def get_dev_list_safe():
    """
    Check Valid IP and Enabled NO LOGIN/PWD
    :return: () of user devices OR empty ()
    """
    hosts = []
    if 'hash' in session and session['hash']:
        devices = RouterBoard.query.filter_by(owner=session['hash']).all()
        for d in devices:
            if d.enabled:
                if chk_ip_addr(d.ip):
                    device_dict = {'ip': d.ip,
                                   'id': d.hash,
                                   'name': d.name,
                                   'loc': d.loc,
                                   'isp': d.isp, }
                    hosts.append(device_dict)
    return tuple(hosts)


def get_dev_list_super_slow():
    hosts = []
    if 'rw' in session and session['rw'] == 1:
        devices = RouterBoard.query.filter_by(owner=session['hash']).all()
        for d in devices:
            try:
                print(socket.getaddrinfo(d.ip, 8729, family=socket.AF_INET, proto=socket.IPPROTO_TCP))
                decoded_pwd = pwd_decode(d.enc_pwd)
                device_dict = {'host': d.ip, 'port': d.port, 'login': d.login, 'pwd': decoded_pwd}
                hosts.append(device_dict)
            except Exception as e:
                print(e)
    return tuple(hosts)


def get_static_test_host():
    return {'host': '172.25.25.1', 'login': 'api', 'pwd': '11111111'}


def chk_ip_addr_prt(addr_part):
    try:
        return str(int(addr_part)) == addr_part and 0 <= int(addr_part) <= 255
    except:
        return False


def chk_ip_addr(ip_addr):
    if ip_addr.count('.') == 3 and all(chk_ip_addr_prt(prt) for prt in ip_addr.split('.')):
        return True
    else:
        return False


def check_to_boolean(param_in_form, form):
    if param_in_form in form:
        return form[param_in_form] == 'on'
    else:
        return False


def parse_uptime(uptime):
    if uptime.split('w')[0] == uptime:
        up_days = uptime.split('d')[0]
        try:
            int_days = int(up_days)
            return int_days
        except ValueError:
            return 0
        except Exception as e:
            print(f'Exception<parse_uptime>: {e}')
            return 0
    else:
        weeks = uptime.split("w")[0]
        days = parse_uptime(uptime.split("w")[1])
        try:
            up_days = int(weeks) * 7 + int(days)
            return up_days
        except ValueError:
            return 0
        except Exception as e:
            print(f'Exception<parse_uptime>: {e}')
            return 0


def pwd_encode(pwd):
    key = session['key'].encode()
    try:
        data = (('0'*16)+pwd).encode()
        e_cipher = AES.new(key, AES.MODE_CBC)
        ciphertext = e_cipher.encrypt(pad(data, AES.block_size))
        return ciphertext
    except ValueError as e:
        print(f'Exception in <pwd_encode>: {e}')
        return 'pwd-not-encrypted'
    except Exception as e:
        print(f'Exception in <pwd_encode>: {e}')
        return 'pwd-not-encrypted'


def pwd_decode(pwd):
    key = session['key'].encode()
    try:
        iv = pwd[0:16]
        d_cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        unc_pwd = unpad(d_cipher.decrypt(pwd[16:]), AES.block_size)
        return unc_pwd.decode()
    except ValueError as e:
        print(f'Exception in <pwd_decode>: {e}')
        return 'pwd-not-decrypted'
    except Exception as e:
        print(f'Exception in <pwd_decode>: {e}')
        return 'pwd-not-decrypted'


def parse_raw_data(data):
    print(data)
    for d in data:
        print(f'{len(d)}#{d}')


def get_rb_by_id(rb_id):
    # print(session['user'])
    # if 'rw' in session and session['rw'] == 1:
    if 'user' not in session or not session['user']:
        return {'ERR': 'AUTH', 'host_id': rb_id}
    try:
        d = RouterBoard.query.filter_by(hash=rb_id).first()
        if d.owner != session["hash"]:
            return {'ERR': 'NOT_OWN_DEVICE', 'host_id': rb_id}
        if d is None:
            return {'ERR': 'NO_DEVICE_WITH_ID', 'host_id': rb_id}
        else:
            decoded_pwd = pwd_decode(d.enc_pwd)
            device_dict = {'ip': d.ip, 'port': d.port, 'login': d.login, 'pwd': decoded_pwd, 'id': rb_id}
            return device_dict
    except Exception as e:
        print(f'Exeption:<get_rb_by_id>: {e}')
        return {'ERR': 'GET_DEVICE', 'host_id': rb_id}


def rb_id_err_handler(rb_id):
    if rb_id == '31':
        return {'ERR': 'POST-NoID'}
    elif rb_id == '32':
        return {'ERR': 'GET-NoID'}
    elif rb_id == '33':
        return {'ERR': 'NoID'}
    else:
        return rb_id


def validate_cmd(cmd):
    if cmd in nx_dataset.command_list:
        return True
    else:
        return False


# PROD
def normalize_data_headers(data, headers=set()):
    if 'ERR' in data:
        return data
    # if dict - have 1 record - no need to normalize
    # return as list
    if isinstance(data, dict):
        return [data]
    data_output = convert_to_new_list(data)
    header_set = set.copy(headers)
    # Fill header set with missing values
    for header_item in data_output:
        for i in header_item:
            header_set.add(i)
    # Fill dictionary to full header version
    # add '-1' values to missing headers keys
    for item in data_output:
        for header in header_set:
            exist_header = item.get(header)
            if exist_header is None:
                item[header] = '-1'
    return data_output


# PROD
# Make Abbr from custom keys and remove from data
def collapse_data(data):
    if 'ERR' in data:
        return data
    data_output = convert_to_new_list(data)
    headers_to_collapse = ('active', 'static', 'dynamic', 'connect')
    for data_item in data_output:
        data_item['abr'] = ''
        for key in data_item:
            if key in headers_to_collapse and data_item[key] == 'true':
                data_item['abr'] = data_item['abr'] + str(key).upper()[0]
        for key in headers_to_collapse:
            if key in data_item:
                data_item.pop(key)
    return data_output


# if only one record incoming - it is dict type
# need list of dicts to parse
def convert_to_new_list(data):
    if isinstance(data, dict):
        data_output = [data]
    else:
        data_output = data[:]
    return data_output


# prod
def parse_log_result(data):
    if 'ERR' in data:
        return data
    topics = set()
    for d in data:
        int_id = int(d.get('id').split('*')[1], 16)     # convert id from hex to int
        d.update({'id': int_id})                        # change hex id to int
        topic_keys = set(d.get('topics').split(','))    # get topics
        topics = topics.union(topic_keys)               # add entry topics to all topics set
    topic_obj = {'all_topics': list(topics)}            # to list because jsonify pukes on set
    data.append(topic_obj)                              # append all topics to last pos
    return data


# prod
def parse_tracert_output(output):
    """
    Strip all records exept last
    in traceroute output
    :param output: [{key: b'value'},]
    :return: [{key:str(value)},]
    """
    if isinstance(output, dict):
        return output
    else:
        seq_num = 0
        last_elem_of_output = output[-1]
        output_result = []
        if '.section' in last_elem_of_output.keys():
            seq_num = int(last_elem_of_output['.section'].decode('utf-8'))
        for record in output:
            if '.section' in record.keys() and int(record['.section'].decode('utf-8')) == seq_num:
                output_result.append(parse_bin_dict(record))
        if len(output_result) == 0:
            output_result = {'ERR': 'EMPTY'}
        return output_result


# prod
def parse_ping_output(output):
    """
    decode byte to str values
    :param output: [{key: b'value'},]
    :return: [{key:str(value)},]
    """
    if isinstance(output, dict):
        return output
    else:
        output_result = []
        for record in output:
            output_result.append(parse_bin_dict(record))
        if len(output_result) == 0:
            output_result = {'ERR': 'EMPTY'}
        return output_result


# prod
def parse_bin_dict(bin_dict):
    """
    convert byte value in dict to string
    :param bin_dict
     {key : b'value'}
    :return: {key : str(value)}
    """
    str_dict = {}
    for k in bin_dict:
        str_dict[k] = bin_dict[k].decode("utf-8")
    return str_dict
