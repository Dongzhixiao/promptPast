import tkinter as tk
from tkinter import filedialog, messagebox
import os

class FileContentWrapper:
    def __init__(self, root):
        self.root = root
        self.root.title("文件内容包装器")
        
        # Variables
        self.selected_files = []
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Frame for file selection controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Select Folder button
        folder_btn = tk.Button(
            control_frame, 
            text="选择文件夹",
            command=self.select_folder
        )
        folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Select Files button
        files_btn = tk.Button(
            control_frame,
            text="选择文件",
            command=self.select_files
        )
        files_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove Selected button
        remove_btn = tk.Button(
            control_frame,
            text="移除选中",
            command=self.remove_selected
        )
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Process button
        process_btn = tk.Button(
            control_frame,
            text="处理文件内容",
            command=self.process_files
        )
        process_btn.pack(side=tk.LEFT, padx=5)
        
        # Selected files listbox
        self.files_listbox = tk.Listbox(
            self.root,
            width=80,
            height=15,
            selectmode=tk.EXTENDED
        )
        self.files_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Content display text
        tk.Label(self.root, text="处理后的内容:").pack()
        
        # Content frame with scrollbars
        content_frame = tk.Frame(self.root)
        content_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        y_scroll = tk.Scrollbar(content_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        x_scroll = tk.Scrollbar(content_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Content text box
        self.content_text = tk.Text(
            content_frame,
            width=80,
            height=15,
            wrap=tk.WORD,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        y_scroll.config(command=self.content_text.yview)
        x_scroll.config(command=self.content_text.xview)
        
        # Copy button
        copy_btn = tk.Button(
            self.root,
            text="复制内容",
            command=self.copy_content
        )
        copy_btn.pack(pady=5)
    
    def select_folder(self):
        # Select folder
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if folder_path:
            # Get only new files in selected folder (non-recursive)
            existing_files = set(self.selected_files)
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if (os.path.isfile(file_path) and 
                    file_path not in existing_files and
                    not file_path.lower().endswith(('.exe', '.dll', '.bin'))):
                    self.selected_files.append(file_path)
            self.update_files_list()

    def select_files(self):
        # Select only new files
        existing_files = set(self.selected_files)
        file_paths = filedialog.askopenfilenames(title="选择文件")
        added_files = False
        
        # Get all selected folder paths
        selected_folders = set()
        for path in self.selected_files:
            if os.path.isdir(path):
                selected_folders.add(path)
        
        for file_path in file_paths:
            # Check if file is already directly selected
            if file_path in existing_files:
                continue
                
            # Check if file is in any selected folder
            in_selected_folder = False
            for folder in selected_folders:
                if os.path.commonprefix([file_path, folder]) == folder:
                    # Also check if file exists in the folder
                    rel_path = os.path.relpath(file_path, folder)
                    if os.path.exists(os.path.join(folder, rel_path)):
                        in_selected_folder = True
                        break
                    
            # Check if file is already in selected_files (using normalized paths)
            file_exists = any(os.path.normpath(file_path) == os.path.normpath(f) 
                            for f in self.selected_files)
            
            if not file_exists and not file_path.lower().endswith(('.exe', '.dll', '.bin')):
                self.selected_files.append(file_path)
                added_files = True
        
        # Update listbox if files were added
        if added_files:
            self.update_files_list()
    
    def remove_selected(self):
        # Remove selected items from list
        selected_indices = self.files_listbox.curselection()
        for i in reversed(selected_indices):
            self.selected_files.pop(i)
        self.update_files_list()
    
    def update_files_list(self):
        # Update listbox with current files
        self.files_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.files_listbox.insert(tk.END, file)
    
    def process_files(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "没有选择任何文件!")
            return
        
        # Clear content text
        self.content_text.delete(1.0, tk.END)
        
        # Process each file
        for i, file_path in enumerate(self.selected_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Wrap content in filename tags
                filename = os.path.basename(file_path)
                wrapped_content = f"<{filename}>\n{content}\n</{filename}>"
                
                # Add to text box with spacing between files
                if i > 0:
                    self.content_text.insert(tk.END, "\n\n")
                self.content_text.insert(tk.END, wrapped_content)
            
            except Exception as e:
                messagebox.showerror("错误", f"处理文件失败: {file_path}\n{str(e)}")
        
        # Add footer text after processing all files
        filenames = [os.path.basename(f) for f in self.selected_files]
        tags = "".join(f"<{name}>" for name in filenames)
        footer = f"\n\n请仔细阅读上述{tags}标签里面的内容，然后按照下面的要求进行回复："
        self.content_text.insert(tk.END, footer)
    
    def copy_content(self):
        # Copy content to clipboard
        content = self.content_text.get(1.0, tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("成功", "内容已复制到剪贴板!")
        else:
            messagebox.showwarning("警告", "没有内容可复制!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileContentWrapper(root)
    root.mainloop()
