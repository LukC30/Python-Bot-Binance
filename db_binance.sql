create database db_binance;
use db_binance;

create table tbl_users(
id int unsigned auto_increment primary key,
api_key varchar(100) not null,
api_secret varchar(100) not null,
constraint unique (api_key),
constraint unique (api_secret)


);


create table tbl_order(
id int auto_increment primary key,
api_key varchar(100),
ativo varchar(20) not null,
tipo_de_ordem enum ('BUY', 'SELL'),
valor_depositado decimal(7,6) not null,
ultimo_alvo decimal(7,6) not null,
ativa enum('n', 's'),
order_id varchar(100)


);

select * from tbl_order;

#drop database db_binance;
