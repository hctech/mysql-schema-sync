#!/usr/bin/env python
# coding: utf-8
# Author: huangchao

from schemaobject import SchemaObject
from schemaobject import syncdb, connection
import optparse
import sys
import time
import pymysql


def parse_cmd_line():
    usage = """
        %prog [options] <source> <target>
        source/target format: mysql://user:pass@host:port/database"""
    description = """
        A MySQL Schema Synchronization Utility"""

    parser = optparse.OptionParser(usage=usage, description=description)

    parser.add_option("-a", "--sync-auto-inc", dest="sync_auto_inc", action="store_true", default=False, help="sync the AUTO_INCREMENT value for eache table.")
    parser.add_option("-c", "--sync-comments", dest="sync_comments", action="store_true", default=False, help="sync the COMMENT field for all tables AND columns")

    return parser


def main():
    options, args = parse_cmd_line().parse_args(sys.argv[1:])

    if (not args) or (len(args) != 2):
        print(parse_cmd_line().print_help())
        return 0

    src_mysql_conn_url, target_mysql_conn_url = args
    src_mysql_object = SchemaObject(src_mysql_conn_url, 'utf8')
    target_mysql_object = SchemaObject(target_mysql_conn_url, 'utf8')

    options = dict(
        sync_auto_inc=options.sync_auto_inc,
        sync_comments=options.sync_comments
    )

    # patch sql and revert sql
    patch = []
    revert = []

    print("\033[92m=== start compare mysql db schema ===\033[0m")
    for p, r in syncdb.sync_schema(src_mysql_object.selected, target_mysql_object.selected, options):
        if isinstance(p, syncdb.SyncSchemaStep):
            print("\033[94m" + p.msg + "\033[0m")
        else:
            print(p + '\n')
            patch.append(p)
            revert.append(r)
    print("\033[92m=== end compare mysql db schema ===\033[0m")

    is_exec = raw_input("exec sync ddl sql on target db? [Y/N]")
    if is_exec.upper() == 'Y':
        exec_total = len(patch)
        exec_success_count = 0
        exec_failed_count = 0

        kwargs = connection.parse_database_url(target_mysql_conn_url)
        del kwargs['protocol']
        target_db = pymysql.connect(**kwargs)
        target_cursor = target_db.cursor()

        print("\033[92m=== start sync schema ===\033[0m")
        for index, p in enumerate(patch):
            try:
                target_cursor.execute(p)
                target_db.commit()
                print("\033[92mexec sync sql success, revert sql:\033[0m")
                print(revert[index])
                exec_success_count += 1
            except Exception as e:
                target_db.rollback()
                print("\033[91mexec sync sql failed: %s, exec sql:\033[0m" % e)
                print(p)
                exec_failed_count += 1
            time.sleep(1)
        target_db.close()
        print("\033[92m=== sync result: exec total: %d, success count: %d, failed count: %d ===\033[0m" %(exec_total, exec_success_count, exec_failed_count))
    else:
        print("\033[92m=== thank you for use, Bye! ===\033[0m")

if __name__ == '__main__':
    main()
    # db_conn = pymysql.connect(host='localhost', user='huangchao', password='huangchao', database='blog')
    # db_cursor = db_conn.cursor()
    # db_cursor.execute("-- select * from users;")
    # for row in db_cursor.fetchall():
    #     print(row)
    # db_conn.close()
