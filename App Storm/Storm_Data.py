import xarray as xr
import math
import numpy as np
import os
import pandas as pd


#danh sách các biến khí tượng và ý nghĩa
variables = {
    "EPV": "Áp suất hơi nước ",
    "H": "Độ ẩm tương đối",
    "O3": "Ozone",
    "OMEGA": "Tốc độ chìm của không khí ",
    "PHIS": "Tiềm năng nhiệt động ",
    "PS": "Áp suất tại mặt đất ",
    "QI": "Độ ẩm đặc hiệu ",
    "QL": "Độ ẩm lỏng ",
    "QV": "Độ ẩm hơi nước ",
    "RH": "Độ ẩm tương đối ",
    "SLP": "Áp suất mặt biển",
    "T": "Nhiệt độ",
    "U": "Thành phần gió theo hướng Đông - Tây ",
    "V": "Thành phần gió theo hướng Bắc - Nam "
}

storm_classification = {
    "Tropical Depression": "Cơn bão nhiệt đới",
    "Tropical Storm": "Bão nhiệt đới",
    "Severe Tropical Storm": "Bão nhiệt đới mạnh",
    "Typhoon": "Bão",
    "Super Typhoon": "Bão siêu mạnh",
    "Cyclonic Storm": "Bão xoáy",
    "Severe Cyclonic Storm": "Bão xoáy mạnh",
    "Subtropical Depression": "Cơn bão cận nhiệt đới",
    "Very Severe Cyclonic Storm": "Bão xoáy rất mạnh"
}

class StormData:
    def __init__(self, positive_dir, negative_dir):
        self.positive_dir = positive_dir
        self.negative_dir = negative_dir


    #hàm này lấy dánh sách các id của các cơn bão trong một năm
    def get_id(self, year):
        """Lấy danh sách các cơn bão trong năm."""
        positive_files = [f for f in os.listdir(self.positive_dir) if f.startswith(f'POSITIVE_{year}')]
        storm_ids = [f[9:22] for f in positive_files]
        return storm_ids


    #hàm này lấy các file negative của id cơn bão đã được chọn
    def get_negative(self, storm_id):
        """Hiển thị các thời điểm trước bão cơn bão."""
        negative_files = [f for f in os.listdir(self.negative_dir) if f.startswith(f'NEGATIVE_{storm_id}')]
        return negative_files
    
    
    #hàm này để mở và đọc dữ liệu file có định dạng .nc
    def load_data(self, file_path):
        """Load dữ liệu từ file NetCDF."""
        return xr.open_dataset(file_path)
    
    
    #hàm này lấy danh sách các mốc thời gian cho đến khi bão được hình thành
    def get_time(self, storm_id):
        positive_path = [f for f in os.listdir(self.positive_dir) if f.startswith(f'POSITIVE_{storm_id}')][0]
        negative_paths = self.get_negative(storm_id)
        ds = self.load_data(os.path.join(self.positive_dir, positive_path))
        time = ds.time.values
        ans_time = []
        for path in negative_paths:
            ds1 = self.load_data(os.path.join(self.negative_dir, path))
            ans_time.append(((time - ds1.time.values) / (3.6 * 10 ** 12)).astype(int))
        ans_time.sort()
        return ans_time
    

    
    #hàm này tạo 1 dataframe chứa các thông tin của các cơn bão
    def storms_infomation(self, year):
        storms_id = self.get_id(year)
        storm_data = []
        
        for id in storms_id:
            day_of_year = int(id[4:7])
            latitude = int(id[8:10])
            longitude = int(id[10:13])
            
            #lấy ra tên và phân loại cơn bão
            file_path = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Tên và Phân loại\\storm_data.csv"  # Thay thế bằng đường dẫn tới file CSV của bạn
            df = pd.read_csv(file_path)
            result = df[df['ID'] == id]
            name = result['Tên cơn bão'].values[0]
            type =storm_classification[result['Phân loại'].values[0]]
            
            positive_path = [f for f in os.listdir(self.positive_dir) if f.startswith(f'POSITIVE_{id}')][0]
            ds = self.load_data(os.path.join(self.positive_dir, positive_path))
            time = ds.time.values # Giả sử time là một mảng, có thể cần xử lý thêm
            
            storm_data.append({
                'Số thứ tự': len(storm_data) + 1,
                'ID':id,
                'Tên bão' :name,
                'Phân loại':type,
                'Ngày xuất hiện(1 - 365)': day_of_year,
                'Vĩ độ': latitude,
                'Kinh độ': longitude,
                'Thời gian': time
            })
            
        storm_table = pd.DataFrame(storm_data)
        return storm_table
    
    
    #hàm này tạo 1 dataframe chứa thông tin các biến khí tượng
    def list_variable(self,year):
        storm_ids = self.get_id(year)
        storm_id = storm_ids[0]
        list = []
        positive_path = [f for f in os.listdir(self.positive_dir) if f.startswith(f'POSITIVE_{storm_id}')][0]
        ds = self.load_data(os.path.join(self.positive_dir, positive_path))
        for var in ds.data_vars:
            list.append({
                'Số thứ tự': len(list) + 1,
                'Tên biến': var,
                'Ý nghĩa' :variables[var]
            })
        list_table = pd.DataFrame(list)
        return list_table
    
    
    #hàm này tạo 1 dataframe chứa danh sách các file negative ứng với id cơn bão đã được chọn
    def list_negative(self, id):
        negative_path = [f for f in os.listdir(self.negative_dir) if f.startswith(f'NEGATIVE_{id}')]
        negative_path = [s.strip() for s in negative_path]
        sorted_list = sorted(negative_path, key=lambda x: int(x.split('_')[2]))
        
        list = []
        for path in sorted_list:
            list.append({
                'Số thứ tự': len(list) + 1,
                'Tên file' : path
            })
        negative_table = pd.DataFrame(list)
        return negative_table
    
    #hàm này trả về 1 list chứa các đường dẫn đến các file ảnh vệ tinh và ảnh đường đi
    def list_path_image(self,storm_ids):
        image_paths = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Hình ảnh bão"
        image_roads = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Đường đi của bão"
        
        list = []
        
        for id in storm_ids:
            image = [f for f in os.listdir(image_paths) if f.startswith(f'{id}')][0]
            image_path =  os.path.join(image_paths, image)
            list.append(image_path)
            road = [f for f in os.listdir(image_roads) if f.startswith(f'{id}')][0]
            image_road =  os.path.join(image_roads, road)
            list.append(image_road)
        return list
    
    
    #hàm này trả về tên 1 cơn bão khi biết id
    def get_name(self,id):
        file_path = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Tên và Phân loại\\storm_data.csv"  # Thay thế bằng đường dẫn tới file CSV của bạn
        df = pd.read_csv(file_path)
        # Tìm kiếm trong DataFrame
        result = df[df['ID'] == id]
        if not result.empty:
            return result['Tên cơn bão'].values[0]  # Trả về tên cơn bão
        else:
            return "ID không tồn tại"
    
    
    #hàm này trả về dạng của 1 cơn bão khi biết đường đi    
    def get_type(self,id):
        file_path = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\Tên và Phân loại\\storm_data.csv"  # Thay thế bằng đường dẫn tới file CSV của bạn
        df = pd.read_csv(file_path)
        # Tìm kiếm trong DataFrame
        result = df[df['ID'] == id]
        if not result.empty:
            return result['Phân loại'].values[0]  # Trả về tên cơn bão
        else:
            return "ID không tồn tại"