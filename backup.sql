-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: glace_code
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `CONVERSION_UNIDAD`
--

DROP TABLE IF EXISTS `CONVERSION_UNIDAD`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CONVERSION_UNIDAD` (
  `id` int NOT NULL AUTO_INCREMENT,
  `factor_conversion` float DEFAULT NULL,
  `insumo_id` int DEFAULT NULL,
  `unidad_destino_id` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_CONVERSION_UNIDAD_insumo_id` (`insumo_id`),
  KEY `ix_CONVERSION_UNIDAD_is_active` (`is_active`),
  KEY `ix_CONVERSION_UNIDAD_unidad_destino_id` (`unidad_destino_id`),
  CONSTRAINT `CONVERSION_UNIDAD_ibfk_1` FOREIGN KEY (`insumo_id`) REFERENCES `INSUMO` (`id`),
  CONSTRAINT `CONVERSION_UNIDAD_ibfk_2` FOREIGN KEY (`unidad_destino_id`) REFERENCES `UNIDAD_MEDIDA` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CONVERSION_UNIDAD`
--

LOCK TABLES `CONVERSION_UNIDAD` WRITE;
/*!40000 ALTER TABLE `CONVERSION_UNIDAD` DISABLE KEYS */;
INSERT INTO `CONVERSION_UNIDAD` VALUES (1,1000,1,1,0),(2,0.001,1,1,0),(3,1000,1,5,0),(4,120,2,4,1),(5,120,3,4,1),(6,120,4,4,1),(7,120,5,4,1),(8,120,6,4,1),(9,120,7,4,1),(10,120,8,4,1),(11,120,9,4,0),(12,375,10,2,1),(13,360,11,2,1),(14,1000,12,2,1),(15,180,13,2,1),(16,20,14,3,1),(17,20000,14,4,1),(18,1000,15,4,1),(19,17,16,5,1),(20,120,17,4,1),(21,170,18,2,0),(22,21,18,5,0),(23,27,19,5,1),(24,0.001,20,2,0),(25,1000,20,2,1),(26,21,18,5,0),(27,21,18,5,1),(28,1000,21,2,0),(29,1000,22,2,0),(30,1000,23,2,0),(31,1000,26,2,0),(32,1000,27,2,0),(33,1000,28,2,0),(34,1000,25,2,1),(35,1000,29,2,1),(36,5,30,5,1),(37,1000,31,2,0),(38,1000,32,2,0),(39,6,31,5,1),(40,1000,23,2,1),(41,33,23,5,1),(42,120,9,4,1),(43,0.001,1,1,1),(44,1000,1,5,1),(45,1000,22,2,1),(46,0.001,33,2,0),(47,0.001,34,2,0),(48,1000,33,2,1),(49,1000,34,2,1);
/*!40000 ALTER TABLE `CONVERSION_UNIDAD` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `INSUMO`
--

DROP TABLE IF EXISTS `INSUMO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `INSUMO` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_insumo` varchar(100) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `stock_actual` float DEFAULT NULL,
  `stock_minimo_alerta` float DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `unidad_base_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_INSUMO_categoria` (`categoria`),
  KEY `ix_INSUMO_is_active` (`is_active`),
  KEY `ix_INSUMO_unidad_base_id` (`unidad_base_id`),
  CONSTRAINT `INSUMO_ibfk_1` FOREIGN KEY (`unidad_base_id`) REFERENCES `UNIDAD_MEDIDA` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `INSUMO`
--

LOCK TABLES `INSUMO` WRITE;
/*!40000 ALTER TABLE `INSUMO` DISABLE KEYS */;
INSERT INTO `INSUMO` VALUES (1,'Grenetina sin Sabor Duche','Materias Primas',2934,1000,1,2),(2,'Concentrado de Fresa','Materias Primas',110,2,1,5),(3,'Concentrado de Piña','Materias Primas',109.725,2,1,5),(4,'Concentrado de Jerez','Materias Primas',110,2,1,5),(5,'Concentrado de Limón','Materias Primas',110,2,1,5),(6,'Concentrado de Grosella','Materias Primas',110,2,1,5),(7,'Concentrado de Cajeta','Materias Primas',110,1,1,5),(8,'Concentrado de  Vainilla','Materias Primas',111,3,1,5),(9,'Concentrado de Nuez','Materias Primas',110,2,1,5),(10,'Lata de leche condensada','Materias Primas',105,18,1,5),(11,'Lata de leche evaporada','Materias Primas',205,20,1,5),(12,'Azucar','Materias Primas',108.58,28,1,1),(13,'Queso philadelphia ','Lácteos',81,30,1,5),(14,'Agua','Materias Primas',304.935,25,1,5),(15,'Leche','Lácteos',1015,80,1,3),(16,'Huevo','Materias Primas',72.4118,20,1,1),(17,'Concentrado de Coco','Materias Primas',205,23,1,5),(18,'Paquete Galletas María','Materias Primas',310,30,1,2),(19,'Limon','Frutas',208.26,10,1,1),(20,'Arroz','Materias Primas',103,20,1,1),(21,'Canela','Materias Primas',963,100,1,2),(22,'Crema para batir','Lácteos',105,30,1,1),(23,'Fresa','Frutas',108,20,1,1),(24,'Chocolate','Chocolates',1000,100,1,2),(25,'Mantequilla ','Lácteos',1001.9,100,1,1),(26,'Harina','Materias Primas',100,10,0,1),(27,'Harina de Trigo','Insumos de Repostería',200,20,0,1),(28,'Mantequilla','Lácteos',200,20,0,1),(29,'Harina','Insumos de Repostería',208.5,20,1,1),(30,'Manzana','Frutas',200.2,20,1,1),(31,'Banana','Frutas',206,20,1,1),(32,'Chocolate','Chocolates',200,20,0,1),(33,'Sal','Materias Primas',9.98,100,1,1),(34,'Azucar morena','Materias Primas',9.4,100,1,1);
/*!40000 ALTER TABLE `INSUMO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MERMA`
--

DROP TABLE IF EXISTS `MERMA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MERMA` (
  `id` int NOT NULL AUTO_INCREMENT,
  `insumo_id` int DEFAULT NULL,
  `cantidad_perdida` float NOT NULL,
  `causa` varchar(255) DEFAULT NULL,
  `notas_adicionales` text,
  `fecha_registro` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `producto_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_MERMA_fecha_registro` (`fecha_registro`),
  KEY `ix_MERMA_insumo_id` (`insumo_id`),
  KEY `ix_MERMA_is_active` (`is_active`),
  KEY `ix_merma_is_active_fecha_registro` (`is_active`,`fecha_registro`),
  KEY `ix_merma_producto_id` (`producto_id`),
  CONSTRAINT `fk_merma_producto_id_product` FOREIGN KEY (`producto_id`) REFERENCES `product` (`id`),
  CONSTRAINT `MERMA_ibfk_1` FOREIGN KEY (`insumo_id`) REFERENCES `INSUMO` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MERMA`
--

LOCK TABLES `MERMA` WRITE;
/*!40000 ALTER TABLE `MERMA` DISABLE KEYS */;
INSERT INTO `MERMA` VALUES (1,NULL,4,'Daño','Se derritieron por el mal funcionamiento del refrigerador','2026-04-16 22:52:40',1,19),(2,NULL,3,'Caducidad','Las fresas se hecharon a perder','2026-04-16 22:54:53',0,20);
/*!40000 ALTER TABLE `MERMA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UNIDAD_MEDIDA`
--

DROP TABLE IF EXISTS `UNIDAD_MEDIDA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UNIDAD_MEDIDA` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `abreviatura` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UNIDAD_MEDIDA`
--

LOCK TABLES `UNIDAD_MEDIDA` WRITE;
/*!40000 ALTER TABLE `UNIDAD_MEDIDA` DISABLE KEYS */;
INSERT INTO `UNIDAD_MEDIDA` VALUES (1,'Kilogramo','kg'),(2,'Gramo','g'),(3,'Litro','L'),(4,'Mililitro','ml'),(5,'Unidad','u'),(6,'Cartón','cart'),(7,'Onza','oz');
/*!40000 ALTER TABLE `UNIDAD_MEDIDA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('d8f3a7c2b1e4');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_order`
--

DROP TABLE IF EXISTS `custom_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `custom_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `detalle_venta_id` int NOT NULL,
  `tipo_evento` varchar(50) NOT NULL,
  `instrucciones_decoracion` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `detalle_venta_id` (`detalle_venta_id`),
  CONSTRAINT `custom_order_ibfk_1` FOREIGN KEY (`detalle_venta_id`) REFERENCES `detalle_venta` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_order`
--

LOCK TABLES `custom_order` WRITE;
/*!40000 ALTER TABLE `custom_order` DISABLE KEYS */;
INSERT INTO `custom_order` VALUES (1,11,'cumpleaños','Con trozos de piña'),(2,12,'otro','Sin especificaciones'),(3,13,'otro','Sin especificaciones'),(4,15,'cumpleaños','Feliz Cumpleaños'),(5,16,'cumpleaños','Feliz Cumpleaños'),(6,18,'baby_shower','Flores rosas y azules'),(7,19,'cumpleaños','Glaceado especial');
/*!40000 ALTER TABLE `custom_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion_despacho` varchar(200) DEFAULT NULL,
  `puntos_acumulados` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_customer_user_id` (`user_id`),
  KEY `ix_customer_is_active` (`is_active`),
  CONSTRAINT `customer_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (1,2,'+52111223344','Calle falsa, #123',100,1),(2,6,'4776532536','Avenida Pradera 116',1636,1),(3,7,'4775679432','Fraccionamiento El Dorado #123',2,0),(4,8,'4779845362','Fraccionamiento El Dorado #120',34,1);
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_venta`
--

DROP TABLE IF EXISTS `detalle_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_venta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `venta_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario_aplicado` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_detalle_venta_producto_id` (`producto_id`),
  KEY `ix_detalle_venta_venta_id` (`venta_id`),
  CONSTRAINT `detalle_venta_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `product` (`id`),
  CONSTRAINT `detalle_venta_ibfk_2` FOREIGN KEY (`venta_id`) REFERENCES `venta` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_venta`
--

LOCK TABLES `detalle_venta` WRITE;
/*!40000 ALTER TABLE `detalle_venta` DISABLE KEYS */;
INSERT INTO `detalle_venta` VALUES (1,1,16,25,20),(2,2,18,1,30),(3,2,14,1,17),(4,2,13,1,170),(5,3,19,4,12),(6,4,20,3,25),(7,5,13,1,170),(8,5,14,1,17),(9,5,12,1,17),(10,5,7,1,17),(11,6,3,11,17),(12,7,16,10,20),(13,7,10,2,150),(14,8,20,1,25),(15,9,13,2,170),(16,10,13,2,170),(17,11,20,1,25),(18,12,13,2,170),(19,13,22,2,500),(20,14,22,1,500);
/*!40000 ALTER TABLE `detalle_venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_producto` varchar(100) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `precio_venta` float DEFAULT NULL,
  `stock` int DEFAULT NULL,
  `imagen_url` varchar(200) DEFAULT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `pedido_minimo` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `ix_product_categoria` (`categoria`),
  KEY `ix_product_is_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` VALUES (2,'Gelatina de Fresa','Postres Fríos',17,25,'/static/images/productos/ab5840c5621641e78925f569015c7c0b.png','Gelatina de agua sabor fresa en vaso de 100g',1,10),(3,'Gelatina de Piña','Postres Fríos',17,25,'/static/images/productos/9fd3cc174a8d49309cf47f3a4c1ef0a2.png','Gelatina de agua sabor piña en vaso de 100g',1,10),(4,'Gelatina de Jerez','Postres Fríos',17,25,'/static/images/productos/44065b1c09634248ae084fc6bd4d0beb.png','Gelatina de agua sabor jerez en vaso de 100g',1,10),(5,'Gelatina de Grosella','Postres Fríos',17,25,'/static/images/productos/074ef7e523f046069bec6844c0faf8ad.png','Gelatina de agua sabor grosella en vaso de 100g',1,10),(6,'Gelatina de Limón','Postres Fríos',17,25,'/static/images/productos/2f4ccbb167284bb7950b2c4eedd270fc.png','Gelatina de agua sabor limón en vaso de 100g',1,10),(7,'Gelatina de Cajeta','Postres Fríos',17,24,'/static/images/productos/87f4a533f7ee4996bc07d0bf48f0403e.png','Gelatina de leche sabor cajeta en vaso de 100g',1,10),(8,'Gelatina de Vainilla','Postres Fríos',17,25,'/static/images/productos/b5a0abcf27df475eb51d908cfcd1aeef.png','Gelatina de leche sabor vainilla en vaso de 100g',1,10),(9,'Gelatina de Nuez','Postres Fríos',17,25,'/static/images/productos/b2023b025cd04907bcd6e041582b287f.png','Gelatina de leche sabor Nuez en vaso de 100g',1,10),(10,'Flan de Queso','Postres Horneados',150,25,'/static/images/productos/fde13547c7c74908beaf8cf719479a52.png','Flan napolitano de queso de un kilo',1,2),(11,'Gelatina de Mosaico','Postres Fríos',20,25,'/static/images/productos/3046d6d00c6046d596f7650e4341529e.png','Gelatina de leche y agua, varios sabores en un vaso de 100g',1,10),(12,'Gelatina de Coco','Postres Fríos',17,24,'/static/images/productos/f0677c931f0d4bd1ac080664eb2d9972.png','Gelatina de agua sabor coco, en un vaso de 100g',1,10),(13,'Carlota de Limón','Postres Fríos',170,23,'/static/images/productos/8014fb2ee1ed45d0a6ecfe3dbd87770f.png','Carlota de limón en recipiente de 1 kilo',1,2),(14,'Arroz con Leche','Postres Fríos',30,23,'/static/images/productos/de459bf6eff5431b9073db3d6e51dc90.png','Arroz con leche en vaso de 100g',1,10),(15,'Fresas con Crema','Postres Fríos',25,25,'/static/images/productos/de8c2960b36e4741a1a82e5e2ca091be.png','Fresas con crema en un vaso de 100g',1,10),(16,'Brownies','Postres Horneados',20,50,'/static/images/productos/bf571065ce77415688a265c3e79d18c4.png','Brownie artesanal de chocolate intenso y mantequilla premium, con textura densa y corazón húmedo.',1,10),(17,'Galletas de mantequilla','Postres Horneados',50,25,'/static/images/productos/c423f52b75004d66b24acc3f7cfa9964.png','Deliciosas galletas de mantequilla, artesanales y echas con amor',1,15),(18,'Manzanas Caramelizadas','Postres de Vitrina',30,24,'/static/images/productos/5584150ec43d4c1885c66b8a6239ddff.png','Manzanas caramelizadas con un caramelo artesanal',1,4),(19,'Chocobananas','Snacks Frutales',15,17,'/static/images/productos/347f8770e1f1480dafebf6b27187af61.png','Bananas cubiertas de chocolate artesanal',1,4),(20,'Chocofresas','Postres Fríos',25,20,'/static/images/productos/ef57fee5966e40cc9594112afe43cb28.png','Fresas cubiertas de chocolate artesanal',1,4),(21,'test','Postres Fríos',1,0,'/static/images/productos/07724c9ab88741adb5f97079749cc509.jpeg','1',0,1),(22,'Tarta de Manzana','Postres Horneados',500,0,'/static/images/productos/0b5f3834b423485ea52d02b35c41cb2a.jpeg','Tarta de manzana',1,2);
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `production_task`
--

DROP TABLE IF EXISTS `production_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_task` (
  `id` int NOT NULL AUTO_INCREMENT,
  `receta_id` int NOT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `prioridad` varchar(10) DEFAULT NULL,
  `fecha_limite` datetime NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_production_task_estado` (`estado`),
  KEY `ix_production_task_fecha_limite` (`fecha_limite`),
  KEY `ix_production_task_is_active` (`is_active`),
  KEY `ix_production_task_prioridad` (`prioridad`),
  KEY `ix_production_task_prioridad_is_active_fecha_limite` (`prioridad`,`is_active`,`fecha_limite`),
  KEY `ix_production_task_receta_id` (`receta_id`),
  CONSTRAINT `production_task_ibfk_1` FOREIGN KEY (`receta_id`) REFERENCES `recipe` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_task`
--

LOCK TABLES `production_task` WRITE;
/*!40000 ALTER TABLE `production_task` DISABLE KEYS */;
INSERT INTO `production_task` VALUES (1,45,'En Horno','Alta','2026-04-16 22:40:00','2026-04-16 22:31:35',0),(2,45,'En Horno','Alta','2026-04-16 22:40:00','2026-04-16 22:31:35',0),(3,45,'Decorando','Media','2026-04-16 22:40:00','2026-04-16 22:40:38',0),(4,45,'Pendiente','Media','2026-04-17 22:43:00','2026-04-16 22:43:15',0),(5,45,'Pendiente','Alta','2026-04-18 22:47:00','2026-04-16 22:47:46',0),(6,77,'Listo','Media','2026-04-17 20:42:00','2026-04-17 20:43:30',1),(7,77,'Pendiente','Media','2026-04-17 20:42:00','2026-04-17 20:43:30',1);
/*!40000 ALTER TABLE `production_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase`
--

DROP TABLE IF EXISTS `purchase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase` (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int NOT NULL,
  `fecha_orden` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `ix_purchase_fecha_orden` (`fecha_orden`),
  KEY `ix_purchase_is_active` (`is_active`),
  KEY `ix_purchase_is_active_supplier_id` (`is_active`,`supplier_id`),
  KEY `ix_purchase_supplier_id` (`supplier_id`),
  CONSTRAINT `purchase_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `supplier` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase`
--

LOCK TABLES `purchase` WRITE;
/*!40000 ALTER TABLE `purchase` DISABLE KEYS */;
INSERT INTO `purchase` VALUES (1,4,'2026-04-16 20:06:56',1),(2,1,'2026-04-16 20:35:23',1),(3,3,'2026-04-16 20:39:22',1),(4,5,'2026-04-16 20:41:27',1),(5,8,'2026-04-16 20:44:03',1),(6,4,'2026-04-17 09:12:32',1),(7,3,'2026-04-17 09:55:46',1),(8,1,'2026-04-17 20:31:13',1);
/*!40000 ALTER TABLE `purchase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_detail`
--

DROP TABLE IF EXISTS `purchase_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purchase_id` int NOT NULL,
  `insumo_id` int NOT NULL,
  `cantidad` float NOT NULL,
  `precio_unitario` float NOT NULL,
  `unidad_medida_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_purchase_detail_insumo_id` (`insumo_id`),
  KEY `ix_purchase_detail_purchase_id` (`purchase_id`),
  KEY `ix_purchase_detail_unidad_medida_id` (`unidad_medida_id`),
  CONSTRAINT `purchase_detail_ibfk_1` FOREIGN KEY (`insumo_id`) REFERENCES `INSUMO` (`id`),
  CONSTRAINT `purchase_detail_ibfk_2` FOREIGN KEY (`purchase_id`) REFERENCES `purchase` (`id`),
  CONSTRAINT `purchase_detail_ibfk_3` FOREIGN KEY (`unidad_medida_id`) REFERENCES `UNIDAD_MEDIDA` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_detail`
--

LOCK TABLES `purchase_detail` WRITE;
/*!40000 ALTER TABLE `purchase_detail` DISABLE KEYS */;
INSERT INTO `purchase_detail` VALUES (22,3,13,10,38,5),(23,3,15,15,24,3),(24,3,22,5,65,1),(25,3,25,3,26,1),(26,4,19,9,45,1),(27,4,23,8,55,1),(28,4,30,5,35,1),(29,4,31,6,22,1),(30,5,29,10,75,1),(31,2,1,1000,0.6,2),(32,2,2,10,55,5),(33,2,3,10,55,5),(34,2,4,10,55,5),(35,2,5,10,55,5),(36,2,6,10,55,5),(37,2,7,10,55,5),(38,2,8,10,55,5),(39,2,9,10,55,5),(40,2,10,5,25,5),(41,2,11,5,25,5),(42,2,12,10,28,1),(43,2,14,5,55,5),(44,2,16,3,45,1),(45,2,17,5,51,5),(46,2,18,10,0.15,2),(47,2,20,3,34,1),(48,2,21,3,41,2),(50,1,24,1000,0.2,2),(51,6,24,1000,0.2,2),(52,7,13,1,10,5),(53,8,8,1,30,5),(54,8,34,10,32,1),(55,8,33,10,27,1);
/*!40000 ALTER TABLE `purchase_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipe`
--

DROP TABLE IF EXISTS `recipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recipe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `nombre_variante` varchar(100) NOT NULL,
  `cantidad_producida` float DEFAULT NULL,
  `tiempo_estimado_min` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_recipe_is_active` (`is_active`),
  KEY `ix_recipe_product_id` (`product_id`),
  CONSTRAINT `recipe_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipe`
--

LOCK TABLES `recipe` WRITE;
/*!40000 ALTER TABLE `recipe` DISABLE KEYS */;
INSERT INTO `recipe` VALUES (1,2,'Pedido Chico',10,135,1),(2,2,'Pedido Mediano',45,188,1),(3,2,'Pedido Grande',220,450,1),(4,3,'Pedido Chico',10,135,1),(5,3,'Pedido Mediano',45,186,1),(6,3,'Pedido Grande',220,450,1),(7,4,'Pedido Chico',10,135,1),(8,4,'Pedido Mediano',45,188,1),(9,5,'Pedido Chico',10,135,1),(10,5,'Pedido Mediano',45,188,1),(11,4,'Pedido Grande',220,450,1),(12,5,'Pedido Grande',220,450,1),(13,6,'Pedido Chico',10,135,1),(14,7,'Pedido Chico',10,134,1),(15,6,'Pedido Mediano',45,188,1),(16,7,'Pedido Mediano',45,188,1),(17,6,'Pedido Grande',220,450,1),(18,7,'Pedido Grande',220,450,1),(19,8,'Pedido Chico',10,135,1),(20,8,'Pedido Mediano',45,187,1),(21,9,'Pedido Chico',10,135,1),(22,8,'Pedido Grande',220,450,1),(23,9,'Pedido Mediano',45,188,1),(24,9,'Pedido Grande',220,450,1),(25,10,'Pedido chico',3,150,1),(26,10,'Pedido mediano',5,270,1),(27,10,'Pedido Grande',24,1200,1),(28,12,'Pedido chico',10,135,1),(29,12,'Pedido mediano',45,188,1),(30,12,'Pedido Grande',220,450,1),(31,11,'Pedido chico',25,140,1),(32,11,'Pedido mediano',45,193,1),(33,11,'Pedido Grande',220,455,1),(34,13,'Pedido Personalizado',1,260,1),(35,13,'Pedido Grande',20,1120,1),(36,13,'Pedido chico',5,280,1),(37,14,'Pedido Chico',10,45,1),(38,13,'Pedido mediano',12,840,1),(39,14,'Pedido Mediano',45,70,1),(40,14,'Pedido Grande',220,95,1),(41,15,'Pedido Personalizado',1,28,1),(42,15,'Pedido chico',10,145,1),(43,15,'Pedido mediano',45,599,1),(44,15,'Pedido Grande',220,2875,1),(45,16,'Pedido Chico',10,45,1),(46,17,'Pedido Personalizado',1,20,1),(47,17,'Pedido chico',10,160,1),(48,16,'Pedido Mediano',55,65,1),(49,17,'Pedido mediano',55,850,1),(50,16,'Pedido Grande',200,95,1),(51,17,'Pedido Grande',200,1025,1),(52,16,'Pedido Personalizado',1,25,1),(53,14,'Pedido Personalizado',1,10,1),(54,18,'Pedido Unico',1,33,1),(55,18,'Pedido chico',6,45,1),(56,10,'Pedido Personalizado',1,50,1),(57,18,'Pedido mediano',10,53,1),(58,18,'Pedido Grande',100,230,1),(59,7,'Pedido Personalizado',1,44,1),(60,12,'Pedido Personalizado',1,45,1),(61,2,'Pedido Personalizado',1,45,1),(62,19,'Pedido Personalizado',1,20,1),(63,5,'Pedido Personalizado',1,45,1),(64,19,'Pedido chico',6,67,1),(65,4,'Pedido Personalizado',1,45,1),(66,6,'Pedido Personalizado',1,45,1),(67,19,'Pedido mediano',10,73,1),(68,19,'Pedido Grande',100,140,1),(69,11,'Pedido Personalizado',1,45,1),(70,9,'Pedido Personalizado',1,45,1),(71,3,'Pedido Personalizado',1,45,1),(72,8,'Pedido Personalizado',1,45,1),(73,20,'Pedido Personalizado',1,26,1),(74,20,'Pedido chico',6,41,1),(75,20,'Pedido mediano',10,57,1),(76,20,'Pedido Grande',100,220,1),(77,22,'Unidad',1,1,1);
/*!40000 ALTER TABLE `recipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipe_detail`
--

DROP TABLE IF EXISTS `recipe_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recipe_detail` (
  `recipe_id` int NOT NULL,
  `insumo_id` int NOT NULL,
  `cantidad` float DEFAULT NULL,
  `unidad_medida_id` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`recipe_id`,`insumo_id`),
  KEY `ix_recipe_detail_insumo_id` (`insumo_id`),
  KEY `ix_recipe_detail_is_active` (`is_active`),
  KEY `ix_recipe_detail_unidad_medida_id` (`unidad_medida_id`),
  CONSTRAINT `recipe_detail_ibfk_1` FOREIGN KEY (`insumo_id`) REFERENCES `INSUMO` (`id`),
  CONSTRAINT `recipe_detail_ibfk_2` FOREIGN KEY (`recipe_id`) REFERENCES `recipe` (`id`),
  CONSTRAINT `recipe_detail_ibfk_3` FOREIGN KEY (`unidad_medida_id`) REFERENCES `UNIDAD_MEDIDA` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipe_detail`
--

LOCK TABLES `recipe_detail` WRITE;
/*!40000 ALTER TABLE `recipe_detail` DISABLE KEYS */;
INSERT INTO `recipe_detail` VALUES (1,1,37,2,1),(1,2,10,4,1),(1,12,200,2,1),(1,14,1,3,1),(2,1,166.5,2,1),(2,2,45,4,1),(2,12,900,2,1),(2,14,4.5,3,1),(3,1,814,2,1),(3,2,220,4,1),(3,12,4.4,1,1),(3,14,22,3,1),(4,1,37,2,1),(4,3,10,4,1),(4,12,200,2,1),(4,14,1,3,1),(5,1,166.5,2,1),(5,3,45,4,1),(5,12,900,2,1),(5,14,4.5,3,1),(6,1,814,2,1),(6,2,220,4,1),(6,12,4.4,1,1),(6,14,22,3,1),(7,1,37,2,1),(7,4,10,4,1),(7,12,200,2,1),(7,14,1,3,1),(8,1,166.5,2,1),(8,4,45,4,1),(8,12,900,2,1),(8,14,4.5,3,1),(9,1,37,2,1),(9,6,10,4,1),(9,12,200,2,1),(9,14,1,3,1),(10,1,166.5,2,1),(10,6,45,4,1),(10,12,900,2,1),(10,14,4.5,3,1),(11,1,814,2,1),(11,4,220,4,1),(11,12,4.4,1,1),(11,14,22,3,1),(12,1,814,2,1),(12,6,220,4,1),(12,12,4.4,1,1),(12,14,22,3,1),(13,1,37,2,1),(13,5,10,4,1),(13,12,200,2,1),(13,14,1,3,1),(14,1,37,2,1),(14,7,10,4,1),(14,12,200,2,1),(14,15,1,3,1),(15,1,166.5,2,1),(15,5,45,4,1),(15,12,900,2,1),(15,14,4.5,3,1),(16,1,166.5,2,1),(16,7,45,4,1),(16,12,900,2,1),(16,15,4.5,3,1),(17,1,814,2,1),(17,5,220,4,1),(17,12,4.4,1,1),(17,14,22,3,1),(18,1,814,2,1),(18,7,220,4,1),(18,12,4.4,1,1),(18,15,22,3,1),(19,1,37,2,1),(19,8,10,4,1),(19,12,200,2,1),(19,15,1,3,1),(20,1,166.5,2,1),(20,8,45,4,1),(20,12,900,2,1),(20,14,4.5,3,0),(20,15,4.5,3,1),(21,1,37,2,1),(21,9,10,4,1),(21,12,200,2,1),(21,15,1,3,1),(22,1,814,2,1),(22,8,220,4,1),(22,12,4.4,1,1),(22,15,22,3,1),(23,1,166.5,2,1),(23,9,45,4,1),(23,12,900,2,1),(23,15,4.5,3,1),(24,1,814,2,1),(24,9,220,4,1),(24,12,4.4,1,1),(24,15,22,3,1),(25,8,30,4,1),(25,10,3,5,1),(25,11,3,5,1),(25,12,30,2,1),(25,13,3,5,1),(25,16,15,5,1),(26,8,50,4,1),(26,10,5,5,1),(26,11,5,5,1),(26,12,50,2,1),(26,13,5,5,1),(26,16,25,5,1),(27,8,240,4,1),(27,10,24,5,1),(27,11,24,5,1),(27,12,240,2,1),(27,13,24,5,1),(27,16,120,5,1),(28,1,37,2,1),(28,12,200,2,1),(28,15,1,3,1),(28,17,10,4,1),(29,1,166.5,2,1),(29,12,900,2,1),(29,15,4.5,3,1),(29,17,45,4,1),(30,1,814,2,1),(30,12,4.4,1,1),(30,15,22,3,1),(30,17,220,4,1),(31,1,40,2,1),(31,3,10,4,1),(31,4,10,4,1),(31,5,10,4,1),(31,6,10,4,1),(31,14,4,3,1),(31,15,1,3,1),(31,17,10,4,1),(32,1,72,2,1),(32,3,18,4,1),(32,4,18,4,1),(32,5,18,4,1),(32,6,18,4,1),(32,14,7.2,3,1),(32,15,1.8,3,1),(32,17,18,4,1),(33,1,352,2,1),(33,3,88,4,1),(33,4,88,4,1),(33,5,87.999,4,1),(33,6,88,4,1),(33,14,35.2,3,1),(33,15,8.8,3,1),(33,17,88,4,1),(34,10,1,5,1),(34,11,1,5,1),(34,18,200,2,1),(34,19,6,5,1),(35,10,20,5,1),(35,11,20,5,1),(35,18,4000,2,1),(35,19,120,5,1),(36,10,5,5,1),(36,11,5,5,1),(36,18,1000,2,1),(36,19,30,5,1),(37,12,150,2,1),(37,15,1,3,1),(37,20,190,2,1),(37,21,5,2,1),(38,10,12,5,1),(38,11,12,5,1),(38,18,2400,2,1),(38,19,72,5,1),(39,12,675,2,1),(39,15,4.5,3,1),(39,20,810,2,1),(39,21,20,2,1),(40,12,3.3,1,1),(40,15,22,3,1),(40,20,3.96,1,1),(40,21,110,2,1),(41,8,2,4,1),(41,10,30,2,1),(41,12,10,2,1),(41,22,60,2,1),(41,23,100,2,1),(42,8,20,4,1),(42,10,300,2,1),(42,12,100,2,1),(42,22,600,2,1),(42,23,1,1,1),(43,8,90,4,1),(43,10,1350,2,1),(43,12,450,2,1),(43,22,2.7,1,1),(43,23,4.5,1,1),(44,8,440,4,1),(44,10,6600,2,1),(44,12,2.2,1,1),(44,22,13.2,1,1),(44,23,22,1,1),(45,12,200,2,1),(45,16,2,5,1),(45,24,200,2,1),(45,25,100,2,1),(45,27,60,2,0),(45,29,60,2,1),(46,12,200,2,1),(46,16,1,5,1),(46,25,227,2,1),(46,26,280,2,0),(46,29,280,2,1),(47,12,2,1,1),(47,16,10,5,1),(47,25,2.27,1,1),(47,26,2.8,1,0),(47,29,2.8,1,1),(48,12,1.1,1,1),(48,16,11,5,1),(48,24,1100,2,1),(48,25,550,2,1),(48,29,330,2,1),(49,12,11,1,1),(49,16,55,5,1),(49,25,12.5,1,1),(49,29,15.4,1,1),(50,12,4,1,1),(50,16,40,5,1),(50,24,4000,2,1),(50,25,2,1,1),(50,29,1.2,1,1),(51,12,40,1,1),(51,16,200,5,1),(51,25,45.4,1,1),(51,29,56,1,1),(52,12,20,2,1),(52,16,1,5,1),(52,24,20,2,1),(52,25,10,2,1),(52,29,6,2,1),(53,12,15,2,1),(53,15,100,4,1),(53,20,19,2,1),(53,21,0.5,2,1),(54,12,67,2,1),(54,14,17,4,1),(54,30,1,5,1),(55,12,399.999,2,1),(55,14,100,4,1),(55,30,6,5,1),(56,8,10,4,1),(56,11,1,5,1),(56,12,10,2,1),(56,13,1,5,1),(56,16,5,5,1),(57,12,667,2,1),(57,14,167,4,1),(57,30,10,5,1),(58,12,6.7,1,1),(58,14,1.7,3,1),(58,30,100,5,1),(59,1,13,2,1),(59,7,1,4,1),(59,12,20,2,1),(59,15,100,4,1),(60,1,13,2,1),(60,12,20,2,1),(60,15,100,4,1),(60,17,1,4,1),(61,1,13,2,1),(61,2,3,4,1),(61,12,20,2,1),(61,14,100,4,1),(62,22,17,2,1),(62,24,50,2,1),(62,31,1,5,1),(63,1,6,2,1),(63,6,3,4,1),(63,12,20,2,1),(63,14,100,4,1),(64,22,100,2,1),(64,24,300,2,1),(64,31,6,5,1),(65,1,6,2,1),(65,4,3,4,1),(65,12,20,2,1),(65,14,100,4,1),(66,1,6,2,1),(66,5,3,4,1),(66,12,20,2,1),(66,14,100,4,1),(67,22,167,2,1),(67,24,500,2,1),(67,31,10,5,1),(68,22,1.7,1,1),(68,24,5000,2,1),(68,31,100,5,1),(69,1,8,2,1),(69,3,3,4,1),(69,4,3,4,1),(69,5,3,4,1),(69,6,3,4,1),(69,14,400,4,1),(69,15,100,4,1),(69,17,3,4,1),(70,1,6,2,1),(70,9,3,4,1),(70,12,20,2,1),(70,15,100,4,1),(71,1,6,2,1),(71,3,3,4,1),(71,12,20,2,1),(71,14,100,4,1),(72,1,6,2,1),(72,8,3,4,1),(72,12,20,2,1),(72,15,100,4,1),(73,22,42,2,1),(73,23,1,5,1),(73,24,50,2,1),(74,22,250,2,1),(74,23,6,5,1),(74,24,300,2,1),(75,22,300,2,1),(75,23,10,5,1),(75,24,500,2,1),(76,22,1.2,1,1),(76,23,100,5,1),(76,24,5000,2,1),(77,12,50,2,1),(77,14,50,4,1),(77,19,5,5,1),(77,21,10,2,1),(77,25,150,2,1),(77,29,300,2,1),(77,30,6,5,1),(77,33,5,2,1),(77,34,150,2,1);
/*!40000 ALTER TABLE `recipe_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `supplier`
--

DROP TABLE IF EXISTS `supplier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplier` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_empresa` varchar(100) NOT NULL,
  `categoria_insumos` varchar(50) NOT NULL,
  `nombre_contacto` varchar(100) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `correo_electronico` varchar(100) NOT NULL,
  `direccion_fisica` varchar(200) DEFAULT NULL,
  `notas_adicionales` text,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `ix_supplier_categoria_insumos` (`categoria_insumos`),
  KEY `ix_supplier_is_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `supplier`
--

LOCK TABLES `supplier` WRITE;
/*!40000 ALTER TABLE `supplier` DISABLE KEYS */;
INSERT INTO `supplier` VALUES (1,'Distribuidora Nacional de Granos y Harinas S.A.','Materias Primas','Roberto Martínez','4771234567','ventas@distribuidoranacional.com','Av. Industrial No. 405, Col. Julián de Obregón, León, Gto.','Entrega de 08:00 a 10:00. Entregan al día siguiente de realizar el pedido vía telefónica. Suministra diversos polvos y granos, destacando harina de trigo, azúcares y levaduras entre su catálogo.',1),(2,'Eco-Empaques Creativos','Packaging','Sofía Casas','5559876543','scasas@ecoempaques.mx','Calle de los Empaques #12, Parque Industrial Norte, Querétaro, Qro.','Entrega de 10:00 a 14:00. Visita la ciudad todos los miércoles para entrega de pedidos. Maneja todo tipo de empaques, incluyendo cajas personalizadas, domos y capacillos de diversos tamaños.',1),(3,'Lácteos San Juan de los Lagos','Lácteos','Pedro Alcantara','3957821100','pedidos@lacteossanjuan.com.mx','Carretera Lagos-San Juan Km 4.5, San Juan de los Lagos, Jal.','Entrega de 07:00 a 09:00. Tiene ruta de entrega fija en la ciudad 3 veces por semana. Distribuye derivados de la leche, principalmente leche entera, crema para batir y mantequillas.',1),(4,'Cacao Real & Co.','Chocolates','Beatriz Echeverría','4773329088','beatriz.ventas@cacaoreal.com','Blvd. Adolfo López Mateos #1502, Col. Centro, León, Gto.','Entrega de 11:00 a 13:00. Entregan al día siguiente de solicitar el pedido por teléfono. Especialistas en derivados del cacao; puede traer chocolate de cobertura, chispas y cocoa, entre otros.',1),(5,'Frutería El Huerto del Bajío','Frutas','Javier Solís','4775562231','elhuertobajio@gmail.com','Central de Abastos, Bodega H-24, León, Gto.','Entrega de 06:00 a 08:00. Surtido inmediato al día siguiente de la llamada. Trae fruta fresca de temporada, tales como fresas, frutos rojos y duraznos según disponibilidad.',1),(6,'Aromas y Sabores de México','Esencias','Elena Ruiz','3336142299','contacto@aromasysabores.mx','Av. Vallarta 2340, Col. Americana, Guadalajara, Jal.','Entrega de 09:00 a 12:00. Visita la ciudad todos los viernes para resurtir. Cuenta con una amplia gama de concentrados, incluyendo vainilla natural, almendra y colorantes variados.',1),(7,'Detalles Dulces S.A. de C.V.','Decoraciones','Mónica Pantoja','4778894455','ventas@detallesdulces.com','Calle Madero #410, Zona Centro, León, Gto.','Entrega de 12:00 a 16:00. Pedido telefónico con entrega garantizada al día siguiente. Maneja artículos decorativos comestibles como sprinkles, perlas y flores de azúcar de diversos estilos.',1),(8,'Todo para el Chef','Insumos de Repostería','Carlos Aranda','4776703321','caranda@todochef.com.mx','Av. Panorama #89, Col. Valle del Campestre, León, Gto.','Entrega de 10:00 a 15:00. entrega al día siguiente de confirmar el pedido. Proveedor de utensilios desechables y herramientas, entre los que destacan mangas, papel encerado y moldes.',1),(9,'Servicios Químicos de Limpieza LimpioYa','Otros','Ricardo Vega','4774410092','rvega@limpioya.com.mx','Calle de la Limpieza #102, Col. San Miguel, León, Gto.','Entrega de 08:00 a 11:00. Surtido de químicos al día siguiente de solicitarlo por teléfono. Trae productos de limpieza de grado alimenticio, sanitizantes y equipo de protección.',1);
/*!40000 ALTER TABLE `supplier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_completo` varchar(150) NOT NULL,
  `correo_electronico` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol_asignado` varchar(50) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo_electronico` (`correo_electronico`),
  UNIQUE KEY `ix_user_correo_electronico` (`correo_electronico`),
  KEY `ix_user_rol_asignado` (`rol_asignado`),
  KEY `ix_user_is_active` (`is_active`),
  KEY `ix_user_rol_asignado_is_active` (`rol_asignado`,`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','admin@maisonglace.com','scrypt:32768:8:1$FHgao0lVt75lLHI0$65b1023daef7a06c177de4775d3c4e006e8446f2127c1dc64ec2056e2fd77997fe710a11e04ce32ff0564509af39a98fd7fed964353cbfdbfc2fe338b3ff1b97','admin',1),(2,'superadmin','superadmin@maisonglace.com','scrypt:32768:8:1$nrCP0EoWySwaKh2I$83428168cc96870f8470ae1ebb3643b408b17f06e420759e4573de7f93e4e28a34c605cf09e48042b61598fbc95a880e24c30ffa599d2619aa20ef4be94a5a04','superadmin',1),(3,'Miriam Conchas','vendedor@maisonglace.com.deleted.3','scrypt:32768:8:1$2GfaWcIFdFtOhSVH$7ec7d42b6bfd74c06b9974fd4c6c6165a78a98f34adf7d6439115f9746e020ed9f89ab3d505189ee22e5d920400be6c92e0e19c4184300135a074bd89e46e4ff','seller',0),(4,'Melchor Ruiz','chef@maisonglace.com','scrypt:32768:8:1$8Hw3QCjIiWn5hTD0$d5bddef9df00f546ce1460de6ca0ad21a1647aeb91225f237c0603feb93211a7da645181f8c13a48934e9647e35219c45c486e3f2ae5e38477c0be78f21b2a73','chef',1),(5,'Paulina Vargas','vendedor@maisonglace.com','scrypt:32768:8:1$CSbE7dUSRSLWrdEW$3856c31c972313201b37109d094ee743e623c1fedf61640ba0ec872d2a8308e38d2461253a5607bd37311f9dc29bf43062fb79f2e5489b9efc31f84eb0cbced9','seller',1),(6,'Miriam Conchas','mconchas@gmail.com','scrypt:32768:8:1$yVqHAsABoGjYqk13$38775beed6515054c09f21034865fa0f5a00ae7dacbaf120a1096f794bd01ac959eb4c3e2894bfeb1b82f2a74820a04a372ac306c9ba609021facce86474d1a3','customer',1),(7,'Sandro Ramirez','sramirez@maisonglace.com.deleted.7','scrypt:32768:8:1$oSEEvxCUWsNFFs43$65fe641970302a0732940f5cf5368267dd37b9ae83edd349af31dcda51bd369dc257a2e69edfe96ea9fcb3c0c697bf0e79089a860936d9053a745a637dc48e43','customer',0),(8,'Sandro Ramirez','sramirez@gmail.com','scrypt:32768:8:1$ZLl8GjDLpgi7acDj$305f1efb1ed4ed93c941a0b45bedeb5bc38cf3195d67bff821e6d41e44ec2123ffc132cb89d020a27f9b1554e45db1141516fa3d054cd6f9400149875f223642','customer',1);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta`
--

DROP TABLE IF EXISTS `venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int DEFAULT NULL,
  `fecha_hora` datetime DEFAULT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `monto_recibido` float DEFAULT NULL,
  `monto_cambio` float DEFAULT NULL,
  `lugar_entrega` varchar(50) DEFAULT NULL,
  `fecha_hora_entrega` datetime DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_venta_estado` (`estado`),
  KEY `ix_venta_cliente_id` (`cliente_id`),
  KEY `ix_venta_fecha_hora` (`fecha_hora`),
  CONSTRAINT `venta_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `customer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta`
--

LOCK TABLES `venta` WRITE;
/*!40000 ALTER TABLE `venta` DISABLE KEYS */;
INSERT INTO `venta` VALUES (1,NULL,'2026-04-16 22:28:00','efectivo',1000,1000,'Tienda','2026-04-16 22:28:00','Entregado'),(2,NULL,'2026-04-16 22:47:11','efectivo',500,500,'Tienda','2026-04-16 22:47:11','Entregado'),(3,NULL,'2026-04-16 23:02:43','efectivo',1000,1000,'Tienda','2026-04-16 23:02:43','Entregado'),(4,NULL,'2026-04-16 23:34:45','efectivo',500,425,'Tienda','2026-04-16 23:34:45','Entregado'),(5,NULL,'2026-04-16 23:39:09','tarjeta',221,0,'Tienda','2026-04-16 23:39:09','Entregado'),(6,2,'2026-04-17 00:02:50','tarjeta',187,0,'Tienda','2026-04-19 18:00:00','Entregado'),(7,2,'2026-04-17 00:06:44','tarjeta',500,0,'Domicilio','2026-04-20 19:10:00','Pendiente'),(8,3,'2026-04-17 00:19:27','efectivo',500,475,'Tienda','2026-04-17 00:19:27','Entregado'),(9,2,'2026-04-17 00:28:39','efectivo',500,160,'tienda','2026-04-21 19:30:00','Pendiente'),(10,2,'2026-04-17 00:28:39','efectivo',500,160,'tienda','2026-04-21 19:30:00','Cancelado'),(11,NULL,'2026-04-17 00:31:28','efectivo',50,25,'Tienda','2026-04-17 00:31:28','Entregado'),(12,4,'2026-04-17 09:19:49','tarjeta',340,0,'Tienda','2026-04-23 11:20:00','Pendiente'),(13,1,'2026-04-17 20:40:06','tarjeta',1000,0,'Tienda','2026-04-20 20:43:00','Entregado'),(14,NULL,'2026-04-17 20:46:08','efectivo',500,0,'Tienda','2026-04-17 20:46:08','Entregado');
/*!40000 ALTER TABLE `venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-17 21:48:22
