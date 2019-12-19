import os
import sqlite3
from sqlite3 import IntegrityError

from comic_dl.core import config


class ComicDB():
    location = config.ASSETS_PATH
    if not os.path.exists(location):
        os.makedirs(location)

    def __init__(self):
        self.conn = sqlite3.connect(
            os.path.join(self.__class__.location, config.__dbName__)
        )
        self.cursor = self.conn.cursor()

        sql_create_comics_table = """
        CREATE TABLE IF NOT EXISTS comics (
            id integer PRIMARY KEY,
            title text NOT NULL UNIQUE,
            link text NOT NULL UNIQUE,
            alias text NOT NULL UNIQUE,
            latest_issue integer,
            last_downloaded integer
        );
        """
        self.cursor.execute(sql_create_comics_table)

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

    def close(self):
        self.conn.close()

    def save(self, **kwargs):
        try:
            sql_insert_comic = """
            INSERT INTO comics (title, link, alias,
            latest_issue, last_downloaded)
            VALUES ("{title}", "{link}", "{alias}",
            {latest_issue}, {last_downloaded});
            """.format(**kwargs)
            self.cursor.execute(sql_insert_comic)
            self.conn.commit()

        except IntegrityError:
            sql_update_comic = """
            UPDATE comics
            SET latest_issue = {latest_issue},
                last_downloaded = {last_downloaded}
            WHERE alias = "{alias}";
            """.format(**kwargs)
            self.cursor.execute(sql_update_comic)
            self.conn.commit()

    def delete(self, alias):
        sql_delete_comic = """
        DELETE FROM comics
        WHERE alias = "{}";
        """.format(alias)
        self.cursor.execute(sql_delete_comic)
        self.conn.commit()

    def get_all(self):
        sql_select_all = """
        SELECT * FROM comics
        ORDER BY latest_issue DESC, last_downloaded DESC;
        """
        self.cursor.execute(sql_select_all)
        return self.cursor.fetchall()

    def get(self, alias):
        sql_select_by_alias = """
        SELECT * FROM comics WHERE alias="{}";
        """.format(alias)
        self.cursor.execute(sql_select_by_alias)
        return self.cursor.fetchone()
