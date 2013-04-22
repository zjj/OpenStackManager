CREATE TABLE user(
     id           INTEGER PRIMARY KEY AUTOINCREMENT,
     username     VARCHAR(100) UNIQUE,
     password     VARCHAR(128),
     email        VARCHAR(75) UNIQUE,
     is_superuser BOOL NOT NULL DEFAULT 0
  );


CREATE TABLE sessions(
     session_id CHAR(128) UNIQUE NOT NULL,
     atime      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
     data       TEXT
  );

