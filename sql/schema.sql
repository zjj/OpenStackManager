BEGIN;
CREATE TABLE `user` (
    `id` integer AUTO_INCREMENT PRIMARY KEY,
    `username` varchar(100) UNIQUE,
    `password` varchar(200),
    `email` varchar(100),
    `is_superuser` bool DEFAULT 0
)
;
CREATE TABLE `sessions` (
    `session_id` varchar(128),
    `atime` timestamp DEFAULT CURRENT_TIMESTAMP,
    `data` longtext
)
;
CREATE TABLE `wiki` (
    `id` integer AUTO_INCREMENT PRIMARY KEY,
    `ctx` longtext
)
;
CREATE TABLE `server` (
    `id` integer AUTO_INCREMENT PRIMARY KEY,
    `user` integer,
    `server_name` varchar(128),
    `image` varchar(128),
    `flavor` varchar(128)
)
;
CREATE TABLE `cache` (
    `describle` varchar(128),
    `detail` longtext
)
;

-- if MYSQL ADD THIS line: ALTER TABLE `server` ADD CONSTRAINT `user_id_refs_id_fba847f1` FOREIGN KEY (`user`) REFERENCES `user` (`id`);

COMMIT;

