from contextlib import contextmanager
from typing import Any

import pgdb

from osiris.base.environments import env


def new_connection(name: str, db_name: str, **kwargs) -> pgdb.Connection:
    """
    Open New connection. It is caller responsibility to close connection after use.
    Alternatively you may use new_connection with context manager

    Example of defined secret:
        {'username': 'DB_USER_NAME', 'password': 'DB_USER_PASSWORD', 'engine': 'redshift',
        'host': 'specified-redshift-cluster-name.region-name.redshift.amazonaws.com',
        'port': 5439,'dbClusterIdentifier': 'specified-redshift-cluster-name'}

    :param name: Secret Name defining the connection information in SecretManager
    :param db_name: database name
    :return: db connection
    """

    definition = env.get_property(f"vault.{name}")

    return pgdb.connect(host=f"{definition['host']}:{definition['port']}",
                        database=db_name,
                        user=definition['username'],
                        password=definition['password'],
                        **kwargs)


@contextmanager
def open_connection(name, db, **kwargs) -> pgdb.Connection:
    try:
        con = new_connection(name, db, **kwargs)
        yield con
    finally:
        con.close()


def execute_scalar(con: pgdb.Connection, sql_text: str, **kwargs) -> Any:
    """
    Execute scalar query
    :param con: connection
    :param sql_text:
    :param kwargs:
    :return: scalar value
    """
    with con.cursor() as cursor:
        cursor.execute(sql_text, **kwargs)
        return cursor.fetchone()[0]
