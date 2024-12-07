import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from Storm_Data import StormData
import pandas as pd

class CrawlData:
    def __init__(self, storm_data):
        self.storm_data = storm_data
        
    
    #lấy ảnh vệ tinh và ảnh đường đi của bão từ trên web xuống    
    def get_storm_roads(self) :
        ids = []
        for i in range(2010,2021):
           ids += self.storm_data.get_id(i)
           
        for id in ids:
            url = f"https://ncics.org/ibtracs/index.php?name=v04r00-{id}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            link_tag = soup.find('img', attrs={'alt': "Satellite image near maximum intensity"})
            if link_tag is not None:  # Kiểm tra xem link_tag có phải là None không
                response1 = requests.get("https://ncics.org/ibtracs/" + link_tag['src'])
                # Kiểm tra nếu tải thành công
                if response1.status_code == 200:
                    # Mở ảnh từ dữ liệu tải về
                    img = Image.open(BytesIO(response1.content))
                    
                    file_name = f"{id}.png"  # Sử dụng id làm tên file
                    img.save("C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Hình ảnh bão\\" + file_name)
                else:
                    print(f"Không thể tải ảnh. Mã lỗi: {response1.status_code}")
            else:
                path = "C:\\Users\\linhn\\Pictures\\Screenshots\\Screenshot 2024-12-06 233341.png"
                img = Image.open(path)
                    
                file_name = f"{id}.png"  # Sử dụng id làm tên file
                img.save("C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Hình ảnh bão\\" + file_name)
        
    #lấy tên và dạng bão từ trên web xuống        
    def get_storm_name_and_type(self):
        data = []
        ids = []
        for i in range(2010,2021):
           ids += self.storm_data.get_id(i)

        for id in ids:
            url = f"https://ncics.org/ibtracs/index.php?name=v04r00-{id}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Lấy tên bão và phân loại
            storm_name_tag = soup.find('h1')
            storm_name_full = storm_name_tag.text.strip()  # Lấy toàn bộ nội dung của thẻ <h1>
            storm_name = storm_name_full.split(' ')[len(storm_name_full.split(' '))-3]  # Lấy tên trước dấu ngoặc
            storm_type = " ".join(storm_name_full.split(' ')[1:len(storm_name_full.split(' '))-3])  # Lấy phân loại từ nội dung

            # Thêm dữ liệu vào danh sách
            data.append([id, storm_name, storm_type])

        # Tạo DataFrame từ danh sách dữ liệu
        df = pd.DataFrame(data, columns=['ID', 'Tên cơn bão', 'Phân loại'])

        # Xuất DataFrame thành file CSV
        df.to_csv('C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Tên và Phân loại\\storm_data.csv', index=False, encoding='utf-8-sig')

        print("Đã xuất dữ liệu thành công vào file 'storm_data.csv'.")      
def main():
    positive_dir = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\POSITIVE"
    negative_dir = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\PastDomain"
    storm_data = StormData(positive_dir, negative_dir)

    crawler = CrawlData(storm_data)
    
    crawler.get_storm_name_and_type()

# Gọi hàm main
if __name__ == "__main__":
    main()            