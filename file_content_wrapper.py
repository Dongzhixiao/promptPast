
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
        
        # Clear All button
        clear_btn = tk.Button(
            control_frame,
            text="清空全部",
            command=self.clear_all
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Process button
        process_btn = tk.Button(
            control_frame,
            text="处理文件内容",
            command=self.process_files
        )
        process_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame for files listbox with scrollbars
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        y_scroll = tk.Scrollbar(list_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        x_scroll = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Selected files listbox
        self.files_listbox = tk.Listbox(
            list_frame,
            width=80,
            height=15,
            selectmode=tk.EXTENDED,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        y_scroll.config(command=self.files_listbox.yview)
        x_scroll.config(command=self.files_listbox.xview)
        
        # Bind single click to toggle selection
        self.files_listbox.bind('<Button-1>', self.toggle_selection)
        
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
        
        # Help button
        help_btn = tk.Button(
            self.root,
            text="使用说明",
            command=self.show_help
        )
        help_btn.pack(pady=5)
        
        # Character count label
        self.char_count_label = tk.Label(
            self.root,
            text="字符数: 0",
            fg="gray"
        )
        self.char_count_label.pack()
        
        # Bind text modification event
        self.content_text.bind('<<Modified>>', self.update_char_count)
        self.content_text.bind('<KeyRelease>', self.update_char_count)
    
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
                    not file_path.lower().endswith(('.exe', '.dll', '.bin', '.zip', '.docx', '.ipynb'))):
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
            
            if not file_exists and not file_path.lower().endswith(('.exe', '.dll', '.bin', '.zip', '.docx', '.ipynb')):
                self.selected_files.append(file_path)
                added_files = True
        
        # Update listbox if files were added
        if added_files:
            self.update_files_list()
    
    def toggle_selection(self, event):
        # Get clicked item index
        index = self.files_listbox.nearest(event.y)
        
        # Toggle selection state
        if index in self.files_listbox.curselection():
            self.files_listbox.selection_clear(index)
        else:
            self.files_listbox.selection_set(index)
        
        # Prevent default selection behavior
        return 'break'
    
    def remove_selected(self):
        # Remove all selected items at once
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            return
            
        # Remove from selected_files list
        for i in reversed(sorted(selected_indices)):
            self.selected_files.pop(i)
            
        self.update_files_list()
    
    def update_files_list(self):
        # Update listbox with current files
        self.files_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.files_listbox.insert(tk.END, file)
            
    def update_char_count(self, event=None):
        # Update character count
        content = self.content_text.get(1.0, tk.END)
        char_count = len(content)
        self.char_count_label.config(text=f"字符数: {char_count}")
        return "break"  # Prevent default event handling

    def clear_all(self):
        # Clear all selected files
        self.selected_files = []
        self.update_files_list()
        self.content_text.delete(1.0, tk.END)
        self.char_count_label.config(text="字符数: 0")
    
    def process_files(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "没有选择任何文件!")
            return
        
        # Pre-check files for readability
        error_files = []
        for file_path in self.selected_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
            except Exception:
                error_files.append(file_path)
        
        # Block processing if problematic files found
        if error_files:
            file_list = '\n'.join(os.path.basename(f) for f in error_files)
            messagebox.showwarning(
                "警告", 
                f"以下文件无法处理，已自动选中:\n{file_list}\n请移除这些文件后再试"
            )
            # Select problematic files in listbox
            self.files_listbox.selection_clear(0, tk.END)
            for i, file_path in enumerate(self.selected_files):
                if file_path in error_files:
                    self.files_listbox.selection_set(i)
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
        footer = f"\n\n请仔细阅读上述{tags}标签里面的内容，然后按照下面的要求进行回复或处理："
        self.content_text.insert(tk.END, footer)
        
        # Update character count
        content = self.content_text.get(1.0, tk.END)
        char_count = len(content)
        self.char_count_label.config(text=f"字符数: {char_count}")
    
    def show_help(self):
        """Show help message with usage instructions"""
        help_text = """
文件内容包装神器 - 让批量文件处理变得轻松高效！

✨ 核心功能：
1. 一键批量处理多个文件内容，自动添加<filename>标签包装
2. 智能生成大模型提示语，引导模型理解上下文
3. 智能过滤系统文件，保护您的数据安全  
4. 直观的GUI界面，操作简单易上手
5. 处理结果可直接复制到剪贴板，一键粘贴提问

🔥 为什么选择这个工具？
- 大模型最佳搭档：自动<filename>标签完美组织多文件上下文
- 智能提示生成：自动添加引导语让模型更好理解内容
- 告别重复劳动：不再需要手动整理和拼接文件内容
- 完美格式保持：严格的标签包装确保内容边界清晰
- 安全无忧：自动跳过.exe/.dll等系统文件

🚀 大语言模型最佳搭档：
- 为DeepSeek/Claude等大模型准备提问材料
- 一键整理代码/文档作为上下文参考
- 批量处理多个文件内容作为知识背景
- 自动格式化内容便于模型理解
- 快速构建多文件知识库供模型参考

📝 使用方法：
1. 点击"选择文件夹"或"选择文件"按钮添加文件
2. 在列表中可预览和移除已选文件
3. 点击"处理文件内容"按钮生成格式化内容
4. 点击"复制内容"按钮将结果复制到剪贴板

💡 大模型提问小贴士：
1. 选择相关代码/文档文件（支持多选）
2. 点击"处理文件内容"生成格式化内容
   - 每个文件自动添加<filename>标签包装
   - 末尾添加智能提示语引导模型理解
3. 复制全部内容粘贴到模型提问中
4. 模型将获得：
   - 清晰的标签划分的多文件上下文
   - 明确的处理指引提示语
5. 文件名标签确保模型准确识别内容来源

版本: 1.0
作者: 智能文件处理专家
"""
        messagebox.showinfo("使用说明", help_text)

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
