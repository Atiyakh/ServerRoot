-- The following table names are forbidden [archive, record, connection]
-- Use the same structure, and follow the same pattern of the comments below
-- MySql DBMS is strongly recommended
-- Use `_connection_` as the name of the clients' ip

/*START*/
CREATE TABLE accounts(
	id INT AUTO_INCREMENT,
	username VARCHAR(50) UNIQUE,
	password VARCHAR(128) NOT NULL,
	_connection_ VARCHAR(200),
	PRIMARY KEY (id)
);
/*END*/
