-- MySQL Script generated by MySQL Workbench
-- Wed Nov 28 01:04:31 2018
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema FLOW_TRUCK
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `FLOW_TRUCK` ;

-- -----------------------------------------------------
-- Schema FLOW_TRUCK
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `FLOW_TRUCK` DEFAULT CHARACTER SET utf8 COLLATE utf8_spanish_ci ;
USE `FLOW_TRUCK` ;

-- -----------------------------------------------------
-- Table `FLOW_TRUCK`.`TRUCK`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FLOW_TRUCK`.`TRUCK` ;

CREATE TABLE IF NOT EXISTS `FLOW_TRUCK`.`TRUCK` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `NAME` VARCHAR(45) NULL,
  `MAXIMUM_POSSIBLE_VELOCITY` INT NULL,
  `POSITIONED_AT` VARCHAR(45) NULL,
  `STORAGE_CAPACITY` INT NULL,
  `CURRENT_LOAD` DECIMAL(5,2) NULL,
  `DISCHARGE_RATE` INT NULL,
  `LOADED_SPEED` INT NULL,
  `SPOTTING_TIME` INT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FLOW_TRUCK`.`SHORTEST_PATH`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FLOW_TRUCK`.`SHORTEST_PATH` ;

CREATE TABLE IF NOT EXISTS `FLOW_TRUCK`.`SHORTEST_PATH` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `NAME` VARCHAR(45) NULL,
  `STARTING_AT` VARCHAR(45) NULL,
  `DIRECTED_TO` VARCHAR(45) NULL,
  `EDGE_LENGTH` INT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FLOW_TRUCK`.`SHOVEL`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FLOW_TRUCK`.`SHOVEL` ;

CREATE TABLE IF NOT EXISTS `FLOW_TRUCK`.`SHOVEL` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `NAME` VARCHAR(45) NULL,
  `POSITIONED_AT` VARCHAR(45) NULL,
  `TRANSPORTATION_CAPACITY` INT NULL,
  `LOAD_RATE` INT NULL,
  `DIG_RATE` INT NULL,
  `CURRENT_LOAD` INT NULL,
  `IDEAL_AMOUNT` INT NULL,
  `DESTINATION` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FLOW_TRUCK`.`UNLOAD`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FLOW_TRUCK`.`UNLOAD` ;

CREATE TABLE IF NOT EXISTS `FLOW_TRUCK`.`UNLOAD` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `TYPE` VARCHAR(45) NULL,
  `NAME` VARCHAR(45) NULL,
  `POSITIONED_AT` VARCHAR(45) NULL,
  `CURRENT_LOAD` VARCHAR(45) NULL,
  `MAXIMUM_DISCHARGE` INT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FLOW_TRUCK`.`ASSIGNMENT`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FLOW_TRUCK`.`ASSIGNMENT` ;

CREATE TABLE IF NOT EXISTS `FLOW_TRUCK`.`ASSIGNMENT` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `TRUCK_ID` INT NOT NULL,
  `SHOVEL_ID` INT NOT NULL,
  PRIMARY KEY (`ID`, `TRUCK_ID`, `SHOVEL_ID`),
  INDEX `fk_ASSIGNMENT_TRUCK1_idx` (`TRUCK_ID` ASC),
  INDEX `fk_ASSIGNMENT_SHOVEL1_idx` (`SHOVEL_ID` ASC),
  CONSTRAINT `fk_ASSIGNMENT_TRUCK1`
    FOREIGN KEY (`TRUCK_ID`)
    REFERENCES `FLOW_TRUCK`.`TRUCK` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ASSIGNMENT_SHOVEL1`
    FOREIGN KEY (`SHOVEL_ID`)
    REFERENCES `FLOW_TRUCK`.`SHOVEL` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FLOW_TRUCK`.`TRUCK_FLOW`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FLOW_TRUCK`.`TRUCK_FLOW` ;

CREATE TABLE IF NOT EXISTS `FLOW_TRUCK`.`TRUCK_FLOW` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `TRUCK_ID` INT NULL,
  `STATION_ID` INT NULL,
  `STATION_TYPE` VARCHAR(45) NULL,
  `BUFFER` VARCHAR(45) NULL,
  `FINISHED` VARCHAR(45) NULL,
  `STATUS` VARCHAR(45) NULL,
  `START_TIME` VARCHAR(45) NULL,
  `END_TIME` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
