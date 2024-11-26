import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature

variables_l = {
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

class StormPlotter:
    def __init__(self, storm_data):
        self.storm_data = storm_data
        
    def plot_variable(self, storm_ids, vars):
        if not storm_ids:
            print("Không có cơn bão nào được chọn.")
            return

        # Tạo một lưới các biểu đồ
        num_vars = len(vars)
        cols = 4 # Số cột trong lưới
        
        if len(vars) < cols:
            cols = len(vars)
            
        rows = (num_vars + cols - 1) // cols  # Số hàng bằng số biến

        fig, axes = plt.subplots(rows, cols, figsize=(15, 2.6 * rows))
        if len(vars) == 1:
            axes = np.array([axes])
        else :
            axes = axes.flatten()

        for idx, var in enumerate(vars):
            for storm_id in storm_ids:
                negative_files = self.storm_data.get_negative(storm_id)
                negative_files.sort()

                mean_values = np.zeros(len(negative_files))

                for i, negative_file in enumerate(negative_files):
                    negative_data = self.storm_data.load_data(os.path.join(self.storm_data.negative_dir, negative_file))
                    mean_value = negative_data[var].mean().values
                    mean_values[i] = mean_value

                time_points = self.storm_data.get_time(storm_id)

                # Vẽ dữ liệu lên subplot tương ứng với biến
                axes[idx].plot(time_points, mean_values, label=f"Cơn bão {storm_id}")

            axes[idx].set_title(f"Trung bình " + variables_l[var])
            axes[idx].set_xlabel("Thời gian (giờ trước khi bão đổ bộ)")
            axes[idx].set_ylabel("Giá trị trung bình")
            axes[idx].grid()
            axes[idx].legend()
            
        # Nếu có ít biến hơn số subplots, ẩn các subplots không sử dụng
        for j in range(len(vars), len(axes)):
            axes[j].axis('off')

        plt.tight_layout()  # Tự động điều chỉnh khoảng cách giữa các subplot
        plt.show()
        
    def plot_storms(self, start_year, end_year):
        # Tạo một dictionary để lưu trữ số lượng cơn bão theo năm
        storm_counts = {}

        # Duyệt qua từng năm từ start_year đến end_year
        for year in range(start_year, end_year + 1):
            storm_ids = self.storm_data.get_id(year)  # Lấy danh sách các cơn bão trong năm
            storm_counts[year] = len(storm_ids)  # Đếm số lượng cơn bão

        # Vẽ biểu đồ cột
        years = list(storm_counts.keys())
        counts = list(storm_counts.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(years, counts, color='blue')

        ax.set_title("Số lượng cơn bão từ năm 2010 đến 2020")
        ax.set_xlabel("Năm")
        ax.set_ylabel("Số lượng cơn bão")
        ax.grid(axis='y')
    
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')


        # Hiển thị biểu đồ
        plt.xticks(years)  # Đặt nhãn cho các năm
        plt.show()  
        
    def plot_storms_by_month(self, start_year, end_year):
        # Tạo một dictionary để lưu trữ số lượng cơn bão theo tháng
        monthly_storm_counts = {month: 0 for month in range(1, 13)}

        # Duyệt qua từng năm từ start_year đến end_year
        for year in range(start_year, end_year + 1):
            storm_ids = self.storm_data.get_id(year)  # Lấy danh sách các cơn bão trong năm
            for storm_id in storm_ids:
                # Lấy thông tin thời gian của cơn bão
                positive_dir = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\POSITIVE"
                positive_path = [f for f in os.listdir(positive_dir) if f.startswith(f'POSITIVE_{storm_id}')][0]
                data_positive = self.storm_data.load_data(os.path.join(positive_dir, positive_path))
                storm_time = data_positive.time.values  # Giả sử thời gian bão là thời gian đầu tiên trong file

                # Chuyển đổi thời gian thành năm và tháng
                storm_date = pd.to_datetime(storm_time)
                month = storm_date.month

                # Tăng số lượng cơn bão cho tháng tương ứng
                monthly_storm_counts[month] += 1

        # Vẽ biểu đồ cột
        months = list(monthly_storm_counts.keys())
        counts = list(monthly_storm_counts.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(months, counts, color='blue')
        bars = ax.bar(months, counts, color='blue')

        ax.set_title("Số lượng cơn bão theo từng tháng")
        ax.set_xlabel("Tháng")
        ax.set_ylabel("Số lượng cơn bão")
        ax.set_xticks(months)  # Đặt nhãn cho các tháng
        ax.grid(axis='y')
    
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
        
        
        ax.text(0.5, 1, 'Chuỗi văn bản của bạn ở đây', 
                                             transform=ax.transAxes,
                                             fontsize=12, ha='center', va='center', color='black')



        # Hiển thị biểu đồ
        plt.show()  
        
    def plot_storm_address(self, year):
    
    
        positive_dir = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\POSITIVE"
        positive_files = [f for f in os.listdir(positive_dir) if f.startswith(f'POSITIVE_{year}')]    
    
        # Trích xuất tọa độ từ dữ liệu
        latitudes = [int(file[-8:-6]) for file in positive_files]
        longitudes = [int(file[-6:-3]) for file in positive_files]
    
        # Tạo một GeoDataFrame để vẽ
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent([min(longitudes)-5, max(longitudes)+5, min(latitudes)-5, max(latitudes)+5], crs=ccrs.PlateCarree())  # Giới hạn bản đồ

        # Thêm các yếu tố bản đồ

        ax.add_feature(cfeature.LAND, color='lightgrey')
        ax.add_feature(cfeature.OCEAN, color='lightblue')
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        # Vẽ đường đi của cơn bão
        ax.scatter(longitudes, latitudes, color='red', marker='o', s=50)  # Sử dụng scatter để vẽ các điểm
        for lon, lat in zip(longitudes, latitudes):
            ax.text(lon, lat, f'({lon}, {lat})', fontsize=8, transform=ccrs.PlateCarree())

        # Thêm tiêu đề
        plt.title('Vị trí các cơn bão lúc mới hình thành', fontsize=16)

        # Hiển thị bản đồ
        plt.show()