import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, Listbox, END, messagebox
import subprocess
from services.planner_service import run_full_planning
from pipelines.input_pipeline import preprocess_input

class LogFileAnalyzer:
    def __init__(self, root):
        self.root = root
        self.state_dir = None  # Lưu trữ state_dir của lần chạy gần nhất

        self.setup_proxy("http://192.168.5.8:3128")
        self.create_widgets()

    def setup_proxy(self, proxy_address):
        """Thiết lập proxy môi trường."""
        os.environ['http_proxy'] = proxy_address
        os.environ['https_proxy'] = proxy_address
        os.environ['HTTP_PROXY'] = proxy_address
        os.environ['HTTPS_PROXY'] = proxy_address

    def create_widgets(self):
        """Tạo và sắp xếp các widget trong cửa sổ chính."""
        self.entry_file_path, frame = self.create_file_selection_frame()
        self.text_result = self.create_result_display()
        self.listbox_files = self.create_file_listbox()
        self.text_file_content = self.create_file_content_display()
        self.status_label = self.create_status_label()

        # Nút RUN cạnh nút Load File
        button_run = tk.Button(frame, text="RUN", command=self.run_planning)
        button_run.grid(row=0, column=3, padx=5)

        # Nút mở thư mục
        button_open_dir = tk.Button(self.root, text="Open Directory", command=self.open_directory)
        button_open_dir.pack(pady=5)

    def create_file_selection_frame(self):
        """Tạo khung cho việc chọn file và nhập đường dẫn."""
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        label_file_path = tk.Label(frame, text="File Path:")
        label_file_path.grid(row=0, column=0, padx=5)
        
        entry_file_path = tk.Entry(frame, width=50)
        entry_file_path.grid(row=0, column=1, padx=5)
        
        button_load_file = tk.Button(frame, text="Load File", command=lambda: self.load_file(entry_file_path))
        button_load_file.grid(row=0, column=2, padx=5)

        return entry_file_path, frame

    def load_file(self, entry_widget):
        """Mở hộp thoại chọn file và cập nhật đường dẫn vào ô nhập liệu."""
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def run_planning(self):
        """Chạy logic xử lý từ việc nhập liệu và hiển thị kết quả."""
        file_path = self.entry_file_path.get().strip()
        
        if not file_path:
            # Hiển thị thông báo nếu chưa chọn file
            self.status_label.config(text="Sếp ơi chọn file đi đã")
            return

        # Hiển thị thông báo trạng thái
        self.status_label.config(text="Thằng đệ đang làm việc, đợi chút nhé...")
        self.root.update_idletasks()
        
        # Reset the result display area
        self.text_result.delete("1.0", tk.END)
        self.listbox_files.delete(0, END)
        self.text_file_content.delete("1.0", tk.END)
        
        user_input = f"""Bạn là một chuyên gia Forensic và đang cần parse log hệ thống để phân tích. Đường dẫn file: {file_path} 
        Bước 1: Lấy mẫu 12 dòng trong file
        Bước 2: Viết code python để chuyển dữ liệu từ file log về csv. Chú ý để giữ được đầy đủ các trường và lưu lại cùng vị trí với file log. File có thể rất lớn, hãy sử dụng thư viện tqdm và có thể encoding utf-8
        Bước 3: Kiểm tra lại số line của 2 file để chắc chắn file đã được parse xong và báo cáo tôi kết quả.
        """
        processed_input = preprocess_input(user_input)
        
        # Run the planning service and get the state directory
        _, self.state_dir = run_full_planning(processed_input)
        
        # Display contents of message_notify_log.txt
        log_path = os.path.join(self.state_dir, "message_notify_log.txt")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding='utf-8') as log_file:
                self.text_result.insert(tk.END, log_file.read())
        
        # List all files in the state_dir
        for filename in os.listdir(self.state_dir):
            self.listbox_files.insert(END, filename)
        
        # Set a command to load the file when clicked
        def on_file_select(event):
            selected_file = self.listbox_files.get(self.listbox_files.curselection())
            file_path = os.path.join(self.state_dir, selected_file)
            with open(file_path, "r", encoding='utf-8') as f:
                lines = ''.join(f.readlines()[:10])  # Read first 10 lines
                self.text_file_content.delete("1.0", tk.END)
                self.text_file_content.insert(tk.END, lines)
        
        self.listbox_files.bind('<<ListboxSelect>>', on_file_select)

        # Cập nhật trạng thái sau khi hoàn thành
        self.status_label.config(text="Kết thúc! Kiểm tra ")

    def open_directory(self):
        """Mở thư mục bằng trình quản lý tệp mặc định."""
        absolute_path = os.path.abspath(self.state_dir)
        if self.state_dir:
            if os.name == 'nt':  # Windows
                os.startfile(absolute_path)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.call(['open', self.state_dir])
            else:
                messagebox.showerror("Lỗi", "Không thể mở thư mục trên hệ điều hành này.")
        else:
            messagebox.showerror("Lỗi", "Chưa có thư mục nào được tạo.")

    def create_result_display(self):
        """Tạo hộp văn bản để hiển thị kết quả."""
        text_result = scrolledtext.ScrolledText(self.root, width=80, height=10)
        text_result.pack(pady=10)
        return text_result

    def create_file_listbox(self):
        """Tạo Listbox để liệt kê các file trong thư mục."""
        listbox_files = Listbox(self.root, width=80, height=10)
        listbox_files.pack(pady=10)
        return listbox_files

    def create_file_content_display(self):
        """Tạo hộp văn bản để hiển thị nội dung file."""
        text_file_content = scrolledtext.ScrolledText(self.root, width=80, height=10)
        text_file_content.pack(pady=10)
        return text_file_content

    def create_status_label(self):
        """Tạo nhãn để hiển thị thông báo trạng thái."""
        status_label = tk.Label(self.root, text="")
        status_label.pack(pady=5)
        return status_label

def main():
    root = tk.Tk()
    app = LogFileAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()