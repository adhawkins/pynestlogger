import MySQLdb


class PyNestLoggerDB:
    def __init__(self, host, database, user, password):
        self.conn = MySQLdb.connect(host=host, db=database, user=user, passwd=password)

        if self.conn:
            self.check_database()

    def check_database(self):
        database_version = 0

        if self.table_exists("version"):
            database_version = self.get_version()

        if database_version == 0:
            self.create_database()

        if database_version < 2:
            self.update_to_v2()

        if database_version < 3:
            self.update_to_v3()

        if database_version < 4:
            self.update_to_v4()

        if database_version < 5:
            self.update_to_v5()

    def table_exists(self, table):
        cursor = self.conn.cursor()
        cursor.execute(
            "SHOW TABLES LIKE %s",
            [
                table,
            ],
        )
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False

    def get_version(self):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM `version`")
        row = cursor.fetchone()
        return row["version"]

    def set_version(self, version):
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM `version`")

        cursor.execute(
            "INSERT INTO `version` VALUES (%s);",
            [
                version,
            ],
        )

        self.conn.commit()

    def create_database(self):
        cursor = self.conn.cursor()
        if self.table_exists("version"):
            cursor.execute("DROP TABLE `version`;")

        cursor.execute(
            """CREATE TABLE `version` (
                  `version` int(11) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""
        )

        self.set_version(1)

        if self.table_exists("structures"):
            cursor.execute("DROP TABLE `structures`;")

        cursor.execute(
            """CREATE TABLE `structures` (
                  `id` varchar(100) NOT NULL,
                  `name` varchar(100) DEFAULT NULL,
                  `away` varchar(10) DEFAULT NULL,
                  `country` varchar(10) DEFAULT NULL,
                  `postcode` varchar(20) DEFAULT NULL,
                  `timezone` varchar(100) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""
        )

        cursor.execute("ALTER TABLE `structures` ADD UNIQUE KEY `id` (`id`);")

        if self.table_exists("thermostats"):
            cursor.execute("DROP TABLE `thermostats`;")

        cursor.execute(
            """CREATE TABLE `thermostats` (
                  `id` varchar(100) NOT NULL,
                  `name` varchar(100) DEFAULT NULL,
                  `namelong` varchar(100) DEFAULT NULL,
                  `tempscale` varchar(2) DEFAULT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""
        )

        cursor.execute("ALTER TABLE `thermostats` ADD UNIQUE KEY `id` (`id`);")

        if self.table_exists("measurements"):
            cursor.execute("DROP TABLE `measurements`;")

        cursor.execute(
            """CREATE TABLE `measurements` (
              `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
              `structure_id` varchar(100) NOT NULL,
              `thermostat_id` varchar(100) NOT NULL,
              `targettemp` int(11) NOT NULL,
              `ambienttemp` int(11) NOT NULL,
              `humidity` int(11) NOT NULL,
              `hvacstate` varchar(20) NOT NULL													#off, heating, cooling, heat-cool, eco
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""
        )

        cursor.execute(
            "ALTER TABLE `measurements` ADD PRIMARY KEY (`timestamp`,`structure_id`,`thermostat_id`);"
        )

    def update_to_v2(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """ALTER TABLE `measurements`
            MODIFY COLUMN ambienttemp FLOAT,
            MODIFY COLUMN humidity FLOAT,
            MODIFY COLUMN targettemp FLOAT
        """
        )

        self.set_version(2)

    def update_to_v3(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """ALTER TABLE `measurements`
            ADD COLUMN `away` varchar(10) DEFAULT 'home';
        """
        )

        cursor.execute(
            """ALTER TABLE `structures`
            DROP COLUMN `away`;
        """
        )

        self.set_version(3)

    def update_to_v4(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """ALTER TABLE `measurements`
            ADD COLUMN `loft` FLOAT DEFAULT 0.0;
        """
        )

        self.set_version(4)

    def update_to_v5(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """DROP TABLE `structures`;
            DROP TABLE `thermostats`;
            ALTER TABLE `measurements` DROP PRIMARY KEY;
            ALTER TABLE `measurements` DROP COLUMN `structure_id`;
            ALTER TABLE `measurements` DROP COLUMN `thermostat_id`;
            ALTER TABLE `measurements` DROP COLUMN `away`;
            ALTER TABLE `measurements` ADD PRIMARY KEY (`timestamp`);
        """
        )

        self.set_version(5)

    def round_number(number):
        return round(number * 2) / 2

    def record_measurement(self, ambient, humidity, target, state, loft):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO `measurements` SET ambienttemp=%s,
                                                    humidity=%s,
                                                    targettemp=%s,
                                                    hvacstate=%s,
                                                    loft=%s""",
            [
                PyNestLoggerDB.round_number(ambient),
                PyNestLoggerDB.round_number(humidity),
                PyNestLoggerDB.round_number(target),
                state,
                PyNestLoggerDB.round_number(loft[0]["internal temperature"]),
            ],
        )

        cursor.execute(
            "DELETE FROM `measurements` where `timestamp` < ADDDATE(NOW(), INTERVAL -10 DAY)"
        )

        self.conn.commit()
