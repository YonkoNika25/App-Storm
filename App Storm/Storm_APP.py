import tkinter as tk
from tkinter import messagebox, simpledialog
from Storm_Data import StormData
from StormPlotter import StormPlotter



class StormApp:
    def __init__(self, root, storm_data, storm_plotter):
        self.root = root
        self.root.title("Ứng dụng Cơn Bão")
        self.storm_data = storm_data
        self.storm_plotter = storm_plotter

        self.create_widgets()

    def create_widgets(self):
        
        self.btn_storms_by_year = tk.Button(self.root, text="Xem số cơn bão theo từng năm", command=self.view_storms_by_year)
        self.btn_storms_by_year.pack(pady=10)

        self.btn_storms_by_month = tk.Button(self.root, text="Xem số cơn bão theo từng tháng", command=self.view_storms_by_month)
        self.btn_storms_by_month.pack(pady=10)

        self.btn_storm_path = tk.Button(self.root, text="Xem vị trí các cơn bão", command=self.view_storm_path)
        self.btn_storm_path.pack(pady=10)
        
        self.btn_storm_path = tk.Button(self.root, text="Xem danh sách cơn bão và các biến khí tượng", command=self.view_storm_and_variable)
        self.btn_storm_path.pack(pady=10)

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
                chk = tk.Checkbutton(checkbox_frame_variable, text=f"{row['Ý nghĩa']}", variable=var)
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