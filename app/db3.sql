-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema screech
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema screech
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `screech` DEFAULT CHARACTER SET utf8 ;
USE `screech` ;

-- -----------------------------------------------------
-- Table `screech`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `screech`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 9
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `screech`.`files`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `screech`.`files` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `filename` VARCHAR(200) NOT NULL,
  `owner` INT(11) NOT NULL,
  `date` DATE NOT NULL,
  `dbtable` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `table_UNIQUE` (`dbtable` ASC),
  INDEX `owner_idx` (`owner` ASC),
  CONSTRAINT `owner`
    FOREIGN KEY (`owner`)
    REFERENCES `screech`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 37
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `screech`.`tables`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `screech`.`tables` (
  `uid` INT(11) NOT NULL,
  `fid` INT(11) NOT NULL,
  INDEX `table_idx` (`fid` ASC),
  INDEX `users_idx` (`uid` ASC),
  CONSTRAINT `table`
    FOREIGN KEY (`fid`)
    REFERENCES `screech`.`files` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `users`
    FOREIGN KEY (`uid`)
    REFERENCES `screech`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `screech`.`tree_data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `screech`.`tree_data` (
  `n_cols` INT(11) NOT NULL,
  `n_rows` INT(11) NOT NULL,
  `n_cont` INT(11) NOT NULL,
  `n_disc` INT(11) NOT NULL,
  `n_ts` INT(11) NOT NULL,
  `target` VARCHAR(10) NOT NULL)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
