import xarray as xr
import os
import pandas as pd

variables = {
    "EPV": "Ép suất hơi nước ",
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

class StormData:
    def __init__(self, positive_dir, negative_dir):
        self.positive_dir = positive_dir
        self.negative_dir = negative_dir

    def get_id(self, year):
        """Lấy danh sách các cơn bão trong năm."""
        positive_files = [f for f in os.listdir(self.positive_dir) if f.startswith(f'POSITIVE_{year}')]
        storm_ids = [f[9:22] for f in positive_files]
        return storm_ids

    def get_negative(self, storm_id):
        """Hiển thị các thời điểm trước bão cơn bão."""
        negative_files = [f for f in os.listdir(self.negative_dir) if f.startswith(f'NEGATIVE_{storm_id}')]
        return negative_files

    def load_data(self, file_path):
        """Load dữ liệu từ file NetCDF."""
        return xr.open_dataset(file_path)

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
    
    def storms_infomation(self, year):
        storms_id = self.get_id(year)
        storm_data = []
        
        for id in storms_id:
            day_of_year = int(id[4:7])
            latitude = int(id[8:10])
            longitude = int(id[10:13])
            
            
            positive_path = [f for f in os.listdir(self.positive_dir) if f.startswith(f'POSITIVE_{id}')][0]
            ds = self.load_data(os.path.join(self.positive_dir, positive_path))
            time = ds.time.values # Giả sử time là một mảng, có thể cần xử lý thêm
            
            storm_data.append({
                'Số thứ tự': len(storm_data) + 1,
                'ID':id,
                'Ngày xuất hiện(1 - 365)': day_of_year,
                'Vĩ độ': latitude,
                'Kinh độ': longitude,
                'Thời gian': time
            })
            
        storm_table = pd.DataFrame(storm_data)
        return storm_table
    
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