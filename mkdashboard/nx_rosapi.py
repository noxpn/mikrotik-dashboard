from ssl import SSLError
import routeros_api
from routeros_api.exceptions import *
from mkdashboard import nx_helpers
import mkdashboard.nx_dataset as nx_dataset


def ros(host, port, login, pwd):
    api = routeros_api.RouterOsApiPool(
        host=host,
        port=port,
        username=login,
        password=pwd,
        plaintext_login=True,
        use_ssl=True,
        ssl_verify=False,
        ssl_verify_hostname=False,)
    return api


# prod
def exec_icmp_diag_on_rb(host, cmd, ip_adr, count):
    if not nx_helpers.chk_ip_addr(ip_adr):
        return {'ERR': 'DST_IP', 'host_id': host['id']}
    count = normalize_count(count)
    if cmd in nx_dataset.diag_command_list:
        cmd_param = {'address': ip_adr, 'count': str(count)}
    else:
        return {'ERR': 'CMD_PARAM'}
    connection = ros(host['ip'], host['port'], host['login'], host['pwd'])
    result = {'ERR': 'BIN_CMD'}
    try:
        api = connection.get_api()
        ros_result = api.get_binary_resource('/').call(cmd[1:], cmd_param)
    except RouterOsApiCommunicationError as e:
        try:
            error_code_part = str(e.original_message).split('(')[1][:1]
            if int(error_code_part) == 6:
                result = {'ERR': 'PWD'}
            elif int(error_code_part) == 9:
                result = {'ERR': 'ACC'}
            else:
                result = {'ERR': 'CMD'}
        except IndexError:
            result = {'ERR': e.original_message.decode()}
    except SSLError:
        result = {'ERR': 'SSL'}
    except RouterOsApiConnectionError:
        result = {'ERR': 'NET'}
    except TypeError:
        result = {'ERR': 'TYPE'}
    except Exception as e:
        print(f'exception other: {e}')
        result = {'ERR': e}
    else:
        result = ros_result
    finally:
        connection.disconnect()
        return result


# prod
# normalize number of echo requests
# to prevent infinity loop on rb
def normalize_count(count):
    res = count
    if int(res) <= 0:
        res = 1
    if int(res) > 10:
        res = 10
    return res


# PROD
# main cmd
def exec_simple_cmd_on_rb(host, command):
    if host['pwd'] == 'pwd-not-decrypted':
        return {'ERR': 'DECRYPT_KEY', 'host_id': host['id']}
    connection = ros(host['ip'], host['port'], host['login'], host['pwd'])
    try:
        api = connection.get_api()
        ros_result = api.get_resource(command)
    except RouterOsApiConnectionError:
        result = {'ERR': 'NET', 'host_id': host['id']}
    except RouterOsApiCommunicationError as e:
        try:
            error_code_part = str(e.original_message).split('(')[1][:1]
            if int(error_code_part) == 6:
                result = {'ERR': 'PWD'}
            elif int(error_code_part) == 9:
                result = {'ERR': 'ACC'}
            else:
                result = {'ERR': 'CMD'}
        except IndexError:
            result = {'ERR': e.original_message.decode()}
    except SSLError:
        result = {'ERR': 'SSL', 'host_id': host['id']}
    except TypeError:
        result = {'ERR': 'TYPE', 'host_id': host['id']}
    except Exception as e:
        print(f"EXCEPTION: OTHER: {e}")
        print(f"EXCEPTION: OTHER: {type(e)}")
        result = {'ERR': 'OTHER', 'host_id': host['id']}
    else:
        try:
            tmp_result = ros_result.get()
        except RouterOsApiCommunicationError as e:
            return {'ERR': e.original_message.decode()}
        except Exception:
            return {'ERR': 'OTHER'}
        # cast from routeros_api.api_communicator.base.AsynchronousResponse
        final_ros_result = list(tmp_result)

        if len(final_ros_result) == 0:
            result = {'ERR': 'EMPTY', 'host_id': host['id']}
        elif final_ros_result[0]:
            if len(final_ros_result) == 1:
                result = final_ros_result[0]
                result['host_id'] = host['id']
            else:
                result = final_ros_result
        else:
            result = {'ERR': 'EMPTY', 'host_id': host['id']}
    finally:
        connection.disconnect()
    return result


if __name__ == '__main__':
    pass
