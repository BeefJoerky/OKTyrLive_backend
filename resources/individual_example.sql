-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               11.6.2-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for mop
CREATE DATABASE IF NOT EXISTS `mop` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `mop`;

-- Dumping structure for table mop.mopclass
CREATE TABLE IF NOT EXISTS `mopclass` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL DEFAULT '',
  `ord` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`cid`,`id`),
  KEY `ord` (`ord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopclass: ~0 rows (approximately)
DELETE FROM `mopclass`;
INSERT INTO `mopclass` (`cid`, `id`, `name`, `ord`) VALUES
	(10, 1, 'M21', 10),
	(10, 2, 'W21', 20),
	(10, 3, 'M35', 30),
	(10, 4, 'W35', 40),
	(10, 5, 'M50', 50),
	(10, 6, 'W50', 60),
	(10, 7, 'M70', 70),
	(10, 8, 'W80', 80);

-- Dumping structure for table mop.mopclasscontrol
CREATE TABLE IF NOT EXISTS `mopclasscontrol` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `leg` tinyint(4) NOT NULL,
  `ord` tinyint(4) NOT NULL,
  `ctrl` int(11) NOT NULL DEFAULT 0,
  `distance` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`cid`,`id`,`leg`,`ord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopclasscontrol: ~0 rows (approximately)
DELETE FROM `mopclasscontrol`;

-- Dumping structure for table mop.mopcompetition
CREATE TABLE IF NOT EXISTS `mopcompetition` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL DEFAULT '',
  `date` date NOT NULL DEFAULT '2013-11-04',
  `organizer` varchar(64) NOT NULL DEFAULT '',
  `homepage` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`cid`,`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopcompetition: ~0 rows (approximately)
DELETE FROM `mopcompetition`;
INSERT INTO `mopcompetition` (`cid`, `id`, `name`, `date`, `organizer`, `homepage`) VALUES
	(10, 1, 'MeOS Tredagars, etapp 3', '2015-05-09', 'Melin Software HB', '');

-- Dumping structure for table mop.mopcompetitor
CREATE TABLE IF NOT EXISTS `mopcompetitor` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL DEFAULT '',
  `org` int(11) NOT NULL DEFAULT 0,
  `cls` int(11) NOT NULL DEFAULT 0,
  `stat` tinyint(4) NOT NULL DEFAULT 0,
  `st` int(11) NOT NULL DEFAULT 0,
  `rt` int(11) NOT NULL DEFAULT 0,
  `bib` int(11) DEFAULT NULL,
  `tstat` tinyint(4) NOT NULL DEFAULT 0,
  `it` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`cid`,`id`),
  KEY `org` (`org`),
  KEY `cls` (`cls`),
  KEY `stat` (`stat`,`rt`),
  KEY `st` (`st`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopcompetitor: ~164 rows (approximately)
DELETE FROM `mopcompetitor`;
INSERT INTO `mopcompetitor` (`cid`, `id`, `name`, `org`, `cls`, `stat`, `st`, `rt`, `bib`, `tstat`, `it`) VALUES
	(10, 1, 'Erik Hjerpe', 11, 1, 0, 328420, 0, 105, 1, 0),
	(10, 2, 'Märta Poupard', 10, 1, 0, 328440, 0, 111, 1, 0),
	(10, 3, 'Jessica Askeljung', 25, 1, 0, 331950, 0, 103, 1, 0),
	(10, 4, 'Håkan Pettersson', 9, 1, 0, 335330, 0, 100, 1, 0),
	(10, 5, 'Lennart Nordström', 18, 1, 0, 335560, 0, 107, 1, 0),
	(10, 6, 'Isak Ohlsson', 14, 1, 0, 326280, 0, 102, 1, 0),
	(10, 7, 'Erik Hansson', 18, 1, 0, 360000, 0, 112, 1, 0),
	(10, 8, 'Ragnar Berggrund', 27, 1, 0, 362400, 0, 110, 1, 0),
	(10, 9, 'Erland Josephsson', 30, 1, 0, 361200, 0, 113, 1, 0),
	(10, 10, 'Karin Alheim', 4, 1, 0, 333230, 0, 101, 1, 0),
	(10, 11, 'Line Lauri', 30, 1, 0, 332370, 0, 108, 1, 0),
	(10, 12, 'Magnus Karlsson-Landén', 26, 1, 0, 324000, 0, 106, 1, 0),
	(10, 16, 'Maxim Clevnert', 5, 2, 0, 365000, 0, 218, 1, 0),
	(10, 17, 'Karin Lennartsson', 19, 2, 0, 365870, 0, 213, 1, 0),
	(10, 18, 'Oda Funke', 9, 2, 0, 400800, 0, 207, 1, 0),
	(10, 19, 'Johanna Berglund', 20, 2, 0, 367260, 0, 204, 1, 0),
	(10, 20, 'Axel Johansson', 29, 2, 0, 397200, 0, 201, 1, 0),
	(10, 21, 'Arne Carlson Bjernald', 11, 2, 0, 364410, 0, 205, 1, 0),
	(10, 22, 'Annika Mossberg', 16, 2, 0, 367040, 0, 217, 1, 0),
	(10, 23, 'Yvonne Olsson', 3, 2, 0, 403200, 0, 208, 1, 0),
	(10, 24, 'Lina Olsson', 19, 2, 0, 365390, 0, 222, 1, 0),
	(10, 25, 'Oskar Falk Sörqvist', 6, 2, 0, 367980, 0, 211, 1, 0),
	(10, 26, 'Håkan Svensson', 25, 2, 0, 364480, 0, 223, 1, 0),
	(10, 27, 'Jens Alm', 3, 2, 0, 366210, 0, 226, 1, 0),
	(10, 28, 'Albin Bergvall', 18, 2, 0, 396000, 0, 202, 1, 0),
	(10, 29, 'Katarina Larsson', 6, 2, 0, 360680, 0, 220, 1, 0),
	(10, 30, 'Tomas Krantz', 4, 2, 0, 364480, 0, 214, 1, 0),
	(10, 31, 'Jerry Detterfelt', 22, 2, 0, 360000, 0, 215, 1, 0),
	(10, 32, 'Erik Bergstrand', 23, 2, 0, 363310, 0, 224, 1, 0),
	(10, 33, 'Edvin Persson', 29, 2, 0, 398400, 0, 219, 1, 0),
	(10, 34, 'Bo Gunnarsson', 23, 2, 0, 365400, 0, 206, 1, 0),
	(10, 35, 'Tomas Johansson', 12, 2, 0, 402000, 0, 200, 1, 0),
	(10, 36, 'Carina Lundström', 29, 2, 0, 369300, 0, 210, 1, 0),
	(10, 37, 'Ina Eklöv', 15, 2, 0, 369530, 0, 225, 1, 0),
	(10, 38, 'Katarina Lundgren', 26, 2, 0, 399600, 0, 209, 1, 0),
	(10, 39, 'Kristina Thuresson', 30, 2, 0, 367350, 0, 216, 1, 0),
	(10, 43, 'Ulf Carlsson', 20, 3, 0, 382800, 0, 326, 1, 0),
	(10, 44, 'Karin Kraft', 20, 3, 0, 381600, 0, 317, 1, 0),
	(10, 45, 'Lena Eriksson', 17, 3, 0, 351510, 0, 309, 1, 0),
	(10, 46, 'Niklas Berggren', 23, 3, 0, 349330, 0, 319, 1, 0),
	(10, 47, 'Viktor Olausson', 2, 3, 0, 385200, 0, 321, 1, 0),
	(10, 48, 'Kristina Karlsson', 24, 3, 0, 352310, 0, 323, 1, 0),
	(10, 49, 'Martin Olovsson', 14, 3, 0, 353680, 0, 316, 1, 0),
	(10, 50, 'Oskar Wilander', 6, 3, 0, 351410, 0, 314, 1, 0),
	(10, 51, 'Anders Rylander', 29, 3, 0, 345600, 0, 302, 1, 0),
	(10, 52, 'Erik Forsberg', 5, 3, 0, 380400, 0, 318, 1, 0),
	(10, 53, 'Lars Jonsson', 2, 3, 0, 353250, 0, 312, 1, 0),
	(10, 54, 'Ulf Enges', 27, 3, 0, 346880, 0, 307, 1, 0),
	(10, 55, 'Jan Leksell', 10, 3, 0, 353030, 0, 301, 1, 0),
	(10, 56, 'K-G Palm', 21, 3, 0, 350300, 0, 324, 1, 0),
	(10, 57, 'Lisbeth Amren', 4, 3, 0, 355580, 0, 310, 1, 0),
	(10, 58, 'Carl Andersson', 9, 3, 0, 378000, 0, 325, 1, 0),
	(10, 59, 'Kerstin Johansson', 12, 3, 0, 351520, 0, 305, 1, 0),
	(10, 60, 'Christina Pettersson', 5, 3, 0, 355650, 0, 300, 1, 0),
	(10, 61, 'Ulf Ohlsson', 15, 3, 0, 384000, 0, 303, 1, 0),
	(10, 62, 'Andreas Rönnestrand', 21, 3, 0, 352460, 0, 315, 1, 0),
	(10, 63, 'Lars Karlsson', 18, 3, 0, 342960, 0, 311, 1, 0),
	(10, 64, 'Lisbeth Ingström', 29, 3, 0, 342000, 0, 320, 1, 0),
	(10, 65, 'Ingmar Karlsson', 21, 3, 0, 352930, 0, 306, 1, 0),
	(10, 66, 'Caroline Englund', 20, 3, 0, 379200, 0, 308, 1, 0),
	(10, 70, 'Torgny Andersson', 14, 4, 0, 349480, 0, 400, 1, 0),
	(10, 71, 'Thomas Mårtensson', 14, 4, 0, 347140, 0, 407, 1, 0),
	(10, 72, 'Christer Brynell', 16, 4, 0, 360720, 0, 406, 1, 0),
	(10, 73, 'Anita Axmalm', 3, 4, 0, 349750, 0, 402, 1, 0),
	(10, 74, 'Roland Åhlund', 18, 4, 0, 346970, 0, 416, 1, 0),
	(10, 75, 'Laila Wahlström', 21, 4, 0, 349780, 0, 413, 1, 0),
	(10, 76, 'Bengt Ahlstrand', 2, 4, 0, 378000, 0, 410, 1, 0),
	(10, 77, 'Britt-Inger Blomstrand', 26, 4, 0, 379200, 0, 419, 1, 0),
	(10, 78, 'Joel Carlsson', 26, 4, 0, 380400, 0, 412, 1, 0),
	(10, 79, 'Christer Gustafsson', 27, 4, 0, 344690, 0, 405, 1, 0),
	(10, 80, 'Jenny Carlsson', 2, 4, 0, 346770, 0, 417, 1, 0),
	(10, 81, 'Bengt Wigge', 2, 4, 0, 347550, 0, 403, 1, 0),
	(10, 82, 'Sven Högberg', 30, 4, 0, 342000, 0, 420, 1, 0),
	(10, 83, 'Ann-Britt Moqvist', 11, 4, 0, 348460, 0, 408, 1, 0),
	(10, 84, 'Arne Andersson', 11, 4, 0, 349230, 0, 415, 1, 0),
	(10, 85, 'Kim Svärd', 14, 4, 0, 346580, 0, 414, 1, 0),
	(10, 86, 'Thomas Johansson', 23, 4, 0, 346880, 0, 401, 1, 0),
	(10, 87, 'Bengt Rhodin', 28, 4, 0, 355790, 0, 409, 1, 0),
	(10, 91, 'Roger Johansson', 9, 5, 0, 380400, 0, 616, 1, 0),
	(10, 92, 'Nils Rensgard', 23, 5, 0, 343480, 0, 604, 1, 0),
	(10, 93, 'Linda Salgård', 2, 5, 0, 346280, 0, 610, 1, 0),
	(10, 94, 'Olle Palm', 11, 5, 0, 347890, 0, 607, 1, 0),
	(10, 95, 'Karin Dahlberg', 17, 5, 0, 342000, 0, 620, 1, 0),
	(10, 96, 'Hampus Niklasson', 18, 5, 0, 349540, 0, 611, 1, 0),
	(10, 97, 'Kathrine Gustavsson', 15, 5, 0, 350260, 0, 608, 1, 0),
	(10, 98, 'Mattias Svensson', 2, 5, 0, 379200, 0, 617, 1, 0),
	(10, 99, 'Hanna Erixon', 14, 5, 0, 348940, 0, 603, 1, 0),
	(10, 100, 'Per Bjelk', 18, 5, 0, 342150, 0, 618, 1, 0),
	(10, 101, 'Roy Kruskopf', 20, 5, 0, 345820, 0, 613, 1, 0),
	(10, 102, 'Ulf Skoog', 15, 5, 0, 348260, 0, 615, 1, 0),
	(10, 103, 'Cristina Segerslätt', 8, 5, 0, 384000, 0, 614, 1, 0),
	(10, 104, 'Sigrid Bäcklund', 19, 5, 0, 381600, 0, 601, 1, 0),
	(10, 105, 'Wilma Grahn', 1, 5, 0, 386400, 0, 602, 1, 0),
	(10, 106, 'Susanne Gumaelius', 17, 5, 0, 382800, 0, 606, 1, 0),
	(10, 107, 'Lucie Björklund', 26, 5, 0, 346500, 0, 609, 1, 0),
	(10, 108, 'Emil Jonsson', 28, 5, 0, 385200, 0, 600, 1, 0),
	(10, 112, 'Anders Svahn', 20, 6, 0, 345130, 0, 714, 1, 0),
	(10, 113, 'Lena Östergren', 8, 6, 0, 342760, 0, 723, 1, 0),
	(10, 114, 'Bo Arne Christer Fogelberg', 6, 6, 0, 346480, 0, 713, 1, 0),
	(10, 115, 'Alice Olsson', 20, 6, 0, 378000, 0, 722, 1, 0),
	(10, 116, 'Gunnel Andersson', 7, 6, 0, 353540, 0, 710, 1, 0),
	(10, 117, 'Ove Kvick', 15, 6, 0, 343450, 0, 715, 1, 0),
	(10, 118, 'Ylva Larsson', 8, 6, 0, 342000, 0, 706, 1, 0),
	(10, 119, 'Tilda Abrahamsson', 28, 6, 0, 348200, 0, 700, 1, 0),
	(10, 120, 'Kerstin Wissting', 18, 6, 0, 344360, 0, 717, 1, 0),
	(10, 121, 'Anders Malmberg', 4, 6, 0, 348140, 0, 707, 1, 0),
	(10, 122, 'Olle Kringstad', 2, 6, 0, 344100, 0, 704, 1, 0),
	(10, 123, 'Roland Rudh', 12, 6, 0, 381600, 0, 720, 1, 0),
	(10, 124, 'Tomas Thorman', 26, 6, 0, 354930, 0, 718, 1, 0),
	(10, 125, 'Lennart Sjödin', 20, 6, 0, 355440, 0, 705, 1, 0),
	(10, 126, 'Anna Groth', 18, 6, 0, 344580, 0, 724, 1, 0),
	(10, 127, 'Ing-Marie Holm', 7, 6, 0, 344410, 0, 719, 1, 0),
	(10, 128, 'Margit Grahn', 12, 6, 0, 346560, 0, 702, 1, 0),
	(10, 129, 'Kristin Eriksson', 26, 6, 0, 344670, 0, 709, 1, 0),
	(10, 130, 'Julia Bång', 12, 6, 0, 345480, 0, 711, 1, 0),
	(10, 131, 'Anna Olsson', 13, 6, 0, 379200, 0, 701, 1, 0),
	(10, 132, 'Nils-Olof Sundberg', 21, 6, 0, 344770, 0, 708, 1, 0),
	(10, 133, 'Johan Larsson', 9, 6, 0, 380400, 0, 716, 1, 0),
	(10, 137, 'Lars Molin', 3, 7, 0, 353480, 0, 811, 1, 0),
	(10, 138, 'Petra Sellgren', 1, 7, 0, 346610, 0, 812, 1, 0),
	(10, 139, 'Kari Kårén', 28, 7, 0, 348360, 0, 800, 1, 0),
	(10, 140, 'Axel Andersson', 4, 7, 0, 343170, 0, 805, 1, 0),
	(10, 141, 'Karin Sjöberg', 25, 7, 0, 378000, 0, 802, 1, 0),
	(10, 142, 'Helena Edvinsson', 3, 7, 0, 352830, 0, 807, 1, 0),
	(10, 143, 'Christer Hyland', 4, 7, 0, 347920, 0, 810, 1, 0),
	(10, 144, 'Kevin Rosén', 13, 7, 0, 348970, 0, 803, 1, 0),
	(10, 145, 'Tomas Johansson', 2, 7, 0, 342000, 0, 801, 1, 0),
	(10, 146, 'Ingela Ackelman', 30, 7, 0, 348820, 0, 808, 1, 0),
	(10, 147, 'Anna Nordh', 22, 7, 0, 355440, 0, 806, 1, 0),
	(10, 151, 'Johan Olsson', 24, 8, 0, 345760, 0, 902, 1, 0),
	(10, 152, 'Ulf Kumlin', 23, 8, 0, 380400, 0, 903, 1, 0),
	(10, 153, 'Graham Eriksson', 8, 8, 0, 348310, 0, 912, 1, 0),
	(10, 154, 'Per Schanow', 19, 8, 0, 379200, 0, 913, 1, 0),
	(10, 155, 'Malena Karlsson', 25, 8, 0, 348350, 0, 904, 1, 0),
	(10, 156, 'Doris Karlsson', 7, 8, 0, 343950, 0, 901, 1, 0),
	(10, 157, 'Arne Hjälte', 10, 8, 0, 385200, 0, 911, 1, 0),
	(10, 158, 'Maja-Lisa Bylund', 30, 8, 0, 378000, 0, 908, 1, 0),
	(10, 159, 'Carina Nilsson', 19, 8, 0, 345400, 0, 909, 1, 0),
	(10, 160, 'Rolf Sten Erland Gullbrandsson', 26, 8, 0, 343580, 0, 906, 1, 0),
	(10, 161, 'Jan Landergren', 9, 8, 0, 342000, 0, 907, 1, 0),
	(10, 162, 'Vacant', 888888888, 1, 0, 363600, 0, 109, 1, 0),
	(10, 163, 'Vacant', 888888888, 1, 0, 364800, 0, 114, 1, 0),
	(10, 164, 'Geroge Ohlin', 31, 1, 0, 366000, 0, 104, 1, 0),
	(10, 165, 'Vacant', 888888888, 2, 0, 406800, 0, 221, 1, 0),
	(10, 166, 'Vacant', 888888888, 2, 0, 404400, 0, 203, 1, 0),
	(10, 167, 'Vacant', 888888888, 2, 0, 405600, 0, 212, 1, 0),
	(10, 168, 'Vacant', 888888888, 3, 0, 388800, 0, 322, 1, 0),
	(10, 169, 'Vacant', 888888888, 3, 0, 387600, 0, 313, 1, 0),
	(10, 170, 'Vacant', 888888888, 3, 0, 386400, 0, 304, 1, 0),
	(10, 171, 'Vacant', 888888888, 4, 0, 381600, 0, 404, 1, 0),
	(10, 172, 'Vacant', 888888888, 4, 0, 384000, 0, 418, 1, 0),
	(10, 173, 'Vacant', 888888888, 4, 0, 382800, 0, 411, 1, 0),
	(10, 174, 'Vacant', 888888888, 5, 0, 388800, 0, 619, 1, 0),
	(10, 175, 'Rolf Hansson', 32, 5, 0, 378000, 0, 605, 1, 0),
	(10, 176, 'Vacant', 888888888, 5, 0, 387600, 0, 612, 1, 0),
	(10, 177, 'Vacant', 888888888, 6, 0, 382800, 0, 703, 1, 0),
	(10, 178, 'Vacant', 888888888, 6, 0, 384000, 0, 712, 1, 0),
	(10, 179, 'Vacant', 888888888, 6, 0, 385200, 0, 721, 1, 0),
	(10, 180, 'Vacant', 888888888, 7, 0, 381600, 0, 813, 1, 0),
	(10, 181, 'Vacant', 888888888, 7, 0, 380400, 0, 809, 1, 0),
	(10, 182, 'Vacant', 888888888, 7, 0, 379200, 0, 804, 1, 0),
	(10, 183, 'Vacant', 888888888, 8, 0, 384000, 0, 910, 1, 0),
	(10, 184, 'Vacant', 888888888, 8, 0, 382800, 0, 905, 1, 0),
	(10, 185, 'Vacant', 888888888, 8, 0, 381600, 0, 900, 1, 0);

-- Dumping structure for table mop.mopcontrol
CREATE TABLE IF NOT EXISTS `mopcontrol` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`cid`,`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopcontrol: ~0 rows (approximately)
DELETE FROM `mopcontrol`;

-- Dumping structure for table mop.moporganization
CREATE TABLE IF NOT EXISTS `moporganization` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`cid`,`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.moporganization: ~0 rows (approximately)
DELETE FROM `moporganization`;
INSERT INTO `moporganization` (`cid`, `id`, `name`) VALUES
	(10, 1, 'Degerfors OK'),
	(10, 2, 'Ankarsrums OK'),
	(10, 3, 'Bodafors OK'),
	(10, 4, 'Burseryds IF'),
	(10, 5, 'Domnarvets GOIF'),
	(10, 6, 'Gamleby OK'),
	(10, 7, 'Grangärde OK'),
	(10, 8, 'Halmstad OK'),
	(10, 9, 'Hedesunda IF'),
	(10, 10, 'OK Forsarna'),
	(10, 11, 'Hultsfreds OK'),
	(10, 12, 'Häverödals SK'),
	(10, 13, 'IFK Kiruna'),
	(10, 14, 'K 3 IF'),
	(10, 15, 'Kjula IF'),
	(10, 16, 'Krokeks OK'),
	(10, 17, 'Laxå OK'),
	(10, 18, 'Ljusne-Ala OK'),
	(10, 19, 'OK Mangen'),
	(10, 20, 'Nilivaara IS'),
	(10, 21, 'Nyköpings OK'),
	(10, 22, 'Robertsfors IK'),
	(10, 23, 'OK Roto'),
	(10, 24, 'Sigtuna OK'),
	(10, 25, 'Skellefteå OK'),
	(10, 26, 'FK Snapphanarna'),
	(10, 27, 'Stigfinnarna'),
	(10, 28, 'IK Surd'),
	(10, 29, 'Tandsbyns IF'),
	(10, 30, 'OK Tranan'),
	(10, 31, 'Rånäs OK'),
	(10, 32, 'LKAB OK'),
	(10, 888888888, 'Vacant');

-- Dumping structure for table mop.mopradio
CREATE TABLE IF NOT EXISTS `mopradio` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `ctrl` int(11) NOT NULL,
  `rt` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`cid`,`id`,`ctrl`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopradio: ~0 rows (approximately)
DELETE FROM `mopradio`;

-- Dumping structure for table mop.mopteam
CREATE TABLE IF NOT EXISTS `mopteam` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL DEFAULT '',
  `org` int(11) NOT NULL DEFAULT 0,
  `cls` int(11) NOT NULL DEFAULT 0,
  `stat` tinyint(4) NOT NULL DEFAULT 0,
  `st` int(11) NOT NULL DEFAULT 0,
  `rt` int(11) NOT NULL DEFAULT 0,
  `bib` int(11) DEFAULT NULL,
  PRIMARY KEY (`cid`,`id`),
  KEY `org` (`org`),
  KEY `cls` (`cls`),
  KEY `stat` (`stat`,`rt`),
  KEY `st` (`st`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopteam: ~0 rows (approximately)
DELETE FROM `mopteam`;

-- Dumping structure for table mop.mopteammember
CREATE TABLE IF NOT EXISTS `mopteammember` (
  `cid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `leg` tinyint(4) NOT NULL,
  `ord` tinyint(4) NOT NULL,
  `rid` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`cid`,`id`,`leg`,`ord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- Dumping data for table mop.mopteammember: ~0 rows (approximately)
DELETE FROM `mopteammember`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
