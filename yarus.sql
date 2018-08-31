-- MySQL dump 10.13  Distrib 8.0.12, for Linux (x86_64)
--
-- Host: localhost    Database: yarus
-- ------------------------------------------------------
-- Server version	8.0.12

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `yarus_bind`
--

DROP TABLE IF EXISTS `yarus_bind`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_bind` (
  `client_id` varchar(64) NOT NULL,
  `repo_id` varchar(64) NOT NULL,
  `channel_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_channel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_channel` (
  `ID` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `manager_id` varchar(255) DEFAULT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `last_sync` int(11) DEFAULT NULL,
  `release` varchar(255) DEFAULT NULL,
  `distribution` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `channel_id` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_client` (
  `ID` varchar(255) NOT NULL,
  `IP` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `version` varchar(20) NOT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `last_check` int(11) DEFAULT NULL,
  `manager_id` varchar(255) DEFAULT NULL,
  `distribution` varchar(255) DEFAULT NULL,
  `architecture` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_daterepository`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_daterepository` (
  `ID` varchar(255) NOT NULL,
  `repository` varchar(255) NOT NULL,
  `date` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_group` (
  `ID` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `manager_id` varchar(255) DEFAULT NULL,
  `last_check` int(11) NOT NULL,
  `creation_date` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_grouped`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_grouped` (
  `group_id` varchar(255) DEFAULT NULL,
  `client_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_link` (
  `channel_id` varchar(255) NOT NULL,
  `repo_id` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_linkrcs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_linkrcs` (
  `ID` varchar(255) NOT NULL,
  `distribution` varchar(64) NOT NULL,
  `release` varchar(64) NOT NULL,
  `creation_date` int(11) NOT NULL,
  `manager_id` int(11) NOT NULL,
  `channels` varchar(1000) DEFAULT NULL,
  `architecture` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_package` (
  `ID` varchar(255) NOT NULL,
  `repository` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `architecture` varchar(255) NOT NULL,
  `version` varchar(255) NOT NULL,
  `release` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `checksum_type` varchar(255) NOT NULL,
  `checksum` varchar(255) NOT NULL,
  `summary` varchar(255) NOT NULL,
  `component` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_repository`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_repository` (
  `ID` varchar(255) NOT NULL,
  `URL` varchar(255) DEFAULT NULL,
  `distribution` varchar(255) DEFAULT NULL,
  `release` varchar(255) NOT NULL,
  `components` varchar(255) DEFAULT NULL,
  `architectures` varchar(50) DEFAULT NULL,
  `type` varchar(3) DEFAULT NULL,
  `last_sync` int(11) DEFAULT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `manager_id` varchar(255) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `repo_id` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_scheduled`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_scheduled` (
  `ID` varchar(255) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `action` varchar(255) DEFAULT NULL,
  `minute` varchar(255) NOT NULL,
  `hour` varchar(255) NOT NULL,
  `day_of_month` varchar(255) NOT NULL,
  `month` varchar(255) NOT NULL,
  `day_of_week` varchar(255) NOT NULL,
  `day_place` varchar(255) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `manager_id` varchar(255) NOT NULL,
  `creation_date` int(11) NOT NULL,
  `last_date` int(11) NOT NULL,
  `object_type` varchar(255) DEFAULT NULL,
  `object_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_task` (
  `ID` varchar(32) NOT NULL,
  `status` varchar(255) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `action` varchar(255) NOT NULL,
  `manager_id` varchar(255) DEFAULT NULL,
  `creation_date` int(11) NOT NULL,
  `start_time` int(11) NOT NULL,
  `end_time` int(11) NOT NULL,
  `object_type` varchar(255) DEFAULT NULL,
  `object_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `task_id` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_update`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_update` (
  `date` int(11) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `object_type` varchar(255) DEFAULT NULL,
  `ID` varchar(255) NOT NULL,
  KEY `ID` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_upgradable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_upgradable` (
  `object_id` varchar(255) DEFAULT NULL,
  `approved` int(11) NOT NULL,
  `ID` varchar(255) DEFAULT NULL,
  `package_id` varchar(255) DEFAULT NULL,
  `object_type` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_upgraded`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_upgraded` (
  `package_id` varchar(255) NOT NULL,
  `update_id` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `yarus_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `yarus_user` (
  `ID` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role_id` int(11) NOT NULL,
  `mail` varchar(255) NOT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `token` varchar(64) NOT NULL,
  `token_expire` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `user_id` (`ID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_user`
--

LOCK TABLES `yarus_user` WRITE;
/*!40000 ALTER TABLE `yarus_user` DISABLE KEYS */;
INSERT INTO `yarus_user` VALUES ('1','admin','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',1,'admin@yarus.net',0,'',0);
