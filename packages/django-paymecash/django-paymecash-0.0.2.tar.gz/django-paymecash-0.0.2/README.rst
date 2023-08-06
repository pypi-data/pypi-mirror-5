=====
Dajngo paymecash
=====

Приложения для приема платежей через систему http://tf.org/


=====
Quick start
=====

1. Добавить 'paymecash' INSTALLED_APPS::

      INSTALLED_APPS = (
            # ...
            'paymecash',
      )


2. Добавить ``url(r'^paymecash/', include('paymecash.urls')),`` в urls.py

3. Обязательные параметры settings.py::

      # Номер кошелька и ключь, полученые после регистрации
      PAYMECASH_WALLET_ID = '000000001111'
      PAYMECASH_SECRET_KEY = 'qCck7SpoSdrtfsqCmm7SNTSe'

4. Добавить логер с именем ``paymecash``::

      LOGGING = {
              'version': 1,
              'disable_existing_loggers': False,
              'formatters': {
              'verbose': {
                    'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(message)s'
              }
          },
          'handlers': {
              'paymecash': {
                  'level': 'DEBUG',
                  'class': 'logging.handlers.WatchedFileHandler',
                  'filename': os.path.join(ROOT, 'paymecash.log'),
                  'formatter': 'verbose'
              }
          },
          'loggers': {
              'paymecash': {
                  'handlers': ['paymecash'],
                  'level': 'ERROR',
                  'propagate': True
              }
          }
      }

5. Выполните ``python manage.py syncdb`` для создание таблицы с платежами или выполните мограцию, если вы используете south: ``python manage.py migrate paymecash``

6. Задайте в личном кабинете ( https://tf.org/app/#/integration ) callback URL http://example.com/paymecash/confirm/