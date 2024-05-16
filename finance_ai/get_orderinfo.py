import requests
import pandas as pd

def fetch_orders(dateType, startDate, endDate):
    url = "https://disapi.zyxtravel.com/in-service/ai/orders"
    payload = {
        "dateType": dateType,
        "startDate": startDate,
        "endDate": endDate
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print(f"Sending request to {url} with payload: {payload}")
    
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Received response with status code: {response.status_code}")
    
    if response.status_code == 200:
        response_json = response.json()
        #print(f"Response JSON: {response_json}")
        return response_json
    else:
        print(f"Error: Received status code {response.status_code}")
        response.raise_for_status()

def export_to_files(data, csv_file, xlsx_file):
    df = pd.DataFrame(data)
    
    #print(f"Exporting data to {csv_file} and {xlsx_file}")
    
    # Export to CSV
    df.to_csv(csv_file, index=False)
    
    # Export to Excel
    df.to_excel(xlsx_file, index=False)

def main():
    #dateType:1-按照订单创建时间查询，2-按照checkIn查询
    dateType = "1"
    startDate = "2024-05-06 00:00:00"
    endDate = "2024-05-14 00:00:00"
    
    try:
        data = fetch_orders(dateType, startDate, endDate)
        if data:  # 直接检查返回的数据是否为空
            #print(f"Orders data: {data}")
            export_to_files(data, 'orders3.csv', 'orders3.xlsx')
            print("Data has been successfully exported to orders.csv and orders.xlsx")
        else:
            print("No data found in the response.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
