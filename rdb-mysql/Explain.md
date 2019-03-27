# Explain

## 1.什么是explain

explain是Mysql的一个关键字，用来分析某条SQL语句执行过程和执行效率。

explain又叫执行计划，主要是用来查看优化器将决定如何执行查询过程，比如究竟是全表扫描还是索查询，还可以看到那种访问策略是优化器使用的，比如究竟是直接访问索引内容，还是又进行了筛选过滤，亦或者回查聚合索引等等

我们先看看一下，通过explain关键字可以获得什么信息:

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160152.png)

* id：执行编号，表示SELECT所属的行。如果SQL语句中没有子查询或者关联查询，那么id只有唯一的1，如果有子查询和关联查询，那么就会有多个id。
* select_type：标志本行是简单查询还是其他复杂查询
* table：标识本行查询是访问了哪个表
* type：标识本行查询优化器会使用什么方式进行查询，这个很重要，是我们进行分析的重点内容。
* possible_key：标识本行查询可以使用到的全部索引
* key：标识本次查询真实使用的索引，这个也很重要
* key_len：标识本次查询使用索引的长度，单位是字节数
* ref：标识使用索引查询时，使用了那种数据值进行选择，可以是常量，也可以是其余表的字段值
* row：显示本次查询会有多少行结果被影响
* Extra：一些额外信息，但也很重要


## 2.关键字分析

### 2.1.id

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160511.png)

可以看到有多子句查询的时候，id会有多个，执行顺序是从大到小，也就是说id为2的子句先执行，然后是id为1的语句执行。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160533.png)

而对于连接查询，虽然有两次查询过程，但是id都是1，因为他们是并列关系不是嵌套关系，id相等的情况下执行顺序自上至下。

### 2.2.select_type

* SIMPLE：简单查询，不包括子句和联合查询（union）
* PRIMARY：包含子查询或者联合查询，最外层标识为PRIMARY
* SUBQUERY：这个很容易理解了，就是子查询内层的子句，被标识为SUBQUERY
* DERIVED：派生表，子查询中派生出来的临时表，位于FROM的子查询中
* UNION：位于UNION中联合查询关键字后面的子句，被标记为UNION，但是如果在FROM中还是标识为DERIVED

其余都不会很常见，而且只要弄清楚意思就可以了，因为我们直接看SQL语句也是能看出来各个结构，因此这项并不是很重要。

### 2.3.table

这个就是显示从哪个表进行了本行查询。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160615.png)

还是看这张图，很清晰的显示了两次查询的是哪个表内容。

### 2.4.type（重点理解）

我们在这里建立了一个test表：

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160739.png)

表示MySQL在表中找到所需行的方式，又称“访问类型”，常见类型如下:

```
 ALL, index,  range, ref, eq_ref, const, system, NULL
```

从左到右，查询性能从最差到最好。至于什么时候会出现这些情况以及为什么出现这些情况，我们看逐一进行分析。

#### 2.4.1.ALL

全表扫描，不使用索引，在硬盘上一条一条的进行扫描。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160820.png)

可以看出，没有WERHE查询子句的情况下会使用全表扫描。同时如果WHERE子句中查询了没有建立索引的字段，也会进行全表查询。 

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160840.png)

这很容易理解，因为wu这个字段没有在任何索引中，所以要mysql安照它进行查询，那么msyql必须要一条一条的遍历表中的行，然后找出符合条件的行进行查询。

#### 2.4.2.index

index代表使用索引查询，但是遍历整个索引，和全表遍历的差别差不多，只不过读取的数据更少，效率稍微高一些。 

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-160927.png)

我们查询建立索引的字段san，可以看到使用了index_1作为索引，但是进行的是全索引的遍历。

#### 2.4.3.range

range代表使用了B-TREE索引进行了范围查询，利用了B-TREE的查询性质，查询效率比起前两种有了很大的提升。 

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-161124.png)

显而易见的索引范围扫描是带有between或者where子句里带有LIKE,<, >查询。当mysql使用索引去查找一系列值时，例如IN()和OR列表，也会显示range（范围扫描）,当然性能上面是有差异的。

#### 2.4.4.ref 和 eq_ref

使用非唯一索引进行查询某个值时是ref，很显然ref也是使用了索引查找的，而且看后面ref字段的值是const，其实和const区别不大。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-161403.png)

这种查询的效率高于range，因为首先它同样使用了B-TREE索引的性质查询，其次就是它返回的数据较少。

eq_ref和ref效率差不多，只不过eq_ref是在使用唯一索引进行查询时使用到，因此最多返回一条数据。

简单来说，就是多表连接中使用primary key或者 unique key作为关联条件


#### 2.4.5.const 和 system

使用常量进行索引查询。system是const类型的特例，当查询的表只有一行的情况下，使用system

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-161458.png)

我个人认为这种查询效率，和ref的值为const的查询应该相差无几。

#### 2.4.6.NULL 一些有趣的现象

MySQL在优化过程中分解语句，执行时甚至不用访问表或索引，例如从一个索引列里选取最小值可以通过单独索引查找完成。


一些有趣的现象
在之前索引的学习中，我们就知道聚合索引的值会存储在非聚合索引中，下面我们验证一下。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-161640.png)

id是表的主键，也就是Mysql默认的聚合索引的字段，首先对于index_1，其中的字段只有san，但是我们发现如果查询id字段，这次查询还是直接Using index（索引覆盖），索引覆盖的意思就是索引中包含你想查询的字段，这就证实了非聚合索引（index_1）中确实包含聚合索引（主键索引）的字段id。

还有就是最左前缀原则这个我提到过无数次的东西。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-162014.png)

很明显的说明了，符合最左前缀原则的查询，就可以直接使用建立的组合索引index_2（san,si)进行利用B-TREE索引的 查询

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-162030.png)

这个emmm，自行体会不符合最左前缀原则的查询，使用了index_2进行了全索引扫描，然后再一步进行WHERE条件筛选。


### 2.5.possible_keys，key

这个上面已经说的很清楚了，possible_keys是可以使用的索引，而key是实际要使用的索引。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-162134.png)

上图看到，这次查询可以使用index_1(san)，或者index_2(san,si)，但mysql优化器最终选择了index_1(san)，因为更高效开销更小。

### 2.6.ref ，rows

上面也说的很清楚了，不再这多说。

### 2.7.Extra（重点了解）


#### 2.7.1.Using index 

该值表示相应的select操作中使用了覆盖索引（Covering Index） 上面我也体到这个概念了，这个很容易理解就是直接从索引中就获得了想要的东西，没有必要进行二次查询。 

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-162248.png)

可以看出，这次查询就是索引覆盖索引的一次查询，因为id 是聚合索引的值，存在非聚集索引idnex_1中。 

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-162358.png)

#### 2.7.2.Using where 

这个有很多网上博客说的都不太清楚，其实很容易理解，Using where是指通过数据库引擎第一次查询以后，得到一个结果集，但是这个结果集不满足WHERE语句的限制，所以会Mysql会对这个结果集进行一次筛选，最后得到符合限制的数据集。

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-162436.png)

可以根据这句SQL语句进行理解，因为san,si是索引index_2的内容，所以index_2是覆盖索引（Using index）很容易理解，但是查询条件是si='y'，这时Mysql采取的手段是，遍历全索引（type:index），然后根据si='y'这个WHERE语句中的条件进行一次筛选。这就是Using where的含义

#### 2.7.3.Using temporary 

用临时表保存中间结果，常用于GROUP BY 和 ORDER BY操作中，一般看到它说明查询需要优化了，就算避免不了临时表的使用也要尽量避免硬盘临时表的使用。

#### 2.7.4.Using index condition 

这个意思是mysql会根据索引查找到的内容，作为条件进行下一次的查询操作，可以是排序查询等等操作

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-162639.png)

根据索引的内容，进行了顺序展示操作，因为id是局聚集索引，存储顺序就是索引顺序，因此不需要排序。

#### 2.7.5.Using filesort

MySQL有两种方式可以生成有序的结果，通过排序操作或者使用索引，当Extra中出现了Using filesort 说明MySQL使用了后者，但注意虽然叫filesort但并不是说明就是用了文件来进行排序，只要可能排序都是在内存里完成的。

## 3.利用有序索引获取有序数据

```SQL

CREATE TABLE `test` (  
  `id` int(11) NOT NULLAUTO_INCREMENT,  
  `rdate` datetime NOT NULL,  
  `inventid` int(11) NOT NULL,  
  `customerid` int(11) NOT NULL,  
  `staffid` int(11) NOT NULL,  
  `data` varchar(20) NOT NULL,  
  PRIMARY KEY (`id`),  
  UNIQUE KEY `rdate`(`rdate`,`inventid`,`customerid`),  
  KEY `inventid` (`inventid`),  
  KEY `customerid` (`customerid`),  
  KEY `staffid` (`staffid`)  
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1 
```

取出满足过滤条件作为排序条件的字段，以及可以直接定位到行数据的行指针信息，在 Sort Buffer 中进行实际的排序操作，然后利用排好序的数据根据行指针信息返回表中取得客户端请求的其他字段的数据，再返回给客户端.

这种方式，在使用explain分析查询的时候，显示Using index。而文件排序显示Using filesort。

注意：MySQL在查询时最多只能使用一个索引。因此，如果WHERE条件已经占用了索引，那么在排序中就不使用索引了。

### 3.1.按照索引对结果进行排序order by 使用索引是有条件

**返回选择的字段，即只包括在有选择的此列上（select后面的字段），不一定适应*的情况**)：

```SQL

mysql>   
explain select inventid from test where rdate='2011-12-1400:00:00' order by  inventid , customerid;  
+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------+

| id | select_type | table | type | possible_keys |key    | key_len |ref      | rows |Extra                    |

+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------+

|  1 |  SIMPLE      | test    |ref   |        rdate          |rdate  |      8     |const |   10   | Using where; Using index |

+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------+
```

**Select选择的列使用索引，而下面不使用索引**：

```SQL

CREATE TABLE `test` (  
  `id` int(11) NOT NULLAUTO_INCREMENT,  
  `rdate` datetime NOT NULL,  
  `inventid` int(11) NOT NULL,  
  `customerid` int(11) NOT NULL,  
  `staffid` int(11) NOT NULL,  
  `data` varchar(20) NOT NULL,  
  PRIMARY KEY (`id`),  
  UNIQUE KEY `rdate`(`rdate`,`inventid`,`customerid`),  
  KEY `inventid` (`inventid`),  
  KEY `customerid` (`customerid`),  
  KEY `staffid` (`staffid`)  
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1 
```

```SQL
mysql> explain select * from test where rdate='2011-12-14 00:00:00'order by  inventid , customerid ;

+----+-------------+-------+------+---------------+------+---------+------+------+-----------------------------+

| id | select_type | table | type | possible_keys | key     | key_len|ref     | rows | Extra                       |

+----+-------------+-------+------+---------------+------+---------+------+------+-----------------------------+

|  1 | SIMPLE      | test   | ALL  | rdate               | NULL  | NULL    |NULL |  13   |Using where;Using filesort|

+----+-------------+-------+------+---------------+------+---------+------+------+-----------------------------+
```

**只有当ORDER BY中所有的列必须包含在相同的索引，并且索引的顺序和order by子句中的顺序完全一致，并且所有列的排序方向（升序或者降序）一样才有，（混合使用ASC模式和DESC模式则不使用索引**）

```SQL
mysql>   
explain select inventid from test order byrdate, inventid ;  

+----+-------------+-------+-------+---------------+-------+---------+------+------+-------------+

| id | select_type | table | type  | possible_keys | key   | key_len | ref  | rows | Extra       |

+----+-------------+-------+-------+---------------+-------+---------+------+------+-------------+

|  1 | SIMPLE      | test  | index | NULL          | rdate |16      | NULL |   13 |Using index|

+----+-------------+-------+-------+---------------+-------+---------+------+------+-------------+
```

```SQL
mysql>   
explain select inventid from test where rdate="2011-12-16" order by  inventid ,staffid;  
+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------

| id | select_type | table | type | possible_keys |key   | key_len | ref   | rows | Extra                       |

+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------

|  1 | SIMPLE      | test | ref  | rdate         | rdate | 8       | const |    1 |Using where;Using filesort

+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------
```

由于rdate, inventid使用了同一个索引。排序使用到了索引。这个也是满足了前缀索引。但是order  by  inventid ,staffid;就不是使用了索引，因为staffid和inventid不是同一个索引

**where 语句与ORDER BY语句组合满足最左前缀**:

```SQL

mysql>   
explain select inventid from test where rdate="2011-12-16" order by  inventid ;  

+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------+

| id | select_type | table | type | possible_keys | key   | key_len | ref   | rows | Extra                    |

+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------+

|  1 | SIMPLE      | test | ref  | rdate         | rdate | 8       | const |    1 | Using where;Using index |

+----+-------------+-------+------+---------------+-------+---------+-------+------+--------------------------+
```

**如果查询联接了多个表，只有在order by子句的所有列引用的是第一个表的列才可以**。

**在其他的情况下，mysql使用文件排序  例如**：

* where语句与order by语句，使用了不同的索引
* 检查的行数过多，且没有使用覆盖索引
* ORDER BY中的列不包含在相同的索引，也就是使用了不同的索引
* 对索引列同时使用了ASC和DESC
* where语句或者ORDER BY语句中索引列使用了表达式，包括函数表达式
* where 语句与ORDER BY语句组合满足最左前缀，但where语句中使用了条件查询。查见第10句,虽然where与order by构成了索引最左有缀的条件，但是where子句中使用的是**条件查询(>)**。

```SQL
mysql> explain select inventid from test where  rdate>"2011-12-16" order by  inventid;

+----+-------------+-------+-------+---------------+-------+---------+------+------+----------------

| id | select_type | table | type  | possible_keys | key   | key_len | ref  | rows | Extra                                    

+----+-------------+-------+-------+---------------+-------+---------+------+------+----------------

|  1 |SIMPLE      | test  | range | rdate         | rdate | 8       | NULL |    1 | Using where; Using index;Usingfilesort|

+----+-------------+-------+-------+---------------+-------+---------+------+------+----------------
```


**当使用left join，使用右边的表字段排序**

## 4.文件排序

这个 filesort 并不是说通过磁盘文件进行排序，而只是告诉我们进行了一个排序操作。即在MySQL Query Optimizer 所给出的执行计划(通过 EXPLAIN 命令查看)中被称为文件排序（filesort）

文件排序是通过相应的排序算法,将取得的数据在内存中进行排序: MySQL需要将数据在内存中进行排序，所使用的内存区域也就是我们通过sort_buffer_size 系统变量所设置的排序区。这个排序区是每个Thread 独享的，所以说可能在同一时刻在MySQL 中可能存在多个 sort buffer 内存区域。

在MySQL中filesort 的实现算法实际上是有两种：

双路排序：是首先根据相应的条件取出相应的排序字段和可以直接定位行数据的行指针信息，然后在sort buffer 中进行排序。

单路排序：是一次性取出满足条件行的所有字段，然后在sort buffer中进行排序。

在MySQL4.1版本之前只有第一种排序算法双路排序，第二种算法是从MySQL4.1开始的改进算法，主要目的是为了减少第一次算法中需要两次访问表数据的 IO 操作，将两次变成了一次，但相应也会耗用更多的sortbuffer 空间。当然，MySQL4.1开始的以后所有版本同时也支持第一种算法，

MySQL主要通过比较我们所设定的系统参数 max_length_for_sort_data的大小和Query 语句所取出的字段类型大小总和来判定需要使用哪一种排序算法。如果 max_length_for_sort_data更大，则使用第二种优化后的算法，反之使用第一种算法。所以如果希望 ORDER BY 操作的效率尽可能的高，一定要主义max_length_for_sort_data 参数的设置。曾经就有同事的数据库出现大量的排序等待，造成系统负载很高，而且响应时间变得很长，最后查出正是因为MySQL 使用了传统的第一种排序算法而导致，在加大了max_length_for_sort_data 参数值之后，系统负载马上得到了大的缓解，响应也快了很多。


### 4.1.MySQL 需要使用filesort 实现排序的实例

假设有 Table A 和 B 两个表结构分别如下：

```SQL
# mysql

>show create table A\G
 　　*************************** 1. row ***************************
 　　Table: A
 　　Create Table: CREATE TABLE `A` (
 　　`id` int(11) NOT NULL default '0',
  　 `c2` char(2) default NULL,
 　　`c3` varchar(16) default NULL, 
 　　`c4` datetime default NULL, 
 　　PRIMARY KEY (`id`) 
 　　) ENGINE=MyISAM DEFAULT CHARSET=utf8

#:mysql

> show create table B\G
 　　*************************** 1. row ***************************  　　Table: B
 　　Create Table: CREATE TABLE `B` ( 
 　　`id` int(11) NOT NULL default '0', 
 　　`c2` char(2) default NULL,
 　　`c3` varchar(16) default NULL, 
 　　PRIMARY KEY (`id`),

 　　KEY `B_c2_ind` (`c2`)
 　　) ENGINE=MyISAM DEFAULT CHARSET=utf8
```

A.c2不是索引将使用：

```java
sky@localhost : example 01:54:23> EXPLAIN SELECT A.* FROM A,B WHERE A.id >2 AND A.c2 <5 AND A.c2 = B.c2 ORDER BY A.c2\G

　　*************************** 1. row ***************************
　　id: 1
　　select_type: SIMPLE
　　table: A
　　type: range
　　possible_keys: PRIMARY
　　key: PRIMARY
　　key_len: 4
　　ref: NULL
　　rows: 3
　　Extra: Using where; Using filesort

 

*************************** 2. row ***************************
　　id: 1
　　select_type: SIMPLE
　　table: B
　　type: ref
　　possible_keys: B_c2_ind
　　key: B_c2_ind
　　key_len: 7
　　ref: example.A.c2
　　rows: 2
　　Extra: Using where; Using index
```

MySQL 从 Table A 中取出了符合条件的数据，由于取得的数据并不满足 ORDER BY 条件，所以 MySQL 进行了 filesort 操作，其整个执行过程如下图所示：

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-170148.png)

### 4.2.MySQL 需要使用Using temporary 临时表来filesort

如果order by的子句只引用了联接中的第一个表，MySQL会先对第一个表进行排序，然后进行联接。也就是expain中的Extra的Using Filesort.否则MySQL先把结果保存到临时表(Temporary Table),然后再对临时表的数据进行排序.此时expain中的Extra的显示Using temporary Using Filesort.

例如如果我们的排序数据如果是两个(或者更多个) Table 通过 Join所得出的,如下例所示：

```SQL
sky@localhost : example 02:46:15> explain select A.* from A,B
where A.id > 2 and A.c2 < 5 and A.c2 = B.c2 order by B.c3\G

　　*************************** 1. row***************************

　　id: 1
  　select_type: SIMPLE
　　table: A
　　type: range
　　possible_keys: PRIMARY
　　key: PRIMARY
　　key_len: 4
　　ref: NULL
  　rows: 3

Extra: Using where; Using temporary; Using filesort

　　*************************** 2. row ***************************
　　id: 1
　　select_type: SIMPLE
　　table: B

　　type: ref
　　possible_keys: B_c2_ind
　　key: B_c2_ind
　　key_len: 7
　　ref: example.A.c2
　　rows: 2
　　Extra: Using where
```

实际执行过程应该是如下图所示：

![image](https://clsaa-markdown-imgbed-1252032169.cos.ap-shanghai.myqcloud.com/very-java/2019-03-27-170415.png)

## 4.优化Filesort

当无法避免排序操作时，又该如何来优化呢？很显然，应该尽可能让 MySQL 选择使用第二种单路算法来进行排序。这样可以减少大量的随机IO操作，很大幅度地提高排序工作的效率。

1. 加大 max_length_for_sort_data 参数的设置

在 MySQL 中，决定使用老式排序算法还是改进版排序算法是通过参数 max_length_for_sort_data 来决定的。当所有返回字段的最大长度小于这个参数值时，MySQL 就会选择改进后的排序算法，反之，则选择老式的算法。所以，如果有充足的内存让MySQL 存放须要返回的非排序字段，就可以加大这个参数的值来让 MySQL 选择使用改进版的排序算法。

2. 去掉不必要的返回字段

当内存不是很充裕时，不能简单地通过强行加大上面的参数来强迫 MySQL 去使用改进版的排序算法，否则可能会造成 MySQL 不得不将数据分成很多段，然后进行排序，这样可能会得不偿失。此时就须要去掉不必要的返回字段，让返回结果长度适应 max_length_for_sort_data 参数的限制。

3. 增大 sort_buffer_size 参数设置

增大 sort_buffer_size 并不是为了让 MySQL选择改进版的排序算法，而是为了让MySQL尽量减少在排序过程中对须要排序的数据进行分段，因为分段会造成 MySQL 不得不使用临时表来进行交换排序。

