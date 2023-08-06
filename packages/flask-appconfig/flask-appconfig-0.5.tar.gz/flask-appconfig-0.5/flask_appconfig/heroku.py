#!/usr/bin/env python

from urlparse import urlparse
from . import env


def from_heroku_envvars(config):
        var_map = {
            # SQL-Alchemy
            'DATABASE_URL': 'SQLALCHEMY_DATABASE_URI',

            # newer-style
            'HEROKU_POSTGRESQL_ORANGE_URL': 'SQLALCHEMY_DATABASE_URI',

            # Celery w/ RabbitMQ
            'BROKER_URL': 'RABBITMQ_URL',

            'REDISTOGO_URL': 'REDIS_URL',
            'MONGOLAB_URI': 'MONGO_URI',
            'MONGOHQ_URL': 'MONGO_URI',
            'CLOUDANT_URL': 'COUCHDB_URL',

            'MEMCACHIER_SERVERS': 'CACHE_MEMCACHED_SERVERS',
            'MEMCACHIER_USERNAME': 'CACHE_MEMCACHED_USERNAME',
            'MEMCACHIER_PASSWORD': 'CACHE_MEMCACHED_PASSWORD',
        }

        var_list = [
            # Sentry
            'SENTRY_DSN',

            # Exceptional
            'EXCEPTIONAL_API_KEY',

            # Flask-GoogleFed
            'GOOGLE_DOMAIN',

            # Mailgun
            'MAILGUN_API_KEY', 'MAILGUN_SMTP_LOGIN', 'MAILGUN_SMTP_PASSWORD',
            'MAILGUN_SMTP_PORT', 'MAILGUN_SMTP_SERVER',

            # SendGrid
            'SENDGRID_USERNAME', 'SENDGRID_PASSWORD'
        ]

        # import the relevant envvars
        env.from_envvars(config, envvars=var_list, as_json=False)
        env.from_envvars(config, envvars=var_map, as_json=False)

        # fix up configuration
        if 'MAILGUN_SMTP_SERVER' in config:
            config['SMTP_SERVER'] = config['MAILGUN_SMTP_SERVER']
            config['SMTP_PORT'] = config['MAILGUN_SMTP_PORT']
            config['SMTP_LOGIN'] = config['MAILGUN_SMTP_LOGIN']
            config['SMTP_PASSWORD'] = config['MAILGUN_SMTP_PASSWORD']
            config['SMTP_USE_TLS'] = True
        elif 'SENDGRID_USERNAME' in config:
            config['SMTP_SERVER'] = 'smtp.sendgrid.net'
            config['SMTP_PORT'] = 25
            config['SMTP_LOGIN'] = config['SENDGRID_USERNAME']
            config['SMTP_PASSWORD'] = config['SENDGRID_PASSWORD']
            config['SMTP_USE_TLS'] = True

        # convert to Flask-Mail specific configuration
        if 'MAILGUN_SMTP_SERVER' in config or\
           'SENDGRID_PASSWORD' in config:

            config['MAIL_SERVER'] = config['SMTP_SERVER']
            config['MAIL_PORT'] = config['SMTP_PORT']
            config['MAIL_USE_TLS'] = config['SMTP_USE_TLS']
            config['MAIL_USERNAME'] = config['SMTP_LOGIN']
            config['MAIL_PASSWORD'] = config['SMTP_PASSWORD']

        # for backwards compatiblity, redis:
        if 'REDIS_URL' in config:
            url = urlparse(config['REDIS_URL'])
            config['REDIS_HOST'] = url.hostname
            config['REDIS_PORT'] = url.port
            config['REDIS_PASSWORD'] = url.password
            # FIXME: missing db#?

        if 'MONGO_URI' in config:
            url = urlparse(config['MONGO_URI'])
            config['MONGODB_USER'] = url.username
            config['MONGODB_PASSWORD'] = url.password
            config['MONGODB_HOST'] = url.hostname
            config['MONGODB_PORT'] = url.port
            config['MONGODB_DB'] = url.path[1:]
