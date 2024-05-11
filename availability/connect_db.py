from pymongo import MongoClient
from bson.json_util import dumps
import csv
from datetime import datetime, timedelta
import pprint  # 导入pprint模块

#------------------------连接到数据库验证部分--------------------------#
# 从库地址列表
secondary_addresses = [
    'mongodb://172.17.1.82:27017',
    'mongodb://172.17.1.83:27017'
]

# 主库地址
primary_address = 'mongodb://172.17.1.81:27017'

# 连接到主库
client = MongoClient(primary_address, replicaSet='zyx-mrs01', readPreference='secondaryPreferred')

# 连接数据库
db = client.hotel_data

# 连接数据表
collection = db.yanolja_hotel

# 打印连接成功信息
print("成功连接到 ZYX MongoDB")

# 打印连接数据表成功信息
print("成功获得 yanolja_hotel 数据表")

# 打印数据表中的所有文档数量
doc_count = collection.count_documents({})
print("yanolja_hotel 数据表总数据量: :", doc_count)

# 打印数据表中的列头和属性
sample_doc = collection.find_one({})
print("yanolja_hotel数据表列头信息:")
for key in sample_doc.keys():
    print("-", key)

# 打印最早和最晚的数据时间
earliest_doc = collection.find_one({}, sort=[('_id', 1)])
latest_doc = collection.find_one({}, sort=[('_id', -1)])
print("数据表的最初数据时间:", earliest_doc['_id'].generation_time)
print("数据表的最后数据时间:", latest_doc['_id'].generation_time)
input("回车继续")





#------------------------获取1分钟请求数据，导出到csv--------------------------#

# MongoDB连接信息
primary_address = 'mongodb://172.17.1.91:27017'
secondary_addresses = [
    'mongodb://172.17.1.92:27017',
    'mongodb://172.17.1.93:27017'
]
database_name = 'cache_hotel_data'

# 连接到 MongoDB
client = MongoClient(primary_address, replicaSet='zyx-mrs-g2', readPreference='secondaryPreferred')
db = client[database_name]
print("成功连接到数据库:", database_name)

# 执行查询获取最近的100条数据
cursor = db['zyx_api_search_monitor'].find().sort('_id', -1).limit(10000)
documents = list(cursor)

# 获取字段名列表
fieldnames = set()
for document in documents:
    fieldnames.update(document.keys())

# 导出到CSV文件
csv_output_path = 'recent_search_results.csv'
with open(csv_output_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for document in documents:
        writer.writerow(document)

print("最近的100条数据已导出到CSV文件:", csv_output_path)


input("回车继续")



#------------------------获取YNJ的数据，导出到csv--------------------------#

# 连接到数据库和数据表
hotel_collection = db.yanolja_hotel
price_stock_collection = db.yanolja_price_stock

# 获取hotelId值
hotel_ids = hotel_collection.distinct('hotelId')

# 将hotelId导出到CSV文件
csv_file_path = 'hotel_ids.csv'
with open(csv_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['hotelId'])
    for hotel_id in hotel_ids:
        writer.writerow([hotel_id])
print("hotelId导出到CSV文件成功:", csv_file_path)

# 从CSV文件读取hotelId值
hotel_ids = []
with open(csv_file_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # 跳过表头
    for row in reader:
        hotel_ids.append(row[0])

# 获取三个酒店的所有数据并导出到CSV文件
csv_data = []
for hotel_id in hotel_ids[:10]:  # 获取前X个酒店的数据
    hotel_data = price_stock_collection.find({'hotelId': hotel_id})
    for data in hotel_data:
        csv_data.append(data)

# 导出到CSV文件
csv_output_path = 'hotel_data.csv'
with open(csv_output_path, 'w', newline='') as csvfile:
    fieldnames = csv_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in csv_data:
        writer.writerow(data)
print("酒店数据导出到CSV文件成功:", csv_output_path)