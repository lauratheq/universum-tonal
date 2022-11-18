SELECT genre.name, COUNT(genre.name) AS genre_count FROM `plays`
LEFT JOIN play_genre ON plays.id = play_genre.play_id
LEFT JOIN genre ON genre.id = play_genre.genre_id
GROUP BY genre.name
ORDER BY genre_count DESC, plays.date ASC, genre.id ASC
LIMIT 50


SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `genre`;
CREATE TABLE `genre` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


DROP TABLE IF EXISTS `plays`;
CREATE TABLE `plays` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `artist` text NOT NULL,
  `album` text NOT NULL,
  `track` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


DROP TABLE IF EXISTS `play_genre`;
CREATE TABLE `play_genre` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `play_id` bigint(20) unsigned NOT NULL,
  `genre_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `play_genre_fk0` (`play_id`),
  KEY `play_genre_fk1` (`genre_id`),
  CONSTRAINT `play_genre_fk0` FOREIGN KEY (`play_id`) REFERENCES `plays` (`id`),
  CONSTRAINT `play_genre_fk1` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;