from mkdashboard import app, db_file
import os
import sys


host = '0.0.0.0'
port = '5080'


def get_host_url():
    localhost = '127.0.0.1'
    os_type = sys.platform

    if os_type.startswith('win'):
        url = localhost + ':' + port
    elif os_type.startswith('lin'):
        print(f'DEBUG: OS LIN')
        host_name = os.environ.get("URL")
        if host_name is None:
            print(f'DEBUG: NO HOSTNAME PROVIDED')
            print(f'DEBUG: run image with "-e "URL=frontend_url""')
            print(f'DEBUG: or "-e $(hostname -f)"')
            print(f'DEBUG: Exiting')
            sys.exit(2)
        else:
            print(f'DEBUG: HOSTNAME PROVIDED# {host_name}')
            url = host_name
    else:
        print(f'DEBUG: OS HZ')
        url = localhost+':'+port
    return url


web_url = get_host_url()


if __name__ == '__main__':
    try:
        database = open('mkdashboard/'+db_file)
    except IOError as e:
        print('*'*56)
        print(f'*** WARMING: Creating Brand New Shiny Clean DataBase ***')  # not a misspell
        print('*'*56)
        from mkdashboard import db
        db.create_all()
    else:
        database.close()
    finally:
        app.run(host=host, port=port, debug=False)
