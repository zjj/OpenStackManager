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

CREATE TABLE server(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user        NOT NULL REFERENCES user(id),
    server_name VARCHAR(128),
    image       VARCHAR(128),
    flavor      VARCHAR(128),
    public_key  VARCHAR(128),
);

INSERT INTO server (user, server_name, image, flavor, public_key) values (1,'server_jj','image_idasdf','flavorasf','eeeeewerwerwer');

CREATE TABLE wiki(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ctx         TEXT
);

INSERT INTO wiki (ctx) values ("please edit the index page manually. markdown");

