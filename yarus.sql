-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 20, 2018 at 01:36 PM
-- Server version: 5.7.22-0ubuntu18.04.1
-- PHP Version: 7.2.7-0ubuntu0.18.04.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `yarus`
--

-- --------------------------------------------------------

--
-- Table structure for table `yarus_bind`
--

CREATE TABLE `yarus_bind` (
  `client_id` varchar(64) NOT NULL,
  `repo_id` varchar(64) NOT NULL,
  `channel_id` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_bind`
--

INSERT INTO `yarus_bind` (`client_id`, `repo_id`, `channel_id`) VALUES
('dxx2w2kvz60ybrbr2xoacrnm6s6fr77e', '0', 'na2bnv5hpw3etsvrtd4t5xcvz8huni5n'),
('dxx2w2kvz60ybrbr2xoacrnm6s6fr77e', 'k9vjw1negkktert4szqr1414e9qj23py', '0'),
('dxx2w2kvz60ybrbr2xoacrnm6s6fr77e', 'pxg2y183ugfxxx6burckrj5800eogmco', '0'),
('dxx2w2kvz60ybrbr2xoacrnm6s6fr77e', 'tje0ls7onstzm6efat6xrqxuyuogekxn', '0'),
('dxx2w2kvz60ybrbr2xoacrnm6s6fr77e', '8wfcov8hplov98t2lxkcgh2se7ik7oml', '0'),
('l9akbfkf0plmtg5vikv9b4ojmju1t653', '8wfcov8hplov98t2lxkcgh2se7ik7oml', '0'),
('kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', 'k9vjw1negkktert4szqr1414e9qj23py', '0'),
('kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', 'pxg2y183ugfxxx6burckrj5800eogmco', '0'),
('kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', 'tje0ls7onstzm6efat6xrqxuyuogekxn', '0');

-- --------------------------------------------------------

--
-- Table structure for table `yarus_channel`
--

CREATE TABLE `yarus_channel` (
  `ID` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `manager_id` int(11) NOT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `last_sync` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_channel`
--

INSERT INTO `yarus_channel` (`ID`, `name`, `description`, `manager_id`, `creation_date`, `last_sync`) VALUES
('na2bnv5hpw3etsvrtd4t5xcvz8huni5n', 'Ubuntu Bionic', 'channel for all ubuntu bionic repositories', 1, NULL, 1531989601);

-- --------------------------------------------------------

--
-- Table structure for table `yarus_client`
--

CREATE TABLE `yarus_client` (
  `ID` varchar(255) NOT NULL,
  `IP` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `version` varchar(20) NOT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `last_check` int(11) DEFAULT NULL,
  `manager_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_client`
--

INSERT INTO `yarus_client` (`ID`, `IP`, `name`, `description`, `type`, `version`, `creation_date`, `last_check`, `manager_id`) VALUES
('l9akbfkf0plmtg5vikv9b4ojmju1t653', '155.6.102.162', 'CentOS 75 Test', 'centos 7.5 test client', 'cen', '7.5.1804', 0, 0, 1),
('kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', '10.95.84.131', 'pc alexandre', 'pc ubuntu alexandre', 'ubu', 'bionic', 0, 0, 1);

-- --------------------------------------------------------

--
-- Table structure for table `yarus_group`
--

CREATE TABLE `yarus_group` (
  `ID` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `manager_id` int(11) NOT NULL,
  `last_check` int(11) NOT NULL,
  `creation_date` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_group`
--

INSERT INTO `yarus_group` (`ID`, `name`, `description`, `manager_id`, `last_check`, `creation_date`) VALUES
('87s4zkrc8zhvro1l9o5mwubh911989dp', 'CentOS7 Group', 'all clients with CentOS7', 1, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `yarus_grouped`
--

CREATE TABLE `yarus_grouped` (
  `group_id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `yarus_link`
--

CREATE TABLE `yarus_link` (
  `channel_id` varchar(255) NOT NULL,
  `repo_id` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_link`
--

INSERT INTO `yarus_link` (`channel_id`, `repo_id`) VALUES
('na2bnv5hpw3etsvrtd4t5xcvz8huni5n', 'k9vjw1negkktert4szqr1414e9qj23py'),
('na2bnv5hpw3etsvrtd4t5xcvz8huni5n', 'pxg2y183ugfxxx6burckrj5800eogmco'),
('na2bnv5hpw3etsvrtd4t5xcvz8huni5n', 'tje0ls7onstzm6efat6xrqxuyuogekxn');

-- --------------------------------------------------------

--
-- Table structure for table `yarus_permissions`
--

CREATE TABLE `yarus_permissions` (
  `role_id` int(11) NOT NULL,
  `manage_users` tinyint(1) NOT NULL,
  `manage_repos` tinyint(1) NOT NULL,
  `manage_clients` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_permissions`
--

INSERT INTO `yarus_permissions` (`role_id`, `manage_users`, `manage_repos`, `manage_clients`) VALUES
(1, 1, 1, 1),
(2, 0, 1, 1),
(3, 0, 0, 1),
(4, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `yarus_repository`
--

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
  `manager_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_repository`
--

INSERT INTO `yarus_repository` (`ID`, `URL`, `repository`, `release`, `components`, `architectures`, `type`, `last_sync`, `creation_date`, `name`, `description`, `manager_id`) VALUES
('8wfcov8hplov98t2lxkcgh2se7ik7oml', 'http://distrib-coffee.ipsl.jussieu.fr/pub/linux/centos/', '7.5.1804', '', 'os,updates,extras', 'x86_64', 'cen', 1531991072, 0, 'CentOS 75', 'Repository for CentOS 75', 1),
('k9vjw1negkktert4szqr1414e9qj23py', 'http://mirror.in2p3.fr/pub/linux/ubuntu/', 'bionic', '', 'main,restricted,universe,multiverse', 'amd64,i386', 'ubu', 1531989303, 0, 'Ubuntu Bionic Base', 'Ubuntu Bionic repository', 1),
('pxg2y183ugfxxx6burckrj5800eogmco', 'http://mirror.in2p3.fr/pub/linux/ubuntu/', 'bionic-updates', '', 'main,restricted,universe,multiverse', 'amd64,i386', 'ubu', 1531989489, 0, 'Ubuntu Bionic Update', 'Ubuntu Bionid update repository', 1),
('tje0ls7onstzm6efat6xrqxuyuogekxn', 'http://mirror.in2p3.fr/pub/linux/ubuntu/', 'bionic-security', '', 'main,restricted,universe,multiverse', 'amd64,i386', 'ubu', 1531989601, 0, 'Ubuntu Bionic Security', 'Ubuntu Bionic Security repository', 1);

-- --------------------------------------------------------

--
-- Table structure for table `yarus_task`
--

CREATE TABLE `yarus_task` (
  `ID` varchar(32) NOT NULL,
  `status` varchar(255) NOT NULL,
  `object_id` varchar(255) NOT NULL,
  `action` varchar(255) NOT NULL,
  `manager_id` int(11) NOT NULL,
  `creation_date` int(11) NOT NULL,
  `start_time` int(11) NOT NULL,
  `end_time` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `yarus_task`
--

INSERT INTO `yarus_task` (`ID`, `status`, `object_id`, `action`, `manager_id`, `creation_date`, `start_time`, `end_time`) VALUES
('52983qqjqshachsfoxqc1sfkdfm7nc6p', 'completed', 'kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', 'check_client', 1, 1532081981, 1532082042, 1532082043),
('cavn1z51wkyhwg65ybaffdlla53d3ry0', 'completed', 'kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', 'check_client', 1, 1532081982, 1532082823, 1532082827),
('oftbfkmf79yfh2hvopxha14aekchugre', 'completed', 'kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', 'set_config_file', 1, 1532083136, 1532083142, 1532083142),
('xtq793lwh93qwrdkg9r8olx0vkydgaf4', 'completed', 'l9akbfkf0plmtg5vikv9b4ojmju1t653', 'check_client', 1, 1532082856, 1532082873, 1532082876),
('ylg18wixg44p6qerjacvpjxn503n1lmq', 'failed', 'kcruqu2ckeyrv9x00b7aym8ikz2jh6l0', 'check_client', 1, 1532081982, 1532082783, 1532082786);

-- --------------------------------------------------------

--
-- Table structure for table `yarus_user`
--

CREATE TABLE `yarus_user` (
  `ID` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role_id` int(11) NOT NULL,
  `mail` varchar(255) NOT NULL,
  `creation_date` int(11) DEFAULT NULL,
  `token` varchar(64) NOT NULL,
  `token_expire` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `yarus_user`
--

INSERT INTO `yarus_user` (`ID`, `name`, `password`, `role_id`, `mail`, `creation_date`, `token`, `token_expire`) VALUES
('1', 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 1, 'alexandre.borgo@ratp.fr', NULL, 'ls5croj2cludpmbmmuvhve8101fpcegb', 1532084815);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `yarus_channel`
--
ALTER TABLE `yarus_channel`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `channel_id` (`ID`);

--
-- Indexes for table `yarus_group`
--
ALTER TABLE `yarus_group`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `ID` (`ID`);

--
-- Indexes for table `yarus_permissions`
--
ALTER TABLE `yarus_permissions`
  ADD PRIMARY KEY (`role_id`),
  ADD UNIQUE KEY `role_id` (`role_id`);

--
-- Indexes for table `yarus_repository`
--
ALTER TABLE `yarus_repository`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `repo_id` (`ID`);

--
-- Indexes for table `yarus_task`
--
ALTER TABLE `yarus_task`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `task_id` (`ID`);

--
-- Indexes for table `yarus_user`
--
ALTER TABLE `yarus_user`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `user_id` (`ID`),
  ADD UNIQUE KEY `name` (`name`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
