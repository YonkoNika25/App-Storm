import xarray as xr
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import tkinter as tk
from tkinter import messagebox, simpledialog

variables_l= {
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
                'Ý nghĩa' :variables_l[var]
            })
        list_table = pd.DataFrame(list)
        return list_table
    
class StormPlotter:
    def __init__(self, storm_data):
        self.storm_data = storm_data
          
    def plot_variable(self, storm_ids, vars):
        if not storm_ids:
            print("Không có cơn bão nào được chọn.")
            return

        # Tạo một lưới các biểu đồ
        num_vars = len(vars)
        cols = 2  # Số cột trong lưới
        rows = num_vars // 2  # Số hàng bằng số biếns

        fig, axes = plt.subplots(rows, cols, figsize=(10, 5 * rows))

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

            axes[idx].set_title(f"Giá trị trung bình của {var}")
            axes[idx].set_xlabel("Thời gian (giờ trước khi bão đổ bộ)")
            axes[idx].set_ylabel("Giá trị trung bình")
            axes[idx].grid()
            axes[idx].legend()

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

        # Tính toán thêm thông tin
        min_storms_month = min(monthly_storm_counts, key=monthly_storm_counts.get)
        min_storms_count = monthly_storm_counts[min_storms_month]

        max_storms_month = max(monthly_storm_counts, key=monthly_storm_counts.get)
        max_storms_count = monthly_storm_counts[max_storms_month]
        avg_storms = sum(monthly_storm_counts.values()) / len(monthly_storm_counts)

        # Vẽ biểu đồ cột
        months = list(monthly_storm_counts.keys())
        counts = list(monthly_storm_counts.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(months, counts, color='blue')

        ax.set_title("Số lượng cơn bão theo từng tháng")
        ax.set_xlabel("Tháng")
        ax.set_ylabel("Số lượng cơn bão")
        ax.set_xticks(months)  # Đặt nhãn cho các tháng
        ax.grid(axis='y')

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), ha='center', va='bottom')

        # Ghi thông tin bổ sung
        info_text = (
            f"Tháng có số bão nhỏ nhất: Tháng {min_storms_month} ({min_storms_count} cơn bão)\n"
            f"Tháng có số bão lớn nhất: Tháng {max_storms_month} ({max_storms_count} cơn bão)\n"
            f"Trung bình số bão các tháng: {avg_storms:.2f}"
        )
        ax.text(0.5, -0.15, info_text, transform=ax.transAxes, fontsize=12, ha='center', va='center', color='black')

        # Hiển thị biểu đồ
        plt.tight_layout()
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

class StormApp:
    def __init__(self, root, storm_data, storm_plotter):
        self.root = root
        self.root.title("Ứng dụng Cơn Bão")
        self.storm_data = storm_data
        self.storm_plotter = storm_plotter

        self.create_widgets()

    def create_widgets(self):
        self.btn_view_storm_var = tk.Button(self.root, text="Xem các biến của 1 cơn bão", command=self.view_storm_variable)
        self.btn_view_storm_var.pack(pady=10)

        self.btn_view_var_year = tk.Button(self.root, text="Xem một biến trong cả 1 năm", command=self.view_variable_year)
        self.btn_view_var_year.pack(pady=10)

        self.btn_storms_by_year = tk.Button(self.root, text="Xem số cơn bão theo từng năm", command=self.view_storms_by_year)
        self.btn_storms_by_year.pack(pady=10)

        self.btn_storms_by_month = tk.Button(self.root, text="Xem số cơn bão theo từng tháng", command=self.view_storms_by_month)
        self.btn_storms_by_month.pack(pady=10)

        self.btn_storm_path = tk.Button(self.root, text="Xem vị trí các cơn bão", command=self.view_storm_path)
        self.btn_storm_path.pack(pady=10)
        
        self.btn_storm_path = tk.Button(self.root, text="Xem danh sách bão và thông tin các biến", command=self.view_storm_and_variable)
        self.btn_storm_path.pack(pady=10)

    def view_storm_variable(self):
        # Nhập năm từ người dùng
        year = simpledialog.askinteger("Input", "Bạn vui lòng nhập năm (2010 - 2020):")
        if year is not None:
            # Lấy thông tin cơn bão trong năm
            storm_info_table = self.storm_data.storms_infomation(year)

            # Tạo một cửa sổ mới để hiển thị bảng thông tin
            info_window = tk.Toplevel(self.root)
            info_window.title("Bảng thông tin các cơn bão trong năm {}".format(year))

            # Hiển thị tiêu đề
            title_label = tk.Label(info_window, text="Bảng thông tin các cơn bão trong năm {}".format(year), font=("Arial", 16))
            title_label.pack()

            # Hiển thị bảng thông tin cơn bão
            storm_info_text = tk.Text(info_window, wrap="word", height=10)
            storm_info_text.pack(expand=True, fill='both')

            # Chuyển đổi DataFrame thành chuỗi và hiển thị
            storm_info_text.insert(tk.END, storm_info_table.to_string(index=False))

            # Tạo vùng checkbox để chọn cơn bão
            checkbox_frame = tk.Frame(info_window)
            checkbox_frame.pack(fill='both', expand=True)

            self.selected_storms = []  # Danh sách lưu trạng thái checkbox

            #Tạo checkbox cho từng hàng
            columns = 4
            for index, row in storm_info_table.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame, text=f"Số thứ tự {index + 1}: {row['ID']}", variable=var)
                chk.grid(row=index // columns, column=index % columns, sticky="w", padx=10, pady=5)
                self.selected_storms.append((var, row['ID']))  # Lưu trạng thái và ID cơn bão

            # Thêm nút để xác nhận lựa chọn
            confirm_button = tk.Button(info_window, text="Xem thông tin các cơn bão", command=self.confirm_multiple_storm_choices)
            confirm_button.pack()

    def confirm_multiple_storm_choices(self):
        # Lấy danh sách các cơn bão được chọn
        selected_ids = [storm_id for var, storm_id in self.selected_storms if var.get() == 1]

        if selected_ids:
            # Thực hiện hành động với các ID được chọn
            for storm_id in selected_ids:
                self.storm_plotter.plot_variable(storm_id)
        else:
            messagebox.showinfo("Thông báo", "Bạn chưa chọn cơn bão nào.")


    def view_variable_year(self):
        year = simpledialog.askinteger("Input", "Nhập năm:")
        if year is not None:
            # Lấy thông tin cơn bão trong năm
            list_table = self.storm_data.list_variable(year)

            # Tạo một cửa sổ mới để hiển thị bảng thông tin
            info_window = tk.Toplevel(self.root)
            info_window.title("Danh Sách Các Biến Khí Tượng ")

            # Hiển thị tiêu đề
            title_label = tk.Label(info_window, text="Danh Sách Các Biến Khí Tượng", font=("Arial", 16))
            title_label.pack()

            # Hiển thị bảng thông tin của biến
            storm_info_text = tk.Text(info_window, wrap="word")
            storm_info_text.pack()

            # Chuyển đổi DataFrame thành chuỗi và hiển thị
            storm_info_text.insert(tk.END, list_table.to_string(index=False))

            # Thêm ô nhập để người dùng nhập số thứ tự của biến
            order_label = tk.Label(info_window, text="Nhập số thứ tự biến khí tượng để xem thông tin:")
            order_label.pack()

            self.order_entry = tk.Entry(info_window)
            self.order_entry.pack()

            # Thêm nút để xác nhận lựa chọn
            confirm_button = tk.Button(info_window, text="Xem thông tin của biến", command=lambda: self.confirm_var_choice(list_table,year))
            confirm_button.pack()
            
    def confirm_var_choice(self, list_table,year):
        # Lấy số thứ tự từ ô nhập
        try:
            order = int(self.order_entry.get())
            if 1 <= order <= len(list_table):
                storm_info = list_table.iloc[order - 1]  # Lấy thông tin cơn bão
                self.storm_plotter.plot_variable_year(storm_info['Tên biến'],year)
            else:
                messagebox.showerror("Lỗi", "Số thứ tự không hợp lệ.")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số hợp lệ.")

    def view_storms_by_year(self):
        start_year = simpledialog.askinteger("Input", "Nhập năm bắt đầu:")
        end_year = simpledialog.askinteger("Input", "Nhập năm kết thúc:")
        if start_year is not None and end_year is not None:
            self.storm_plotter.plot_storms(start_year, end_year)

    def view_storms_by_month(self):
        start_year = simpledialog.askinteger("Input", "Nhập năm bắt đầu:")
        end_year = simpledialog.askinteger("Input", "Nhập năm kết thúc:")
        if start_year is not None and end_year is not None:
        # Implement the function to plot storms by month
            self.storm_plotter.plot_storms_by_month(start_year, end_year)

    def view_storm_path(self):
        year = simpledialog.askinteger("Input", "Nhập năm:")
        if year is not None:
            # Implement the function to plot storm paths
            self.storm_plotter.plot_storm_address(year)
            
    def view_storm_and_variable(self):
        year = simpledialog.askinteger("Input", "Bạn vui lòng nhập năm (2010 - 2020):")
        if year is not None:
            # Lấy thông tin cơn bão trong năm
            storm_info_table = self.storm_data.storms_infomation(year)
        
            # Lấy danh sách các biến
            list_table = self.storm_data.list_variable(year)

            # Tạo một cửa sổ mới để hiển thị bảng thông tin
            info_window = tk.Toplevel(self.root)
            info_window.title("Bảng thông tin các cơn bão và biến trong năm {}".format(year))

            # Hiển thị tiêu đề
            title_label = tk.Label(info_window, text="Bảng thông tin các cơn bão trong năm {}".format(year), font=("Arial", 16))
            title_label.pack()

            # Hiển thị bảng thông tin cơn bão
            storm_info_text = tk.Text(info_window, wrap="word", height=10)
            storm_info_text.pack(expand=True, fill='both')
            storm_info_text.insert(tk.END, storm_info_table.to_string(index=False))

            # Hiển thị bảng danh sách biến
            variable_info_text = tk.Text(info_window, wrap="word", height=10)
            variable_info_text.pack(expand=True, fill='both')
            variable_info_text.insert(tk.END, list_table.to_string(index=False))

            # Tạo vùng checkbox để chọn cơn bão
            checkbox_frame_storm = tk.Frame(info_window)
            checkbox_frame_storm.pack(fill='both', expand=True)
            self.selected_storms = []

            # Tạo checkbox cho từng cơn bão
            columns = 8
            for index, row in storm_info_table.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame_storm, text=f"Số thứ tự {index + 1}: {row['ID']}", variable=var)
                chk.grid(row=index // columns, column=index % columns, sticky="w", padx=10, pady=5)
                self.selected_storms.append((var, row['ID']))  # Lưu trạng thái và ID cơn bão

            # Tạo vùng checkbox để chọn biến
            checkbox_frame_variable = tk.Frame(info_window)
            checkbox_frame_variable.pack(fill='both', expand=True)
            self.selected_variables = []

            # Tạo checkbox cho từng biến
            for index, row in list_table.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame_variable, text=f"Số thứ tự {index + 1}: {row['Tên biến']}", variable=var)
                chk.grid(row=index // columns, column=index % columns, sticky="w", padx=10, pady=5)
                self.selected_variables.append((var, row['Tên biến']))  # Lưu trạng thái và tên biến

            # Thêm nút để xác nhận lựa chọn
            confirm_button = tk.Button(info_window, text="Xem thông tin các cơn bão và biến", command=self.confirm_storm_and_variable_choices)
            confirm_button.pack()

    def confirm_storm_and_variable_choices(self):
        # Lấy danh sách các cơn bão được chọn
        selected_storm_ids = [storm_id for var, storm_id in self.selected_storms if var.get() == 1]
    
        # Lấy danh sách các biến được chọn
        selected_variable_names = [var_name for var, var_name in self.selected_variables if var.get() == 1]

        if selected_storm_ids and selected_variable_names:
            # Thực hiện hành động với các ID cơn bão và biến được chọn
            self.storm_plotter.plot_variable(selected_storm_ids,selected_variable_names)
        else:
            messagebox.showinfo("Thông báo", "Bạn chưa chọn cơn bão hoặc biến nào.")


def main():
    positive_dir = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\POSITIVE"
    negative_dir = "C:\\Users\\linhn\\Documents\\DATA_TC\\DATA\\PastDomain"
    
    storm_data = StormData(positive_dir, negative_dir)
    storm_plotter = StormPlotter(storm_data)

    root = tk.Tk()
    app = StormApp(root, storm_data, storm_plotter)
    root.mainloop()

if __name__ == "__main__":
    main()