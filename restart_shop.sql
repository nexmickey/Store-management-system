USE shops;

DELETE FROM `order_item`;
DELETE FROM `product_category`;
DELETE FROM `order`;
DELETE FROM `category`;
DELETE FROM `product`;

ALTER TABLE `product_category` AUTO_INCREMENT = 1;
ALTER TABLE `order` AUTO_INCREMENT = 1;
ALTER TABLE `category` AUTO_INCREMENT = 1;
ALTER TABLE `product` AUTO_INCREMENT = 1;
