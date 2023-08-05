=========
pyvkoauth
=========

pyvkoauth - модуль для OAuth-авторизации приложения в малоизвестной социальной
сети ВКонтакте_. Позволяет получить ``access_token`` путем авторизации
клиентских (Standalone) приложений (`подробнее о методе в официальной
документации`_). Требуются email и пароль пользователя, но зато возможно
обойтись без использования какого-либо тяжелого браузерного движка.

.. _ВКонтакте: http://vk.com
.. _подробнее о методе в официальной документации: http://vk.com/pages?oid=-1&p=%D0%90%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F_%D0%BA%D0%BB%D0%B8%D0%B5%D0%BD%D1%82%D1%81%D0%BA%D0%B8%D1%85_%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D0%B9

Установка
=========

Из PYPI:

::

    pip install pyvkoauth

Из репозитория:

::

    pip install -e hg+ssh://hg@bitbucket.org/cordalace/pyvkoauth#egg=pyvkoauth

Использование
=============

::

    from pyvkoauth import auth
    # user data
    user_email = 'ivanov@mail.ru'
    user_password = 'strong_password'
    # application data
    client_id = 2013400
    scope = 49151
    response = auth(user_email, user_password, client_id, scope)
    access_token = response['access_token']
    expires_in = response['expires_in']
    user_id = response['user_id']

В примере ``user_email`` и ``user_password`` - адрес почты и пароль
пользователя соответственно; ``client_id`` - идентификатор приложения (так же
известный как ``APP_ID``); ``scope`` - запрашиваемые права доступа приложения;
``access_token`` - ключ доступа к API; ``expires_in`` - время жизни ключа
доступа в секундах; ``user_id`` - идентификатор авторизовавшегося
пользователя.
