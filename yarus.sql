-- MySQL dump 10.13  Distrib 5.6.40, for Linux (x86_64)
--
-- Host: localhost    Database: yarus
-- ------------------------------------------------------
-- Server version	5.6.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
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
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_bind` (
  `client_id` varchar(64) NOT NULL,
  `repo_id` varchar(64) NOT NULL,
  `channel_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_bind`
--

LOCK TABLES `yarus_bind` WRITE;
/*!40000 ALTER TABLE `yarus_bind` DISABLE KEYS */;
INSERT INTO `yarus_bind` VALUES ('l9akbfkf0plmtg5vikv9b4ojmju1t653','8wfcov8hplov98t2lxkcgh2se7ik7oml',''),('sc711v55fjc1kqwqggy6si5w53slj80j','8wfcov8hplov98t2lxkcgh2se7ik7oml',''),('vat5zzoqkpx8tj7ya34tdgmghx69rfp0','','na2bnv5hpw3etsvrtd4t5xcvz8huni5n'),('kcruqu2ckeyrv9x00b7aym8ikz2jh6l0','','na2bnv5hpw3etsvrtd4t5xcvz8huni5n'),('0ff9guudivreqh8av48zd0eacn0eb7xz','','na2bnv5hpw3etsvrtd4t5xcvz8huni5n'),('l5fxoowkjf3es5ulkyvwoqq9hi8065bf','8wfcov8hplov98t2lxkcgh2se7ik7oml',''),('py1fc5nte63t8o0jyuktvc6vgna526nv','8wfcov8hplov98t2lxkcgh2se7ik7oml',''),('xfzv6v8j6qmducum2696v8qy7trvssg6','','na2bnv5hpw3etsvrtd4t5xcvz8huni5n'),('0rcr7ynhpysykjpkmf15letr4tf1w7ec','','na2bnv5hpw3etsvrtd4t5xcvz8huni5n');
/*!40000 ALTER TABLE `yarus_bind` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_channel`
--

DROP TABLE IF EXISTS `yarus_channel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_channel` (
  `ID` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `manager_id` int(11) NOT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `last_sync` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `channel_id` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_channel`
--

LOCK TABLES `yarus_channel` WRITE;
/*!40000 ALTER TABLE `yarus_channel` DISABLE KEYS */;
INSERT INTO `yarus_channel` VALUES ('na2bnv5hpw3etsvrtd4t5xcvz8huni5n','Ubuntu Bionic','channel for all ubuntu bionic repositories',1,NULL,1531989601),('tn0x49nxser3f9r6ac5zog9ydd8lsksq','Debian Stretch','Debian Strach 9 channel',1,1532596126,0);
/*!40000 ALTER TABLE `yarus_channel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_client`
--

DROP TABLE IF EXISTS `yarus_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_client` (
  `ID` varchar(255) NOT NULL,
  `IP` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `version` varchar(20) NOT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `last_check` int(11) DEFAULT NULL,
  `manager_id` int(11) NOT NULL,
  `distribution` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_client`
--

LOCK TABLES `yarus_client` WRITE;
/*!40000 ALTER TABLE `yarus_client` DISABLE KEYS */;
INSERT INTO `yarus_client` VALUES ('0ff9guudivreqh8av48zd0eacn0eb7xz','10.95.84.131','PC Alexandre','PC Portable Alexandre','APT','bionic',1532594809,0,1,'ubuntu'),('l5fxoowkjf3es5ulkyvwoqq9hi8065bf','155.6.102.161','sr102161','Server YARUS','YUM','7.5.1804',1532594884,0,1,'centos'),('py1fc5nte63t8o0jyuktvc6vgna526nv','155.6.102.162','sr102162','server test centos','YUM','7.5.1804',1532594908,0,1,'centos'),('0rcr7ynhpysykjpkmf15letr4tf1w7ec','155.6.102.163','sr102163','server test ubuntu','APT','bionic',1532595060,0,1,'ubuntu');
/*!40000 ALTER TABLE `yarus_client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_group`
--

DROP TABLE IF EXISTS `yarus_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_group` (
  `ID` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `manager_id` int(11) NOT NULL,
  `last_check` int(11) NOT NULL,
  `creation_date` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_group`
--

LOCK TABLES `yarus_group` WRITE;
/*!40000 ALTER TABLE `yarus_group` DISABLE KEYS */;
INSERT INTO `yarus_group` VALUES ('87s4zkrc8zhvro1l9o5mwubh911989dp','CentOS7 Group','all clients with CentOS7',1,0,0);
/*!40000 ALTER TABLE `yarus_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_grouped`
--

DROP TABLE IF EXISTS `yarus_grouped`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_grouped` (
  `group_id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_grouped`
--

LOCK TABLES `yarus_grouped` WRITE;
/*!40000 ALTER TABLE `yarus_grouped` DISABLE KEYS */;
/*!40000 ALTER TABLE `yarus_grouped` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_link`
--

DROP TABLE IF EXISTS `yarus_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_link` (
  `channel_id` varchar(255) NOT NULL,
  `repo_id` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_link`
--

LOCK TABLES `yarus_link` WRITE;
/*!40000 ALTER TABLE `yarus_link` DISABLE KEYS */;
INSERT INTO `yarus_link` VALUES ('na2bnv5hpw3etsvrtd4t5xcvz8huni5n','k9vjw1negkktert4szqr1414e9qj23py'),('na2bnv5hpw3etsvrtd4t5xcvz8huni5n','pxg2y183ugfxxx6burckrj5800eogmco'),('na2bnv5hpw3etsvrtd4t5xcvz8huni5n','tje0ls7onstzm6efat6xrqxuyuogekxn'),('tn0x49nxser3f9r6ac5zog9ydd8lsksq','hssq4gsi295p566uccifa45533iiqb4c'),('tn0x49nxser3f9r6ac5zog9ydd8lsksq','4vsox0lp9xk1ldz41k0qkwykt27cgg5q'),('tn0x49nxser3f9r6ac5zog9ydd8lsksq','zme08s8vcrqntpvnkosjmvxgkl4z93r5');
/*!40000 ALTER TABLE `yarus_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_permissions`
--

DROP TABLE IF EXISTS `yarus_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_permissions` (
  `role_id` int(11) NOT NULL,
  `manage_users` tinyint(1) NOT NULL,
  `manage_repos` tinyint(1) NOT NULL,
  `manage_clients` tinyint(1) NOT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_permissions`
--

LOCK TABLES `yarus_permissions` WRITE;
/*!40000 ALTER TABLE `yarus_permissions` DISABLE KEYS */;
INSERT INTO `yarus_permissions` VALUES (1,1,1,1),(2,0,1,1),(3,0,0,1),(4,0,0,0);
/*!40000 ALTER TABLE `yarus_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_repository`
--

DROP TABLE IF EXISTS `yarus_repository`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_repository` (
  `ID` varchar(255) NOT NULL,
  `URL` varchar(255) DEFAULT NULL,
  `repository` varchar(255) DEFAULT NULL,
  `release` varchar(255) NOT NULL,
  `components` varchar(255) DEFAULT NULL,
  `architectures` varchar(50) DEFAULT NULL,
  `type` varchar(3) DEFAULT NULL,
  `last_sync` int(11) DEFAULT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `manager_id` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `repo_id` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_repository`
--

LOCK TABLES `yarus_repository` WRITE;
/*!40000 ALTER TABLE `yarus_repository` DISABLE KEYS */;
INSERT INTO `yarus_repository` VALUES ('4vsox0lp9xk1ldz41k0qkwykt27cgg5q','http://ftp.fr.debian.org/debian/','debian','stretch-updates','contrib,main,non-free','amd64,i386','APT',0,1532595734,'Debian Stretch Update','Debian Stretch 9 base repository ',1),('8wfcov8hplov98t2lxkcgh2se7ik7oml','http://distrib-coffee.ipsl.jussieu.fr/pub/linux/centos/','centos','7.5.1804','os,updates,extras','x86_64','YUM',1532427177,0,'CentOS 75','Repository for CentOS 75',1),('hssq4gsi295p566uccifa45533iiqb4c','http://ftp.fr.debian.org/debian/','debian','stretch','contrib,main,non-free','amd64,i386','APT',0,1532595525,'Debian Stretch Base','Debian Stretch 9 base repository ',1),('k9vjw1negkktert4szqr1414e9qj23py','http://mirror.in2p3.fr/pub/linux/ubuntu/','ubuntu','bionic','main,restricted,universe,multiverse','amd64,i386','APT',1531989303,0,'Ubuntu Bionic Base','Ubuntu Bionic repository',1),('pxg2y183ugfxxx6burckrj5800eogmco','http://mirror.in2p3.fr/pub/linux/ubuntu/','ubuntu','bionic-updates','main,restricted,universe,multiverse','amd64,i386','APT',1532423662,0,'Ubuntu Bionic Update','Ubuntu Bionid update repository',1),('tje0ls7onstzm6efat6xrqxuyuogekxn','http://mirror.in2p3.fr/pub/linux/ubuntu/','ubuntu','bionic-security','main,restricted,universe,multiverse','amd64,i386','APT',1531989601,0,'Ubuntu Bionic Security','Ubuntu Bionic Security repository',1),('zme08s8vcrqntpvnkosjmvxgkl4z93r5','http://security.debian.org/debian-security/','debian','stretch/updates','contrib,main,non-free','amd64,i386','APT',0,1532595920,'Debian Stretch Security','Debian Stretch 9 security repository ',1);
/*!40000 ALTER TABLE `yarus_repository` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_task`
--

DROP TABLE IF EXISTS `yarus_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_task` (
  `ID` varchar(32) NOT NULL,
  `status` varchar(255) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `action` varchar(255) NOT NULL,
  `manager_id` int(11) NOT NULL,
  `creation_date` int(11) NOT NULL,
  `start_time` int(11) NOT NULL,
  `end_time` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `task_id` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_task`
--

LOCK TABLES `yarus_task` WRITE;
/*!40000 ALTER TABLE `yarus_task` DISABLE KEYS */;
INSERT INTO `yarus_task` VALUES ('0jyhrewvpm9zj8e82ql88g7dqr47s2zc','completed','l5fxoowkjf3es5ulkyvwoqq9hi8065bf','config_client',1,1532610138,1532610163,1532610171),('1799etoino2d1gjwqk3cqe4qkf4qoucs','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532614403,1532614418,1532614420),('28pvf2kz1e0y61fh6e1hsxhsp94r13xp','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','config_client',1,1532610137,1532610155,1532610163),('2eyulnz1jhfulkf4pknzy5w4usghnt9d','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532614530,1532614549,1532614555),('2neji6glpe0wjell4gf5d2v48tvgz85b','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','all_update_client',1,1532615820,1532615827,1532615827),('2qh6pvlf6czs0nih5lchz4fy3sn304oe','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','approved_update_client',1,1532614531,1532614555,1532614555),('2w6qjbsvp1p1r30soudbszk5kgv85p3u','completed','l5fxoowkjf3es5ulkyvwoqq9hi8065bf','upgradable_client',1,1532611645,1532611653,1532611659),('318zlywy11x96572690cwtk3ror1xgyt','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532614452,1532614468,1532614470),('3e6urmnwwv138tn6th5iym8zda9vbt3y','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532615759,1532615763,1532615771),('3g8dldd24jqf9gbecym761b9c0o1ri6e','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613672,1532613678,1532613683),('3on0jgnju0eoooqkg55qjs1gemhnlavt','failed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','all_update_client',1,1532614982,1532614984,1532615301),('3ovxbct3l97dvj1bd2u24e25iu3qkzwb','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613330,1532613333,1532613338),('492fhszxs47kewsnntrq351hj3x076dz','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','check_client',1,1532610487,1532610503,1532610508),('4e6od2wqha8xz0ss6zph8aqw6j9alnzw','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','upgradable_client',1,1532615753,1532615753,1532615763),('52fof0munxznhey1orbxbg4ym8pfxj5o','failed','py1fc5nte63t8o0jyuktvc6vgna526nv','upgradable_client',1,1532615812,1532615816,1532615827),('53cpemsxts0vbo6a4qgkrkwylzsyuci6','completed','xfzv6v8j6qmducum2696v8qy7trvssg6','config_client',1,1532610141,1532610183,1532610189),('5l8x3nzw0e767eqrkbl9zsp0j0hb9efk','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','config_client',1,1532610140,1532610171,1532610183),('5pm18m8b0nls89umzs579ztbfwejfvye','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613357,1532613360,1532613364),('5wtjacsg6uyl1zd7m7fkvdbmbv7wf9h3','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532611520,1532611525,1532611533),('6fx2gtkkbh37hwxp9yn5qzbm1reorgzj','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613671,1532613674,1532613678),('6h36pe36n4ihs23zribq86a6jkiyxzce','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532610507,1532610538,1532610546),('6oyeto4d2zdcw3hlmp87tpb7gpcs9866','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532611813,1532611817,1532611821),('7lhnnzuqx23hwy4a15rxo9hx8iy022ah','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532611097,1532611112,1532611125),('815yty520cbjkqop4869l1mch9p3uypa','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','upgradable_client',1,1532611606,1532611617,1532611626),('8h282oinlap7n6cjnqlhmszxn1oerzp3','completed','l5fxoowkjf3es5ulkyvwoqq9hi8065bf','upgradable_client',1,1532610509,1532610546,1532610558),('8tcpbq4qleldb5k64e43p6x31e40ok8y','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532614451,1532614460,1532614468),('93pbtkmgkx1m7x8azwqw7jjjqj94u0n5','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532610862,1532610874,1532610879),('9yhpnyfaqhddqn7u4vvbeukxj3zb82iw','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','approved_update_client',1,1532613125,1532613153,1532613153),('aizq1xc2ukgcp7bld0jqwltl60cq465h','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613247,1532613249,1532613253),('b48j9k91y99f40yduegugizlwhogbxby','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613395,1532613397,1532613401),('dn81gxgutmxncslnv6lt0lh040tpos5w','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613150,1532613158,1532613162),('eunnk5gnfec7i1ae4rfn3loe645whcuk','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','approved_update_client',1,1532613148,1532613158,1532613158),('ey6a2oo4qe3t1y2aq4ql7op7wthjhisg','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','config_client',1,1532610495,1532610522,1532610529),('f1vy2gq2ey6gbaeuxc7toir4wwjz2l9y','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','all_update_client',1,1532615729,1532615733,1532615733),('f6jrqb9x6suoreaz96sem5v2gavjmdg1','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613126,1532613153,1532613158),('fj2koftp4hu8nyhi5xhvtrfcilq48zdw','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532614388,1532614391,1532614397),('fqvov45qqwbemlss1kusjgqqe7scx0wd','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','upgradable_client',1,1532615899,1532615908,1532615914),('fu8mgk3rsgjmq9262cy2wbscecx8l5o3','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','config_client',1,1532610489,1532610508,1532610513),('g6czfdmy9arv15w2fj11agl0kg8wgh7l','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613710,1532613712,1532613717),('gbcm8wui25wtxk7twwtb3mx1jtvge38t','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','upgradable_client',1,1532611608,1532611626,1532611633),('h4gxkd8b5l60xl41vfntxe95lcn522mr','failed','py1fc5nte63t8o0jyuktvc6vgna526nv','all_update_client',1,1532615920,1532615934,1532616267),('hc0t9wz3h6yhzmdsb964128fg6mre3nc','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613217,1532613220,1532613225),('ijrt26iulq85qd53i1pocdp39fh7uxh0','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','all_update_client',1,1532615813,1532615827,1532615827),('is856pmz2592b32d7pww71bwxj3obec6','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','upgradable_client',1,1532610510,1532610558,1532610569),('iu9h3xon4fjpyqngw1enqy0pj8bxo5pg','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','check_client',1,1532610486,1532610499,1532610503),('ixe1t02piatczog0gzjwb82z8yjg5wqa','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','upgradable_client',1,1532610671,1532610673,1532610680),('jghcwhwmpxex3y7ynlr2vuvxfz2yltan','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532611900,1532611908,1532612175),('jmltrvq3hfjy968y32epimmqpareki1s','completed','py1fc5nte63t8o0jyuktvc6vgna526nv','upgradable_client',1,1532611647,1532611659,1532611671),('k4svx4m0j40b219ny4zzyhk06g3dkquf','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','check_client',1,1532610483,1532610489,1532610494),('mgx2fmmvsbrg6tivc5sv6faubw5fx9o0','failed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','upgradable_client',1,1532611094,1532611102,1532611112),('ofblmq4qzm784lnwwftk35yemf46epyr','completed','l5fxoowkjf3es5ulkyvwoqq9hi8065bf','check_client',1,1532610485,1532610494,1532610499),('p1utteyn5bczrkoxu9nn91t62lile20j','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613638,1532613642,1532613647),('q7d4jn2xyz7np9y8jm8y9ti62dkvm47a','failed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','all_update_client',1,1532615415,1532615416,1532615432),('qebfvf369b72jpzeny9yu5fw2svchgxn','running','tn0x49nxser3f9r6ac5zog9ydd8lsksq','sync_channel',1,1532596150,1532596173,0),('rcluz1558ja1qb58d1t4mcoy37ukmxsp','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613640,1532613647,1532613652),('va3da0n43bztk7usiq8d123ofdplfjnv','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613546,1532613551,1532613556),('vtf8bgul9u512jcywmxi9g0xnssfg7m1','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','upgradable_client',1,1532610864,1532610879,1532610885),('vy1xcg9dik3xo62xf59dqaraa1jxdrls','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','upgradable_client',1,1532611522,1532611533,1532611542),('wh5hsyeemjvw2l7b8gubqzq4v4q7mb8b','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532613274,1532613278,1532613281),('x6c666nnws248upq915lem0tmskjgrsb','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','config_client',1,1532610501,1532610529,1532610538),('ymq9xe2jwmjprhk4oznwo6uswaqo6lcf','failed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532611741,1532611751,1532611751),('za4ne7x7hewezs83cyfcxylmfkiuodj0','completed','0rcr7ynhpysykjpkmf15letr4tf1w7ec','upgradable_client',1,1532610512,1532610569,1532610573),('zbzjl1bdmdawvea8ho5e0jw6ullf6fha','completed','l5fxoowkjf3es5ulkyvwoqq9hi8065bf','config_client',1,1532610492,1532610514,1532610522),('zuaztwtibcqufmz1tq6o94bt2d90nxoz','completed','0ff9guudivreqh8av48zd0eacn0eb7xz','all_update_client',1,1532614532,1532614555,1532614555);
/*!40000 ALTER TABLE `yarus_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_upgradable`
--

DROP TABLE IF EXISTS `yarus_upgradable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yarus_upgradable` (
  `name` varchar(255) NOT NULL,
  `release` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `client_id` varchar(255) NOT NULL,
  `approved` int(11) NOT NULL,
  `ID` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yarus_upgradable`
--

LOCK TABLES `yarus_upgradable` WRITE;
/*!40000 ALTER TABLE `yarus_upgradable` DISABLE KEYS */;
INSERT INTO `yarus_upgradable` VALUES ('NetworkManager','1:1.10.2-16.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'e499mp6of4ir9pb0l6awycm8dvo1ivx7'),('NetworkManager-libnm','1:1.10.2-16.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'ukvzostvyvf2ocerpe516b8gv3w7ll28'),('NetworkManager-ppp','1:1.10.2-16.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'x4grus0io9wjahkhprsqqy21j5iqgrjm'),('NetworkManager-team','1:1.10.2-16.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'etdjs0x9ylqnkcevjhg0eiyqs7qm6mnp'),('NetworkManager-tui','1:1.10.2-16.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'jv5e8exn3cqtfxzuh6r85ojof96un783'),('NetworkManager-wifi','1:1.10.2-16.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'eg6ksbmd7pqq7ch21zgcm2688ey2940s'),('binutils','2.27-28.base.el7_5.1','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'n1usg6fp3at29i7fau5fs29x7q9bv7ob'),('gnupg2','2.0.22-5.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'l27psjv9drk5ekczij8u8216g0ajhq05'),('gsettings-desktop-schemas','3.24.1-2.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'qbdn6kn4zcpf683zyfvf6f2qmvok6uzc'),('httpd','2.4.6-80.el7.centos.1','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'yl9mfxhwms5l0ahprbfx9fv70p4b5i4d'),('httpd-tools','2.4.6-80.el7.centos.1','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'avfuc3hje64spug9g3hcto3pb8lom0e3'),('kernel','3.10.0-862.9.1.el7','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'a6isra8b2mefb5u094cicam5x7lky91d'),('kernel-tools','3.10.0-862.9.1.el7','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'fkxmrgzoj2x9ovhg0sxi5fa8jashb3ut'),('kernel-tools-libs','3.10.0-862.9.1.el7','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'wpjuwdxvcbu7egbo3ulq4kctod44boj8'),('python','2.7.5-69.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'z2igu4p9kr98zsf0e3vsfzrfejbnpgu2'),('python-libs','2.7.5-69.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'1aajwm6bldu6q8puuykqek8ax1wxw2eu'),('python-perf','3.10.0-862.9.1.el7','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'qnl55x7dw8qtb8gd1ythc4zatnylml1e'),('selinux-policy','3.13.1-192.el7_5.4','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'hull4rvm09n08ppfvqojgd17bmaguaen'),('selinux-policy-targeted','3.13.1-192.el7_5.4','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'6s4b532ejixouzffg0czecfels7lbsei'),('sudo','1.8.19p2-14.el7_5','updates','l5fxoowkjf3es5ulkyvwoqq9hi8065bf',0,'onjqzxie4h4n1yyibjh3pimgbnorf6m6');
/*!40000 ALTER TABLE `yarus_upgradable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yarus_user`
--

DROP TABLE IF EXISTS `yarus_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
INSERT INTO `yarus_user` VALUES ('1','admin','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',1,'alexandre.borgo@ratp.fr',NULL,'brwqw8thinj16kce55p5o38vchtftfxs',1532624304);
/*!40000 ALTER TABLE `yarus_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-07-26 16:54:57
