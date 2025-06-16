import sqlite3
import pandas as pd
from datetime import datetime

# 连接到 SQLite 数据库
conn = sqlite3.connect('db.sqlite3')

# 定义时间范围
start_time = '2025-06-07 00:00:00'
end_time = '2025-06-11 00:00:00'

# 定义表名列表
tables = [
    'sensor_locationinf',
    'sensor_bluetoothinf',
    'sensor_accelerometerinf'
]

# 创建一个字典来存储各表的数据
data_dict = {}

# 遍历每个表并提取数据
for table in tables:
    query = f"SELECT * FROM {table} WHERE timestamp >= ? AND timestamp < ?"
    df = pd.read_sql_query(query, conn, params=(start_time, end_time))
    data_dict[table] = df

# 关闭数据库连接
conn.close()

# 将数据整合到一个 CSV 文件中
output_csv = 'extracted_data.csv'
with open(output_csv, 'w', encoding='utf-8') as f:
    for table, df in data_dict.items():
        f.write(f"--- {table} ---\n")
        df.to_csv(f, index=False, header=True)
        f.write('\n')
