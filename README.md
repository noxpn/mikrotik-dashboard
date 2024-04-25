###Действия на маршрутизаторе Mikrotik
###Создать пользователя, обладающего минимальными правами для использования API
```
/user
group add name=api policy=read,test,api
add name=api_user group=api password=SomePASSWORD
#Создать сертификат для работы SSL API
/certificate
add name=ca-api country=RU state=RU locality=local organization=N/A unit=N/A common-name=ca-api key-size=2048 days-valid=4000 key-usage=key-cert-sign,crl-sign
sign name=ca-api number=ca-api
add name=api-crt country=RU state=RU locality=local organization=N/A unit=N/A common-name=api-crt key-size=2048 days-valid=4000 key-usage=tls-client,tls-server
sign ca=ca-api api-crt name=api-crt
#Включить сам сервис SSL API и прописать ему сделанный сетификат
/ip service
set api-ssl disabled=no
set api-ssl certificate=api-crt

#Модифицировать firewall для доступа к прту на котором работает SSL API (8729 TCP)
/ip firewall filter
add action=accept chain=input dst-port=8729 protocol=tcp in-interface=ether1 src-address=SRC_IP place-before=0
```   

###Фикс для старой версии библиотеки
```
    rude fix in 'venv/Lib/site-packages/routeros_api/sentence.py':
    ----------------------------------
    def get_api_format(self):
        formated = [self.path + self.command]
        for key, value in self.attributes.items():
            if type(value) == str:
                value = str.encode(value)
            formated.append(b'=' + key + b'=' + value)
            for query in self.queries:
                formated.extend(query.get_api_format())
            if self.tag is not None:
                formated.append(b'.tag=' + self.tag)
        return formated
    -------------------------------------
    
    to create db in python console in PyCharm:
        > from mkdashboard import db
        > db.create_all()
    -------------------------------------
```
###Запуск программы 
```
To start app on Windows (in cmd line)
1. make venv:
    > python -m venv \path\to\venv
    > \path\to\venv\Scripts\activate.bat
    > python -m pip install -r requirements.txt
    > \path\to\venv\Scripts\deactivate.bat 
2. run app:
    > python nxapp.py
-----------

To run in docker

in container build dir:
> git clone http://git.lotos.dom/noxp/mtdb.git
> python -m venv mtdb/venv
> docker volume create mtdb-vol
> docker build --build-arg https_proxy=http://10.10.10.6:9090 -t mtdb:lastest mtdb/
> docker container run --name mtdb -e "URL=$(hostname -f)" -v mtdb-vol:/app/mkdashboard/db -p 80:5080 mtdb:lastest
> docker container start mtdb
``` 

 