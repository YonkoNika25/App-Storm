import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image


#danh sách các biến khí tượng và ý nghĩa
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

class StormPlotter:
    def __init__(self, storm_data):
        self.storm_data = storm_data
    
    
    #hàm này biểu diễn giá trị trung bình của các biến khí tượng theo dòng thời gian cho đến thời điểm bão hình thành  
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
                negative_files =  sorted(negative_files, key=lambda x: int(x.split('_')[2]))

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
            
            
        # Nếu có ít biến hơn số subplots, ẩn các subplots không sử dụng
        for j in range(len(vars), len(axes)):
            axes[j].axis('off')

        plt.tight_layout()  # Tự động điều chỉnh khoảng cách giữa các subplot
        plt.show()
    
    
    #hàm này vẽ biểu đồ thống kê các cơn bão theo năm   
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
        
        max_value = max(counts)
        min_value = min(counts)
        avg_value = sum(counts) // len(counts)

        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.bar(years, counts, color='blue')

        ax.set_title(f"Số lượng cơn bão từ năm {start_year} đến năm {end_year}")
        ax.set_xlabel("Năm")
        ax.set_ylabel("Số lượng cơn bão")
        ax.grid(axis='y')
    
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

        info_text = (
            f"Số bão nhỏ nhất: {min_value} cơn bão\n"
            f"Số bão lớn nhất: {max_value} cơn bão\n"
            f"Trung bình số bão các năm: {avg_value:.2f}"
        )
        ax.text(0.5, -0.15, info_text, transform=ax.transAxes, fontsize=12, ha='center', va='center', color='blue')

        plt.tight_layout()

        # Hiển thị biểu đồ
        plt.xticks(years)  # Đặt nhãn cho các năm
        plt.show()  
    
    #Hàm này vẽ biểu đồ thống kê các cơn bão theo loại bão
    def plot_storm_by_type(self, start_year, end_year):
        type_storm_counts = {type: 0 for type in storm_classification.values()}
        for year in range(start_year, end_year + 1):
            storm_ids = self.storm_data.get_id(year)  # Lấy danh sách các cơn bão trong năm
            for id in storm_ids:
                type_storm_counts[storm_classification[self.storm_data.get_type(id)]] += 1
                
        # Tính toán thêm thông tin
        min_storms_type = min(type_storm_counts, key=type_storm_counts.get)
        min_storms_count = type_storm_counts[min_storms_type]

        max_storms_type = max(type_storm_counts, key=type_storm_counts.get)
        max_storms_count = type_storm_counts[max_storms_type]
        avg_storms = sum(type_storm_counts.values()) / len(type_storm_counts)

        # Vẽ biểu đồ cột
        types = list(type_storm_counts.keys())
        counts = list(type_storm_counts.values())

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.bar( types, counts, color='blue')
        bars = ax.bar( types, counts, color='blue')
        
        if end_year > start_year:
            title = f"Số lượng cơn bão theo dạng bão từ năm {start_year} đến năm {end_year}"
        else:
            title = f"Số lượng cơn bão theo dạng bão trong năm {start_year}"
        ax.set_title(title)
        ax.set_xlabel("Phân loại")
        ax.set_ylabel("Số lượng cơn bão")
        ax.set_xticks(types)  # Đặt nhãn cho các tháng
        ax.grid(axis='y')
    
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
        
        
        # Ghi thông tin bổ sung
        info_text = (
            f"Giá trị nhỏ nhất:  {min_storms_count} cơn bão\n"
            f"Giá trị lớn nhất:  {max_storms_count} cơn bão\n"
            f"Trung bình số bão các dạng: {avg_storms:.2f}"
        )
        ax.text(0.5, -0.15, info_text, transform=ax.transAxes, fontsize=12, ha='center', va='center', color='blue')

        plt.tight_layout()
        # Hiển thị biểu đồ
        plt.show()    
    
    #hàm này vẽ biểu đồ thống kê các cơn bão theo tháng
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
        # Tính toán thêm thông tin
        min_storms_month = min(monthly_storm_counts, key=monthly_storm_counts.get)
        min_storms_count = monthly_storm_counts[min_storms_month]

        max_storms_month = max(monthly_storm_counts, key=monthly_storm_counts.get)
        max_storms_count = monthly_storm_counts[max_storms_month]
        avg_storms = sum(monthly_storm_counts.values()) / len(monthly_storm_counts)

        # Vẽ biểu đồ cột
        months = list(monthly_storm_counts.keys())
        counts = list(monthly_storm_counts.values())

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.bar(months, counts, color='blue')
        bars = ax.bar(months, counts, color='blue')
        
        if end_year > start_year:
            title = f"Số lượng cơn bão theo từng tháng từ năm {start_year} đến năm {end_year}"
        else:
            title = f"Số lượng cơn bão theo từng tháng trong năm {start_year}"
        ax.set_title(title)
        ax.set_xlabel("Tháng")
        ax.set_ylabel("Số lượng cơn bão")
        ax.set_xticks(months)  # Đặt nhãn cho các tháng
        ax.grid(axis='y')
    
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')
        
        
        # Ghi thông tin bổ sung
        info_text = (
            f"Tháng có số bão nhỏ nhất: Tháng {min_storms_month} ({min_storms_count} cơn bão)\n"
            f"Tháng có số bão lớn nhất: Tháng {max_storms_month} ({max_storms_count} cơn bão)\n"
            f"Trung bình số bão các tháng: {avg_storms:.2f}"
        )
        ax.text(0.5, -0.15, info_text, transform=ax.transAxes, fontsize=12, ha='center', va='center', color='blue')

        plt.tight_layout()
        # Hiển thị biểu đồ
        plt.show()  
    
    
    #hàm này vẽ bản đồ đánh dấu ví trí các cơn bão theo các giá trị kinh độ và vĩ độ    
    def plot_storm_address(self, year):
    
    
        positive_dir = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\POSITIVE"
        positive_files = [f for f in os.listdir(positive_dir) if f.startswith(f'POSITIVE_{year}')]    
    
        # Trích xuất tọa độ từ dữ liệu
        latitudes = [int(file[-8:-6]) for file in positive_files]
        longitudes = [int(file[-6:-3]) for file in positive_files]
    
        # Tạo một GeoDataFrame để vẽ
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent([min(longitudes)+0.5, max(longitudes)+0.5, min(latitudes)+0.5, max(latitudes)+0.5], crs=ccrs.PlateCarree())  # Giới hạn bản đồ

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
        
    
    #hàm này vẽ biểu đồ phân tích xu hướng các biến theo năm
    def analyze_trends(self, variable, start_year, end_year):
        """Phân tích xu hướng cho một biến khí tượng trong khoảng thời gian nhất định."""
        years = range(start_year, end_year + 1)
        trend_data = []

        for year in years:
            storm_ids = self.storm_data.get_id(year)
            for storm_id in storm_ids:
                positive_path = [f for f in os.listdir(self.storm_data.positive_dir) if f.startswith(f'POSITIVE_{storm_id}')][0]
                ds = self.storm_data.load_data(os.path.join(self.storm_data.positive_dir, positive_path))
                mean_value = ds[variable].mean().values
                trend_data.append((year, storm_id, mean_value))

        trend_df = pd.DataFrame(trend_data, columns=['Năm', 'ID Cơn Bão', 'Giá Trị Trung Bình'])
        
        # Vẽ biểu đồ xu hướng
        plt.figure(figsize=(12, 6))
        for storm_id in trend_df['ID Cơn Bão'].unique():
            storm_data = trend_df[trend_df['ID Cơn Bão'] == storm_id]
            plt.plot(storm_data['Năm'], storm_data['Giá Trị Trung Bình'], marker='o', label=f"Cơn bão {storm_id}")
        
        plt.title(f"Xu hướng của biến " + variables_l[variable] + f" từ năm {start_year} đến {end_year}")
        plt.xlabel("Năm")
        plt.ylabel("Giá trị trung bình")
        
        plt.grid()
        plt.show()
    
    
    
    #hàm này vẽ biểu đồ chi tiết giá trị của biến khí tượng theo các mốc áp suất    
    def plot_data_for_ps(self, negative_file_name,var):
        ds_negative = self.storm_data.load_data(os.path.join(self.storm_data.negative_dir, negative_file_name))
        # Lấy dữ liệu nhiệt độ và tọa độ
        ps = ds_negative.isobaricInhPa.values
        latitude = ds_negative.latitude.values
        longitude = ds_negative.longitude.values

        # Tạo một cửa sổ Tkinter
        root = tk.Tk()
        root.title(f"{var} Plots")

        # Tạo một khung cuộn
        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Thiết lập khung cuộn
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Số lượng cột
        num_columns = 3
        num_plots = len(ps)

        # Tạo figure và các trục cho các biểu đồ
        fig, axs = plt.subplots(num_plots // num_columns + (num_plots % num_columns > 0), num_columns, figsize=(17, 4.2 * (num_plots // num_columns + 1)), constrained_layout=True)

        # Chuyển đổi axs thành mảng 1 chiều
        axs = axs.flatten()

        # Tạo biểu đồ
        for i, p in enumerate(ps):
            var_dt = ds_negative[var].sel(isobaricInhPa=p).values
            im = axs[i].imshow(var_dt, cmap='coolwarm', aspect='auto', extent=[longitude.min(), longitude.max(), latitude.min(), latitude.max()])
            axs[i].set_title(variables_l[var] + f" tại {p} hPa")
            axs[i].set_xlabel('Longitude')
            axs[i].set_ylabel('Latitude')
            fig.colorbar(im, ax=axs[i])  # Thêm thanh màu cho mỗi biểu đồ

        # Ẩn các trục không sử dụng
        for j in range(i + 1, len(axs)):
            axs[j].axis('off')

        # Thêm biểu đồ vào khung cuộn
        canvas_plot = FigureCanvasTkAgg(fig, master=scrollable_frame)
        canvas_plot.get_tk_widget().pack()
        canvas_plot.draw()

        # Đặt các widget cuộn
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Chạy ứng dụng
        root.mainloop()
        
        
    def plot_storm_images(self,storms_ids):
        list_paths = self.storm_data.list_path_image(storms_ids)
        root = tk.Tk()
        root.title("Ảnh và đường đi của các cơn bão")
        
        # Tạo một khung cuộn
        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Thiết lập khung cuộn
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Số lượng cột
        num_columns = 4
        num_images = len(list_paths)

        # Tạo figure và các trục cho các ảnh
        fig, axs = plt.subplots(num_images // num_columns + (num_images % num_columns > 0), num_columns, figsize=(17, 4.2 * (num_images // num_columns + 1)), constrained_layout=True)

        # Chuyển đổi axs thành mảng 1 chiều
        axs = axs.flatten()
        
            # Tạo biểu đồ
        for i, image_path in enumerate(list_paths):
            img = Image.open(image_path)  # Mở ảnh
            axs[i].imshow(img)  # Hiển thị ảnh
            if i % 2 == 0:
                title = f"Ảnh vệ tinh của cơn bão {self.storm_data.get_name(storms_ids[int(i/2)])}"
            else:
                title = f"Ảnh đường đi của cơn bão {self.storm_data.get_name(storms_ids[int(i/2)])}"
            axs[i].set_title(title)  # Tiêu đề cho mỗi ảnh
            axs[i].axis('off')  # Tắt trục

        # Ẩn các trục không sử dụng
        for j in range(i + 1, len(axs)):
            axs[j].axis('off')

        # Thêm biểu đồ vào khung cuộn
        canvas_plot = FigureCanvasTkAgg(fig, master=scrollable_frame)
        canvas_plot.get_tk_widget().pack()
        canvas_plot.draw()

        # Đặt các widget cuộn
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Chạy ứng dụng
        root.mainloop()       