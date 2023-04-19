/* SQLITE */
CREATE TABLE IF NOT EXISTS `models` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `nom` TEXT NOT NULL,
  `type` INTEGER NOT NULL
);

INSERT INTO `models` (`id`, `nom`, `type`) VALUES (1, 'test', 1);