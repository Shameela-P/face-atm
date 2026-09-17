-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 06, 2026 at 10:33 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `atm_face_multi`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `amount` int(11) NOT NULL,
  `email` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`username`, `password`, `amount`, `email`) VALUES
('admin', 'admin', 50000, 'bgeduscanner@gmail.com');

-- --------------------------------------------------------

--
-- Table structure for table `event`
--

CREATE TABLE `event` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `accno` varchar(20) NOT NULL,
  `amount` int(11) NOT NULL,
  `rdate` varchar(50) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `event`
--

INSERT INTO `event` (`id`, `name`, `accno`, `amount`, `rdate`, `user_id`) VALUES
(1, 'Deposit', '2410102201', 10000, '05-01-2026 16-02-54', 1),
(2, 'Deposit', '4220110211', 10000, '05-01-2026 16-07-41', 2),
(3, 'Deposit', '5154844545', 10000, '06-01-2026 12-25-14', 2),
(4, 'Withdraw', '5154844545', 500, '06-01-2026 12-28-51', 2),
(5, 'Withdraw', '5154844545', 500, '06-01-2026 15-54-11', 2);

-- --------------------------------------------------------

--
-- Table structure for table `numbers`
--

CREATE TABLE `numbers` (
  `id` int(11) NOT NULL,
  `number` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `numbers`
--

INSERT INTO `numbers` (`id`, `number`) VALUES
(1, 0),
(2, 1),
(3, 2),
(4, 3),
(5, 4),
(6, 5),
(7, 6),
(8, 7),
(9, 8),
(10, 9);

-- --------------------------------------------------------

--
-- Table structure for table `register`
--

CREATE TABLE `register` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `address` varchar(200) NOT NULL,
  `mobile` bigint(20) NOT NULL,
  `email` varchar(50) NOT NULL,
  `accno` varchar(20) NOT NULL,
  `card` varchar(20) NOT NULL,
  `bank` varchar(20) NOT NULL,
  `branch` varchar(20) NOT NULL,
  `deposit` int(11) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `rdate` varchar(20) NOT NULL,
  `aadhar1` varchar(20) NOT NULL,
  `aadhar2` varchar(20) NOT NULL,
  `aadhar3` varchar(20) NOT NULL,
  `face_st` int(11) NOT NULL,
  `fimg` varchar(30) NOT NULL,
  `otp` varchar(20) NOT NULL,
  `allow_st` int(11) NOT NULL,
  `pinno` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `register`
--

INSERT INTO `register` (`id`, `name`, `address`, `mobile`, `email`, `accno`, `card`, `bank`, `branch`, `deposit`, `username`, `password`, `rdate`, `aadhar1`, `aadhar2`, `aadhar3`, `face_st`, `fimg`, `otp`, `allow_st`, `pinno`) VALUES
(1, 'Vijay', '34,FF Nagar', 9894442716, 'vijay@gmail.com', '', '486000012167', 'SBI', '', 0, '', '8944', '30-12-2025', '235645127845', '', '', 0, 'User.1.80.jpg', '', 0, ''),
(2, 'Dheena', '32,Salem', 7358479178, 'ragunath@gmail.com', '', '7355260000026714', '', '', 0, '', '', '05-01-2026', '279848617318', '', '', 0, 'User.2.60.jpg', '', 0, '');

-- --------------------------------------------------------

--
-- Table structure for table `user_account`
--

CREATE TABLE `user_account` (
  `id` int(11) NOT NULL,
  `rid` int(11) NOT NULL,
  `bank` varchar(200) NOT NULL,
  `account` varchar(200) NOT NULL,
  `ifsc_code` varchar(200) NOT NULL,
  `branch` varchar(200) NOT NULL,
  `deposit` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user_account`
--

INSERT INTO `user_account` (`id`, `rid`, `bank`, `account`, `ifsc_code`, `branch`, `deposit`) VALUES
(1, 1, 'SBI', '2410102201', 'SB001152', 'Chennai', '10000'),
(2, 1, 'IOB', '4220110211', 'IO55012421', 'Rasipuram', '10000'),
(3, 2, 'SBI', '5154844545', 'SB656656', 'Kattur', '9000');

-- --------------------------------------------------------

--
-- Table structure for table `vt_face`
--

CREATE TABLE `vt_face` (
  `id` int(11) NOT NULL,
  `vid` int(11) NOT NULL,
  `vface` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `vt_face`
--

INSERT INTO `vt_face` (`id`, `vid`, `vface`) VALUES
(39, 1, 'User.1.2.jpg'),
(40, 1, 'User.1.3.jpg'),
(41, 1, 'User.1.4.jpg'),
(42, 1, 'User.1.5.jpg'),
(43, 1, 'User.1.6.jpg'),
(44, 1, 'User.1.7.jpg'),
(45, 1, 'User.1.8.jpg'),
(46, 1, 'User.1.9.jpg'),
(47, 1, 'User.1.10.jpg'),
(48, 1, 'User.1.11.jpg'),
(49, 1, 'User.1.12.jpg'),
(50, 1, 'User.1.13.jpg'),
(51, 1, 'User.1.14.jpg'),
(52, 1, 'User.1.15.jpg'),
(53, 1, 'User.1.16.jpg'),
(54, 1, 'User.1.17.jpg'),
(55, 1, 'User.1.18.jpg'),
(56, 1, 'User.1.19.jpg'),
(57, 1, 'User.1.20.jpg'),
(58, 1, 'User.1.21.jpg'),
(59, 1, 'User.1.22.jpg'),
(60, 1, 'User.1.23.jpg'),
(61, 1, 'User.1.24.jpg'),
(62, 1, 'User.1.25.jpg'),
(63, 1, 'User.1.26.jpg'),
(64, 1, 'User.1.27.jpg'),
(65, 1, 'User.1.28.jpg'),
(66, 1, 'User.1.29.jpg'),
(67, 1, 'User.1.30.jpg'),
(68, 1, 'User.1.31.jpg'),
(69, 1, 'User.1.32.jpg'),
(70, 1, 'User.1.33.jpg'),
(71, 1, 'User.1.34.jpg'),
(72, 1, 'User.1.35.jpg'),
(73, 1, 'User.1.36.jpg'),
(74, 1, 'User.1.37.jpg'),
(75, 1, 'User.1.38.jpg'),
(76, 1, 'User.1.39.jpg'),
(77, 1, 'User.1.40.jpg'),
(78, 1, 'User.1.41.jpg'),
(79, 1, 'User.1.42.jpg'),
(80, 1, 'User.1.43.jpg'),
(81, 1, 'User.1.44.jpg'),
(82, 1, 'User.1.45.jpg'),
(83, 1, 'User.1.46.jpg'),
(84, 1, 'User.1.47.jpg'),
(85, 1, 'User.1.48.jpg'),
(86, 1, 'User.1.49.jpg'),
(87, 1, 'User.1.50.jpg'),
(88, 1, 'User.1.51.jpg'),
(89, 1, 'User.1.52.jpg'),
(90, 1, 'User.1.53.jpg'),
(91, 1, 'User.1.54.jpg'),
(92, 1, 'User.1.55.jpg'),
(93, 1, 'User.1.56.jpg'),
(94, 1, 'User.1.57.jpg'),
(95, 1, 'User.1.58.jpg'),
(96, 1, 'User.1.59.jpg'),
(97, 1, 'User.1.60.jpg'),
(98, 1, 'User.1.61.jpg'),
(99, 1, 'User.1.62.jpg'),
(100, 1, 'User.1.63.jpg'),
(101, 1, 'User.1.64.jpg'),
(102, 1, 'User.1.65.jpg'),
(103, 1, 'User.1.66.jpg'),
(104, 1, 'User.1.67.jpg'),
(105, 1, 'User.1.68.jpg'),
(106, 1, 'User.1.69.jpg'),
(107, 1, 'User.1.70.jpg'),
(108, 1, 'User.1.71.jpg'),
(109, 1, 'User.1.72.jpg'),
(110, 1, 'User.1.73.jpg'),
(111, 1, 'User.1.74.jpg'),
(112, 1, 'User.1.75.jpg'),
(113, 1, 'User.1.76.jpg'),
(114, 1, 'User.1.77.jpg'),
(115, 1, 'User.1.78.jpg'),
(116, 1, 'User.1.79.jpg'),
(117, 1, 'User.1.80.jpg'),
(118, 2, 'User.2.2.jpg'),
(119, 2, 'User.2.3.jpg'),
(120, 2, 'User.2.4.jpg'),
(121, 2, 'User.2.5.jpg'),
(122, 2, 'User.2.6.jpg'),
(123, 2, 'User.2.7.jpg'),
(124, 2, 'User.2.8.jpg'),
(125, 2, 'User.2.9.jpg'),
(126, 2, 'User.2.10.jpg'),
(127, 2, 'User.2.11.jpg'),
(128, 2, 'User.2.12.jpg'),
(129, 2, 'User.2.13.jpg'),
(130, 2, 'User.2.14.jpg'),
(131, 2, 'User.2.15.jpg'),
(132, 2, 'User.2.16.jpg'),
(133, 2, 'User.2.17.jpg'),
(134, 2, 'User.2.18.jpg'),
(135, 2, 'User.2.19.jpg'),
(136, 2, 'User.2.20.jpg'),
(137, 2, 'User.2.21.jpg'),
(138, 2, 'User.2.22.jpg'),
(139, 2, 'User.2.23.jpg'),
(140, 2, 'User.2.24.jpg'),
(141, 2, 'User.2.25.jpg'),
(142, 2, 'User.2.26.jpg'),
(143, 2, 'User.2.27.jpg'),
(144, 2, 'User.2.28.jpg'),
(145, 2, 'User.2.29.jpg'),
(146, 2, 'User.2.30.jpg'),
(147, 2, 'User.2.31.jpg'),
(148, 2, 'User.2.32.jpg'),
(149, 2, 'User.2.33.jpg'),
(150, 2, 'User.2.34.jpg'),
(151, 2, 'User.2.35.jpg'),
(152, 2, 'User.2.36.jpg'),
(153, 2, 'User.2.37.jpg'),
(154, 2, 'User.2.38.jpg'),
(155, 2, 'User.2.39.jpg'),
(156, 2, 'User.2.40.jpg'),
(157, 2, 'User.2.41.jpg'),
(158, 2, 'User.2.42.jpg'),
(159, 2, 'User.2.43.jpg'),
(160, 2, 'User.2.44.jpg'),
(161, 2, 'User.2.45.jpg'),
(162, 2, 'User.2.46.jpg'),
(163, 2, 'User.2.47.jpg'),
(164, 2, 'User.2.48.jpg'),
(165, 2, 'User.2.49.jpg'),
(166, 2, 'User.2.50.jpg'),
(167, 2, 'User.2.51.jpg'),
(168, 2, 'User.2.52.jpg'),
(169, 2, 'User.2.53.jpg'),
(170, 2, 'User.2.54.jpg'),
(171, 2, 'User.2.55.jpg'),
(172, 2, 'User.2.56.jpg'),
(173, 2, 'User.2.57.jpg'),
(174, 2, 'User.2.58.jpg'),
(175, 2, 'User.2.59.jpg'),
(176, 2, 'User.2.60.jpg');
