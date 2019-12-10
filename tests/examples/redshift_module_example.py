def run_it():
    from osiris.connector.redshift_module import open_connection, execute_scalar

    with open_connection('dev/redshift/connection', 'dev') as c:
        print("server time: %s" % execute_scalar(c, "SELECT CURRENT_TIMESTAMP"))


if __name__ == '__main__':
    run_it()
