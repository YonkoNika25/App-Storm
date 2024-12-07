import tkinter as tk
from tkinter import messagebox, simpledialog
from Storm_Data import StormData
from StormPlotter import StormPlotter

#danh sách các biến khí tượng và ý nghĩa
variables_l= {
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


#lớp này xây dựng giao diện người dùng và các hàm logic để xử lí các thao tác
class StormApp:
    def __init__(self, root, storm_data, storm_plotter):
        self.root = root
        self.root.title("Phân Tích Dữ Liệu Bão")
        self.storm_data = storm_data
        self.storm_plotter = storm_plotter
        self.create_widgets()
        
    #xây dựng các nút để người dùng chọn chức năng
    def create_widgets(self):
        self.btn_storm_image = tk.Button(self.root,text = "Ảnh vệ tinh và đường đi của bão", command = self.show_storm_image)
        self.btn_storm_image.pack(pady = 10)
        
        self.btn_storm_path = tk.Button(self.root, text="Giá trị trung bình của các biến dữ liệu trong quá trình bão hình thành", command=self.view_storm_and_variable)
        self.btn_storm_path.pack(pady=10)
        
        self.btn_select_storm = tk.Button(self.root, text="Giá trị chi tiết của các biến dữ liệu trong quá trình bão hình thành", command=self.select_storm_and_variable)
        self.btn_select_storm.pack(pady=10)
        
        self.btn_storms_by_year = tk.Button(self.root, text="Thống kê", command=self.thong_ke)
        self.btn_storms_by_year.pack(pady=10)
    
    
    #hàm này được gọi khi người dùng chọn chức năng thống kê
    def thong_ke(self):
        # Tạo một cửa sổ mới để hiển thị bảng thông tin
        info_window = tk.Toplevel(self.root)
        info_window.title("Thống Kê")
        
        # Hiển thị tiêu đề
        title_label = tk.Label(info_window, text="Thống Kê", font=("Arial", 16))
        title_label.pack()
        
        self.btn_storms_by_year = tk.Button(info_window, text="Thống kê số cơn bão theo từng năm", command=self.view_storms_by_year)
        self.btn_storms_by_year.pack(pady=10)

        self.btn_storms_by_month = tk.Button(info_window, text="Thống kê số cơn bão theo từng tháng", command=self.view_storms_by_month)
        self.btn_storms_by_month.pack(pady=10)
        
        self.btn_storms_by_type = tk.Button(info_window, text="Thống kê số cơn bão theo loại bão", command=self.view_storms_by_type)
        self.btn_storms_by_type.pack(pady=10)

        self.btn_storm_address = tk.Button(info_window, text="Thống kê vị trí các cơn bão", command=self.view_storm_path)
        self.btn_storm_address.pack(pady=10)
        
        self.btn_analyze_trends = tk.Button(info_window, text="Phân tích xu hướng các biến theo năm ", command=self.view_analyze_trends)
        self.btn_analyze_trends.pack(pady=10)
    
        
    #hàm này được gọi nếu người dùng chọn chức năng "Ảnh vệ tinh và đường đi của bão"
    def show_storm_image(self):
        year = simpledialog.askinteger("Input", "Bạn vui lòng nhập năm (2010 - 2020):")
        if year is not None:
            # Lấy thông tin cơn bão trong năm
            storm_info_table = self.storm_data.storms_infomation(year)

            # Tạo một cửa sổ mới để hiển thị bảng thông tin
            info_window = tk.Toplevel(self.root)
            info_window.title("Chọn cơn bão trong năm {}".format(year))
            
            # Hiển thị tiêu đề
            title_label = tk.Label(info_window, text="Bảng danh sách các cơn bão trong năm {}".format(year), font=("Arial", 16))
            title_label.pack()
            
            # Hiển thị bảng thông tin cơn bão
            storm_info_text = tk.Text(info_window, wrap="word", height=10)
            storm_info_text.pack(expand=True, fill='both')
            storm_info_text.insert(tk.END, storm_info_table.to_string(index=False))

            # Tạo vùng checkbox để chọn cơn bão
            checkbox_frame_storm = tk.Frame(info_window)
            checkbox_frame_storm.pack(fill='both', expand=True)
            self.selected_storms = []
            
            # Tạo checkbox "Chọn tất cả"
            select_all_storm = tk.IntVar()
            select_all_chk = tk.Checkbutton(checkbox_frame_storm, text="Chọn tất cả", variable=select_all_storm,command=lambda: self.select_all_storms(select_all_storm.get()))
            select_all_chk.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            # Tạo checkbox cho từng cơn bão
            columns = 8
            for index, row in storm_info_table.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame_storm, text=f"Số thứ tự {index + 1}: {row['ID']}", variable=var)
                chk.grid(row=(index // columns)+1, column=index % columns, sticky="w", padx=10, pady=5)
                self.selected_storms.append((var, row['ID']))  # Lưu trạng thái và ID cơn bão
            # Nút xác nhận lựa chọn
            confirm_button = tk.Button(info_window, text="Xác nhận chọn cơn bão", command=lambda: self.confirm_storm_choice())            
            confirm_button.pack()
            
    #hàm này tạo 1 checkbox để người dùng chọn tất cả các cơn bão trong hàm show_storm_image       
    def select_all_storms(self, select_all):
        for var ,_ in self.selected_storms:
            var.set(select_all)        

    #hàm này gọi đến hàm biểu diễn ảnh của các cơn bão trong lớp StormPlotter
    def confirm_storm_choice(self):
        # Lấy danh sách các cơn bão được chọn
        selected_storm_ids = [storm_id for var, storm_id in self.selected_storms if var.get() == 1]
    
        if selected_storm_ids:
            # Thực hiện hành động với các ID cơn bão và biến được chọn
            self.storm_plotter.plot_storm_images(selected_storm_ids)
        else:
            messagebox.showinfo("Thông báo", "Bạn chưa chọn cơn bão nào.")

    #hàm này được gọi nếu người dùng chọn chức năng "Giá trị chi tiết của các biến dữ liệu trong quá trình bão hình thành"
    def select_storm_and_variable(self):
        year = simpledialog.askinteger("Input", "Bạn vui lòng nhập năm (2010 - 2020):")
        if year is not None:
            # Lấy thông tin cơn bão trong năm
            storm_info_table = self.storm_data.storms_infomation(year)

            # Tạo một cửa sổ mới để hiển thị bảng thông tin
            info_window = tk.Toplevel(self.root)
            info_window.title("Chọn cơn bão trong năm {}".format(year))
            
            # Hiển thị tiêu đề
            title_label = tk.Label(info_window, text="Bảng danh sách các cơn bão trong năm {}".format(year), font=("Arial", 16))
            title_label.pack()
            
            # Hiển thị bảng thông tin cơn bão
            storm_info_text = tk.Text(info_window, wrap="word", height=10)
            storm_info_text.pack(expand=True, fill='both')
            storm_info_text.insert(tk.END, storm_info_table.to_string(index=False))

            # Tạo vùng checkbox để chọn cơn bão
            checkbox_frame_storm = tk.Frame(info_window)
            checkbox_frame_storm.pack(fill='both', expand=True)

            self.selected_storm_id = None  # Biến để lưu ID của cơn bão được chọn
            self.storm_vars = []  # Danh sách các IntVar cho checkbox

            # Tạo checkbox cho từng cơn bão
            columns = 8
            for index, row in storm_info_table.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame_storm, text=f"Số thứ tự {index + 1}: {row['ID']}", variable=var,
                                    command=lambda var=var, storm_id=row['ID']: self.select_only_one_storm(var, storm_id))
                chk.grid(row=index // columns, column=index % columns, sticky="w", padx=10, pady=5)

                self.storm_vars.append((var, row['ID']))  # Lưu trạng thái và ID cơn bão
            # Nút xác nhận lựa chọn
            confirm_button = tk.Button(info_window, text="Xác nhận chọn cơn bão", command=lambda: self.confirm_storm_selection(year))            
            confirm_button.pack()
            
            
    #đảm bảo chỉ có một cơn bão được chọn từ danh sách bão trong hàm select_storm_and_variable
    def select_only_one_storm(self, selected_var, storm_id):
        # Bỏ chọn tất cả các checkbox khác
        for var, id in self.storm_vars:
            if id != storm_id:
                var.set(0)  # Bỏ chọn checkbox khác
        selected_var.set(1)  # Đặt checkbox hiện tại là đã chọn
        self.selected_storm_id = storm_id  # Cập nhật ID cơn bão được chọn
        
    #xác nhận cơn bão được chọn trong hàm select_storm_and_variable và chuyển sang bước chọn biến
    def confirm_storm_selection(self,year):
        # Lấy ID của cơn bão được chọn
        selected_storm_id = self.selected_storm_id
        

        if selected_storm_id:
            # Lấy danh sách các file negative cho cơn bão đã chọn
            negative_files = self.storm_data.list_negative(selected_storm_id)
            
            # Lấy danh sách các biến
            var_table = self.storm_data.list_variable(year)

            #tạo cửa số mới để hiển thị danh sách các file negative
            negative_window = tk.Toplevel(self.root)
            negative_window.title("Bảng danh sách các file negetive theo id {}".format(selected_storm_id))

            # Hiển thị tiêu đề
            title_label = tk.Label(negative_window, text="Bảng danh sách các file negetive theo id {}".format(selected_storm_id), font=("Arial", 16))
            title_label.pack()

            # Hiển thị bảng danh sách file negative
            storm_info_text = tk.Text(negative_window, wrap="word", height=10)
            storm_info_text.pack(expand=True, fill='both')
            storm_info_text.insert(tk.END, negative_files.to_string(index=False))
            
            # Hiển thị bảng danh sách biến
            variable_info_text = tk.Text(negative_window, wrap="word", height=10)
            variable_info_text.pack(expand=True, fill='both')
            variable_info_text.insert(tk.END, var_table.to_string(index=False))

            # Tạo vùng checkbox để chọn file
            checkbox_frame_file = tk.Frame(negative_window)
            checkbox_frame_file.pack(fill='both', expand=True)
            self.selected_file = None
            self.selected_vars1 = []

            # Tạo checkbox cho từng file
            columns = 4
            for index, row in negative_files.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame_file, text=f"Số thứ tự {index + 1}: {row['Tên file']}", variable=var,command=lambda var=var, file_name=row['Tên file']: self.select_only_one_file(var, file_name))
                chk.grid(row=index // columns, column=index % columns, sticky="w", padx=10, pady=5)

                self.selected_vars1.append((var, row['Tên file']))  
            
            # Tạo vùng checkbox để chọn biến
            checkbox_frame_variable = tk.Frame(negative_window)
            checkbox_frame_variable.pack(fill='both', expand=True)
            selected_variable = None
            self.selected_var2 = []
            
            # Tạo checkbox cho từng biến
            columns = 8
            for index, row in var_table.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame_variable, text=f"{row['Ý nghĩa']}", variable=var,
                                    command=lambda var=var, var_name=row['Ý nghĩa']: self.select_only_one_var(var, var_name))
                chk.grid(row=index // columns, column=index % columns, sticky="w", padx=10, pady=5)
                self.selected_var2.append((var, row['Ý nghĩa']))
            
            
            # Thêm nút để xác nhận lựa chọn
            confirm_button = tk.Button(negative_window, text="Xem dữ liệu chi tiết của biến được chọn", command=self.confirm_file_and_variable_choices)
            confirm_button.pack()  
            
       
    #đảm bảo chỉ có một file negative được chọn từ danh sách file negative trong hàm confirm_storm_selection          
    def select_only_one_file(self, selected_var, file_name):
        # Bỏ chọn tất cả các checkbox khác
        for var, name in self.selected_vars1:
            if name != file_name:
                var.set(0)  # Bỏ chọn checkbox khác
        selected_var.set(1)  # Đặt checkbox hiện tại là đã chọn
        self.selected_file_name = file_name  # Cập nhật ID cơn bão được chọn
        
    #đảm bảo chỉ có một biến được chọn từ danh sách biến trong hàm confirm_storm_selection
    def select_only_one_var(self, selected_var, var_name):
        # Bỏ chọn tất cả các checkbox khác
        for var, name in self.selected_var2:
            if name != var_name:
                var.set(0)  # Bỏ chọn checkbox khác
        selected_var.set(1)  # Đặt checkbox hiện tại là đã chọn
        self.selected_var_name = var_name  # Cập nhật ID cơn bão được chọn
        
    #tìm tên biến khi biết ý nghĩa của biến trong từ điển variables_l ở đầu đoạn code   
    def fine_key_from_value(self,val):
        key_found = None
        for key, value in variables_l.items():
            if value == val:
                key_found = key
                break
        return key_found
    
    #gọi hàm biểu diễn chi tiết giá trị của biến được chọn    
    def confirm_file_and_variable_choices(self):
        # Lấy danh sách các file được chọn
        selected_file = self.selected_file_name
        
        # Lấy danh sách các biến được chọn
        selected_variable_name = self.selected_var_name
        selected_variable_name = self.fine_key_from_value(selected_variable_name)
        if selected_file and selected_variable_name:
            # Thực hiện hành động với các ID cơn bão và biến được chọn
            self.storm_plotter.plot_data_for_ps(selected_file,selected_variable_name)
        else:
            messagebox.showinfo("Thông báo", "Bạn chưa chọn cơn bão hoặc biến nào.")
                     
    #hàm này được gọi nếu người dùng chọn chức năng 'Phân tích xu hướng các biến theo năm' trong hàm thong_ke
    def view_analyze_trends(self):
        # Hiển thị danh sách các biến và ý nghĩa
        variable_info = "\n".join([f"{var}: {desc}" for var, desc in variables_l.items()])
        variable_selection = simpledialog.askstring("Chọn biến", f"Chọn biến để phân tích xu hướng:\n{variable_info}\nNhập tên biến:")
        
        start_year = simpledialog.askinteger("Input", "Vui lòng nhập năm bắt đầu:")
        end_year = simpledialog.askinteger("Input", "Vui lòng nhập năm kết thúc:")
        
        if variable_selection and start_year is not None and end_year is not None:
            self.storm_plotter.analyze_trends(variable_selection, start_year, end_year)

    #hàm này được gọi nếu người dùng chọn chức năng 'Thống kê số lượng cơn bão theo dạng bão' trong hàm thong_ke
    def view_storms_by_type(self):
        start_year = simpledialog.askinteger("Input", "Vui lòng nhập năm bắt đầu:")
        end_year = simpledialog.askinteger("Input", "Vui lòng nhập năm kết thúc:")
        if start_year is not None and end_year is not None:
            self.storm_plotter.plot_storm_by_type(start_year, end_year)       

    #hàm này được gọi nếu người dùng chọn chức năng "Thống kê số cơn bão theo từng năm" trong hàm thong_ke
    def view_storms_by_year(self):
        start_year = simpledialog.askinteger("Input", "Vui lòng nhập năm bắt đầu:")
        end_year = simpledialog.askinteger("Input", "Vui lòng nhập năm kết thúc:")
        if start_year is not None and end_year is not None:
            self.storm_plotter.plot_storms(start_year, end_year)
            
            
    #hàm này được gọi nếu người dùng chọn chức năng "Thống kê số cơn bão theo từng tháng" trong hàm thong_ke
    def view_storms_by_month(self):
        start_year = simpledialog.askinteger("Input", "Vui lòng nhập năm bắt đầu:")
        end_year = simpledialog.askinteger("Input", "Vui lòng nhập năm kết thúc:")
        if start_year is not None and end_year is not None:
        # Implement the function to plot storms by month
            self.storm_plotter.plot_storms_by_month(start_year, end_year)


    #hàm này được gọi nếu người dùng chọn chức năng "Thống kê vị trí các cơn bão" trong hàm thong_ke
    def view_storm_path(self):
        year = simpledialog.askinteger("Input", "Nhập năm:")
        if year is not None:
            # Implement the function to plot storm paths
            self.storm_plotter.plot_storm_address(year)
            
            
    #hàm này được gọi nếu người dùng chọn chức năng "Giá trị trung bình của các biến dữ liệu trong quá trình bão hình thành"   
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
            
            # Tạo checkbox "Chọn tất cả"
            select_all_var = tk.IntVar()
            select_all_chk = tk.Checkbutton(checkbox_frame_variable, text="Chọn tất cả", variable=select_all_var,command=lambda: self.select_all_variables(select_all_var.get()))
            select_all_chk.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            # Tạo checkbox cho từng biến
            for index, row in list_table.iterrows():
                var = tk.IntVar()
                chk = tk.Checkbutton(checkbox_frame_variable, text=f"{row['Ý nghĩa']}", variable=var)
                chk.grid(row=(index // columns) + 1, column=index % columns, sticky="w", padx=10, pady=5)
                self.selected_variables.append((var, row['Tên biến']))  # Lưu trạng thái và tên biến

            # Thêm nút để xác nhận lựa chọn
            confirm_button = tk.Button(info_window, text="Xem thông tin các cơn bão và biến", command=self.confirm_storm_and_variable_choices)
            confirm_button.pack()
            
    #hàm này tạo 1 checkbox để người dùng chọn tất cả các biến        
    def select_all_variables(self, select_all):
        for var, _ in self.selected_variables:
            var.set(select_all)
    
    #hàm này gọi đến hàm biểu diễn các giá trị trung bình của các cơn bão trong lớp StormPlotter
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