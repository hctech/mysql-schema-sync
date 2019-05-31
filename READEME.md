同步 MySQL Schema 工具



## 使用说明

1. git clone code

2. 安装依赖

   ```
   pip install pymysql
   ```

3. 运行同步脚本

   ```
   python sync_mysql_schema.py [options] <source> <target>
   
   # source: 源数据库连接 mysql://user:pass@host:port/database
   # target: 目标数据库连接 mysql://user:pass@host:port/database
   # options:
   #      -a: sync the AUTO_INCREMENT value for eache table.
   #      -c: sync the COMMENT field for all tables AND columns. 
   ```