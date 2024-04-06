
# CSV 工具集
# 最后更新 ： 2024.03.14 17:42
# step1 : 提取指定资源的酒店列表
# step2 : 用 1 列表找到 zyx hotel code ，并列出所有zyx酒店信息
# 

from csv_rules import read_excel, read_csv, save_csv, filter_and_export_csv, convert_csv_to_xlsx, process_csv, filter_and_export_csv, zyx_all_room_check_csv
import time
from tqdm import tqdm
import pandas as pd
import os

# 打印当前工作目录
print(os.getcwd())

# 更改当前工作目录
# os.chdir('/path/to/your/directory')

win_file = r'D:\Gfile\mapping28\csv\data\\'  # 文件夹路径
def main():
    while True:
        print("\n可用操作：")
        print("1 - HOTEL: 导入供应商酒店数据，确认与ZYX的聚合关系。")
        print("2 - HOTEL: 通过step1的聚合关系，进一步找到ZYX的酒店基础信息，并排列到一起")
        print("3 - ROOM：确认母房型不为空的房型，导出csv文件")
        print("4 - ROOM : 临时需求，导入的CSV 排序好后输出XLSX")
        print("5 - HOTEL: 用step2完成的数据查找，名称，地址相似度，经纬度距离，邮编是否一致")
        print("6 - HOTEL: 导出2个csv文件。名称100%,距离小于100米，邮编一样的OK，剩余的check")
        print("7 - ROOM : 导入全部房型文件csv；分3个csv出来")
        #  1, 全部正确房型 名称一样，最大入住人数母房型不大于子房型，面积属性一样（没有或数字一样），床型一样（考虑 others=other等逻辑),床数量一样，吸烟属性一样
        #  2, 除了正确之外的所有房型，标注是哪里有问题，名称不一样就输出 False,面积，床型，床数量，吸烟属性等，都用 TRUE，FALSE 表示
        #  3, 没有母房型的所有房型
        print("q - 退出程序")
        choice = input("请选择一个操作（1/2/3/q）：")

        if choice == '1':
            step1()
        elif choice == '2':
            step2()
        elif choice == '3':
            step3()
        elif choice == '4':
            step4()
        elif choice == '5':
            step5()
        elif choice == '6':
            step6()
        elif choice == '7':
            step7()
        elif choice == 'q' or choice == 'Q':
            print("退出程序")
            break
        else:
            print("无效输入，请重新选择。")

# 导入所有ZYZ酒店对照表，xlsx
# 导入所有zyx酒店列表 csv 

def step1(): # 导入并合并后导出程序
    print("执行步骤 1...")
  
    start_time = time.time()
    print("程序开始执行")
    # 读取数据
    df_zyxallcsv = read_csv(win_file + 'zyxAllHotel_0314v2.csv')
    df_jalan = read_excel(win_file + 'zyx_all_hotel0314.xlsx', sheet_name='jalan_hotel')
    df_jtb = read_excel(win_file + 'zyx_all_hotel0314.xlsx', sheet_name='jtb_hotel')
    df_rtx = read_excel(win_file + 'zyx_all_hotel0314.xlsx', sheet_name='rtx_hotel')
    df_ynj = read_excel(win_file + 'zyx_all_hotel0314.xlsx', sheet_name='yanolja_hotel')
    mapping_df = read_excel(win_file + 'zyx_all_hotel0314.xlsx', sheet_name='mapping')
    
    # 准备数据
    # rtx
    df_excel_renamed_rtx = df_rtx.rename(columns={
        'hotelId': 'rtx-hotelid',
        'name': 'sup_name',
        'address': 'sup_add',
        'postal_code': 'sup_post',
        'latitude': 'sup_long',
        'longitude': 'sup_lat'
    })
    df_mapping_filtered_rtx = mapping_df[mapping_df['channel'] == 'M122031274'] # RTX
    
    # 准备数据
    # jalan
    df_excel_renamed_jalan = df_jalan.rename(columns={
        'hotelId': 'jalan-hotelid',
        'hotelNameEnglish': 'sup_name',
        'addressEnglish': 'sup_add',
        'postalCode': 'sup_post',
        'latitudeW': 'sup_lat',
        'longitudeW': 'sup_long'
    })
    df_mapping_filtered_jalan = mapping_df[mapping_df['channel'] == 'M121111273'] # JALAN
    
    # 准备数据
    # yanolja
    df_excel_renamed_ynj = df_ynj.rename(columns={
        'hotelId': 'ynj-hotelid',
        'name': 'sup_name',
        'address': 'sup_add',
        'postalCode': 'sup_post',
        'latitude': 'sup_lat',
        'longitude': 'sup_long'
    })
    df_mapping_filtered_ynj = mapping_df[mapping_df['channel'] == 'M122031275'] # Yanolja
    
    # 准备数据
    # jtb
    df_excel_renamed_jtb = df_jtb.rename(columns={
        'SupplierCode': 'jtb-hotelid',
        'SupplierName': 'sup_name',
        'Address2': 'sup_add',
        'PostCode': 'sup_post',
        'Latitude': 'sup_lat',
        'Longitude': 'sup_long'
    })
    df_mapping_filtered_jtb = mapping_df[(mapping_df['channel'] == 'M123121297') | (mapping_df['channel'] == 'M122091278')] # jtb

    # 合并数据 检查 columns
    print(df_excel_renamed_rtx.columns)
    print(df_excel_renamed_jalan.columns)
    print(df_excel_renamed_jtb.columns)
    print(df_excel_renamed_ynj.columns)
    
    # 对于 RTX
    result_df_rtx = df_excel_renamed_rtx.merge(df_mapping_filtered_rtx[['out_hotel_code', 'hotel_code']], how='left', left_on='rtx-hotelid', right_on='out_hotel_code')
    rtx_columns = ['rtx-hotelid','sup_name','sup_add','sup_post','sup_lat','sup_long','out_hotel_code','hotel_code']
    result_df_rtx = result_df_rtx[rtx_columns]
    
    # 对于 Jalan
    result_df_jalan = df_excel_renamed_jalan.merge(df_mapping_filtered_jalan[['out_hotel_code', 'hotel_code']], how='left', left_on='jalan-hotelid', right_on='out_hotel_code')
    jalan_columns = ['jalan-hotelid', 'sup_name','sup_add','sup_post','sup_lat','sup_long','out_hotel_code','hotel_code']
    result_df_jalan = result_df_jalan[jalan_columns]
    
    # 对于 JTB
    result_df_jtb = df_excel_renamed_jtb.merge(df_mapping_filtered_jtb[['out_hotel_code', 'hotel_code']], how='left', left_on='jtb-hotelid', right_on='out_hotel_code')
    jtb_columns = ['jtb-hotelid','sup_name','sup_add','sup_post','sup_lat','sup_long','out_hotel_code','hotel_code']
    result_df_jtb = result_df_jtb[jtb_columns]
    
    # 对于 YNJ
    result_df_ynj = df_excel_renamed_ynj.merge(df_mapping_filtered_ynj[['out_hotel_code', 'hotel_code']], how='left', left_on='ynj-hotelid', right_on='out_hotel_code')
    ynj_columns = ['ynj-hotelid','sup_name','sup_add','sup_post','sup_lat','sup_long','out_hotel_code','hotel_code']
    result_df_ynj = result_df_ynj[ynj_columns]
    
    # 合并后，检查结果 DataFrame
    #print("合并后的 JTB 数据行数:", len(result_df_jtb))
    
    # 保存数据到 CSV
    save_csv(result_df_rtx, win_file + 'RTXmaping_check0317.csv')
    print("RTXmaping_check0317.csv 文件已创建。")
    
    save_csv(result_df_jalan, win_file + 'Jalanmaping_check0317.csv')
    print("Jalanmaping_check0317.csv 文件已创建。")
    
    save_csv(result_df_jtb, win_file + 'JTBmaping_check0317.csv')
    print("JTBmaping_check0317.csv 文件已创建。")
    
    save_csv(result_df_ynj, win_file + 'YNJmaping_check0317.csv')
    print("YNJmaping_check0317.csv 文件已创建。")
    
    end_time = time.time()
    print(f"程序执行结束，总耗时 {end_time - start_time:.2f} 秒")
    
    print("步骤 1 完成")
    input("按回车键继续...")
    

# step1 找到的 hotel code 一样的
# 排序对比内容

def step2(): # 用step1 找到hotel code 一样的
    start_time = time.time()
    print("执行步骤 2...")
    
    # ZYX 所有酒店 csv
    all_hotel_df = pd.read_csv(win_file + 'zyxAllHotel_0314v2.csv', sep='\t')
    # rtx 整理
    rtx_df = pd.read_csv(win_file + 'RTXmaping_check0317.csv')
    # jalan 整理
    jalan_df = pd.read_csv(win_file + 'Jalanmaping_check0317.csv')
    # jtb 整理
    jtb_df = pd.read_csv(win_file + 'JTBmaping_check0317.csv')
    # jtb 整理
    ynj_df = pd.read_csv(win_file + 'YNJmaping_check0317.csv')

    # 查找匹配的 hotel_code 并合并数据
    merged_df_rtx = pd.merge(rtx_df, all_hotel_df, how='left', left_on='hotel_code', right_on='zyx-hotelid')
    merged_df_jalan = pd.merge(jalan_df, all_hotel_df, how='left', left_on='hotel_code', right_on='zyx-hotelid')
    merged_df_jtb = pd.merge(jtb_df, all_hotel_df, how='left', left_on='hotel_code', right_on='zyx-hotelid')
    merged_df_ynj = pd.merge(ynj_df, all_hotel_df, how='left', left_on='hotel_code', right_on='zyx-hotelid')

    # 打印合并后的 DataFrame 的前几行以检查结果
    #print(merged_df.head())

    # 继续执行其他操作...
    # 当准备好保存新的 CSV 文件时
    merged_df_rtx.to_csv(win_file + 'RTXmaping_check0317_step2.csv', index=False)
    print("RTXmaping确认文件已创建")
    merged_df_jalan.to_csv(win_file + 'JALANmaping_check0317_step2.csv', index=False)
    print("JALANmaping确认文件已创建")
    merged_df_jtb.to_csv(win_file + 'JTBmaping_check0317_step2.csv', index=False)
    print("JTBmaping确认文件已创建")
    merged_df_ynj.to_csv(win_file + 'YNJmaping_check0317_step2.csv', index=False)
    print("YNJmaping确认文件已创建")

    end_time = time.time()
    print(f"程序执行结束，总耗时 {end_time - start_time:.2f} 秒")
    print("步骤 2 完成")
    input("按回车键继续...")
 
# 输入一个房型csv文件，确认母房型不为空的数量，并导出函数 
def step3():
    print("执行步骤 3...")
    input_csv_path = win_file + 'jpRoomType_0310v2.csv'  # 日本全部房型
    output_csv_path = win_file + 'RtxRoom_check0314.csv'  # Rtx房型确认
    filter_and_export_csv(input_csv_path, output_csv_path)
    print("房型数量确认 完成")
    input("按回车键继续...")
    
#一个临时操作一个酒店房型
#从csv 导出标准格式 original_sep='\t' 到一个 xlsx文件
def step4():
    print("执行步骤 4...")
    # 这里放置步骤 4 的代码

    convert_csv_to_xlsx(win_file + 'JP20093_room.csv', win_file + 'JP20093_roomX.xlsx', original_sep='\t')
   
    print("完成步骤 4...")
    input("按回车键继续...")
    
# 导入 step2文件
# 对比名称，地址相似度，经纬度距离，邮编是否一致
# 导出csv文件
def step5():
    print("执行步骤 5...")
    # 这里放置步骤 4 的代码
    time.sleep(1)  # 模拟耗时操作
    # 使用示例
    process_csv(win_file + 'RTXmaping_check0317_step2.csv', win_file + 'RTXmaping_end0317_step5.csv')
    print("已创建RTX对比文件")
    process_csv(win_file + 'JALANmaping_check0317_step2.csv', win_file + 'JALANmaping_end0317_step5.csv')
    print("已创建JALAN对比文件")
    process_csv(win_file + 'JTBmaping_check0317_step2.csv', win_file + 'JTBmaping_end0317_step5.csv')
    print("已创建JTB对比文件")
    process_csv(win_file + 'YNJmaping_check0317_step2.csv', win_file + 'YNJmaping_end0317_step5.csv')
    print("已创建YNJ对比文件")
    
    print("完成步骤 5...")
    input("按回车键继续...")

# 处理 step5 导出的文件
# 分组 1 ：名称 100% 一样，地址小于100米，POST是 True 分为 一组
# 分组 2 ： 其余的 1组，必须人工审核
def step6():
    print("执行步骤 6...")
    # 这里放置步骤 4 的代码
    
    # 处理 RTX
    filter_and_export_csv(win_file + 'RTXmaping_end0317_step5.csv', win_file + 'RTX_hotel_ok_list.csv', win_file + 'RTX_hotel_check_list.csv')
    print("RTX hotel 处理完毕")
    # 处理 jalan
    filter_and_export_csv(win_file + 'JALANmaping_end0317_step5.csv', win_file + 'JALAN_hotel_ok_list.csv', win_file + 'JALAN_hotel_check_list.csv')
    print("JALAN hotel 处理完毕")
    # 处理 JTB
    filter_and_export_csv(win_file + 'JTBmaping_end0317_step5.csv', win_file + 'JTB_hotel_ok_list.csv', win_file + 'JTB_hotel_check_list.csv')
    print("JTB hotel 处理完毕")
    # 处理 YNJ
    filter_and_export_csv(win_file + 'YNJmaping_end0317_step5.csv', win_file + 'YNJ_hotel_ok_list.csv', win_file + 'YNJ_hotel_check_list.csv')
    print("YNJ hotel 处理完毕")
    
    print("完成步骤 6...")
    input("按回车键继续...")
    
#导入全部房型文件csv；分3个csv出来
def step7():
    print("执行步骤 7...")
    # 这里放置步骤 7 的代码
    zyx_all_room_check_csv(win_file + 'kr_jp_room_44w.csv', win_file + 'ok_room.csv', win_file + 'check_room.csv', win_file + 'no_mather_room.csv')
    
    print("完成步骤 7...")
    input("按回车键继续...")
    
if __name__ == "__main__":
    main()
