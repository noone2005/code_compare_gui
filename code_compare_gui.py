import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext, filedialog
import difflib
from typing import List
import sys
import io
from contextlib import redirect_stdout
import traceback

class CodeCompareGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("大飞Python代码对比工具")
        self.root.geometry("1500x800")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建三列布局
        self.create_columns()
        
        # 创建底部按钮
        self.create_buttons()
        
    def create_columns(self):
        """创建三列布局"""
        # 左侧标准代码区
        self.left_frame = ttk.LabelFrame(self.main_frame, text="标准代码")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 创建标准代码的行号和文本框容器
        standard_container = ttk.Frame(self.left_frame)
        standard_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标准代码的行号显示
        self.standard_line_numbers = tk.Text(
            standard_container,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background='lightgray',
            state='disabled',
            font=('Consolas', 11)
        )
        self.standard_line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # 标准代码文本框
        self.standard_code = scrolledtext.ScrolledText(
            standard_container,
            wrap=tk.NONE,
            width=40,
            height=35,
            font=('Consolas', 11)
        )
        self.standard_code.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 同步标准代码的滚动
        self.standard_code.vscrollbar = self.standard_code.vbar
        self.standard_code.vscrollbar.configure(command=self._on_standard_scroll)
        self.standard_code.configure(yscrollcommand=self._on_standard_scroll_set)
        
        # 中间待检查代码区
        self.middle_frame = ttk.LabelFrame(self.main_frame, text="待检查代码")
        self.middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 创建待检查代码的行号和文本框容器
        check_container = ttk.Frame(self.middle_frame)
        check_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 待检查代码的行号显示
        self.check_line_numbers = tk.Text(
            check_container,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background='lightgray',
            state='disabled',
            font=('Consolas', 11)
        )
        self.check_line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # 待检查代码文本框
        self.check_code = scrolledtext.ScrolledText(
            check_container,
            wrap=tk.NONE,
            width=40,
            height=35,
            font=('Consolas', 11)
        )
        self.check_code.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 同步待检查代码的滚动
        self.check_code.vscrollbar = self.check_code.vbar
        self.check_code.vscrollbar.configure(command=self._on_check_scroll)
        self.check_code.configure(yscrollcommand=self._on_check_scroll_set)
        
        # 右侧对比结果区
        self.right_frame = ttk.LabelFrame(self.main_frame, text="对比结果")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.result_display = scrolledtext.ScrolledText(
            self.right_frame,
            wrap=tk.NONE,
            width=40,
            height=35,
            font=('Consolas', 11)
        )
        self.result_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置标签和文本标签
        self.result_display.tag_config('add', foreground='blue')
        self.result_display.tag_config('remove', foreground='red')
        self.result_display.tag_config('info', foreground='green')
        
        # 绑定文本更改事件
        self.standard_code.bind('<Key>', self._update_standard_line_numbers)
        self.standard_code.bind('<MouseWheel>', self._update_standard_line_numbers)
        self.check_code.bind('<Key>', self._update_check_line_numbers)
        self.check_code.bind('<MouseWheel>', self._update_check_line_numbers)
        
    def create_buttons(self):
        """创建底部按钮"""
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 打开标准代码按钮
        self.open_standard_btn = ttk.Button(
            self.button_frame,
            text="打开标准代码",
            command=self.open_standard_file
        )
        self.open_standard_btn.pack(side=tk.LEFT, padx=5)
        
        # 运行按钮
        self.run_btn = ttk.Button(
            self.button_frame,
            text="运行代码",
            command=self.run_both_codes
        )
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        self.clear_btn = ttk.Button(
            self.button_frame,
            text="清空所有",
            command=self.clear_all
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 对比按钮
        self.compare_btn = ttk.Button(
            self.button_frame,
            text="开始对比",
            command=self.compare_code
        )
        self.compare_btn.pack(side=tk.RIGHT, padx=5)
        
    def _update_line_numbers(self, text_widget, line_numbers_widget):
        """更新行号"""
        line_numbers_widget.config(state='normal')
        line_numbers_widget.delete('1.0', tk.END)
        
        # 获取总行数
        text_content = text_widget.get('1.0', tk.END)
        lines = text_content.count('\n')
        if text_content.endswith('\n'):
            lines -= 1
        
        # 生成行号文本
        line_numbers_text = '\n'.join(str(i).rjust(3) for i in range(1, lines + 2))
        line_numbers_widget.insert('1.0', line_numbers_text)
        line_numbers_widget.config(state='disabled')

    def _update_standard_line_numbers(self, event=None):
        """更新标准代码的行号"""
        self._update_line_numbers(self.standard_code, self.standard_line_numbers)

    def _update_check_line_numbers(self, event=None):
        """更新待检查代码的行号"""
        self._update_line_numbers(self.check_code, self.check_line_numbers)

    def _on_standard_scroll(self, *args):
        """同步标准代码的滚动"""
        self.standard_code.yview(*args)
        self.standard_line_numbers.yview(*args)

    def _on_standard_scroll_set(self, *args):
        """设置标准代码的滚动位置"""
        self.standard_line_numbers.yview_moveto(args[0])
        self.standard_code.vscrollbar.set(*args)

    def _on_check_scroll(self, *args):
        """同步待检查代码的滚动"""
        self.check_code.yview(*args)
        self.check_line_numbers.yview(*args)

    def _on_check_scroll_set(self, *args):
        """设置待检查代码的滚动位置"""
        self.check_line_numbers.yview_moveto(args[0])
        self.check_code.vscrollbar.set(*args)

    def open_standard_file(self):
        """打开标准代码文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.standard_code.delete('1.0', tk.END)
                    self.standard_code.insert('1.0', content)
                    self._update_standard_line_numbers()  # 更新行号
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")
                
    def clear_all(self):
        """清空所有文本框"""
        self.standard_code.delete('1.0', tk.END)
        self.check_code.delete('1.0', tk.END)
        self.result_display.delete('1.0', tk.END)
        self._update_standard_line_numbers()  # 更新行号
        self._update_check_line_numbers()  # 更新行号
        
    def compare_code(self):
        """执行代码对比"""
        # 获取代码内容并过滤注释行
        standard_code = [line for line in self.standard_code.get('1.0', tk.END).splitlines() 
                        if not line.strip().startswith('#')]
        check_code = [line for line in self.check_code.get('1.0', tk.END).splitlines() 
                      if not line.strip().startswith('#')]
        
        # 清空结果显示
        self.result_display.delete('1.0', tk.END)
        
        # 使用difflib进行对比
        differ = difflib.Differ()
        diff = list(differ.compare(standard_code, check_code))
        
        # 显示带行号的对比结果
        standard_line = 1  # 标准代码行号
        check_line = 1    # 待检查代码行号
        
        for line in diff:
            if line.startswith('  '):  # 相同的行
                line_text = f"{standard_line:3d}|{check_line:3d}| {line[2:]}\n"
                self.result_display.insert(tk.END, line_text)
                standard_line += 1
                check_line += 1
            elif line.startswith('- '):  # 标准代码中有，待检查代码中没有
                line_text = f"{standard_line:3d}|   | {line[2:]}\n"
                self.result_display.insert(tk.END, line_text, 'remove')
                standard_line += 1
            elif line.startswith('+ '):  # 标准代码中没有，待检查代码中有
                line_text = f"   |{check_line:3d}| {line[2:]}\n"
                self.result_display.insert(tk.END, line_text, 'add')
                check_line += 1
            elif line.startswith('? '):  # 忽略差异标记行
                continue

    def run_code(self, code: str) -> tuple:
        """运行代码并返回输出结果和错误信息"""
        output = io.StringIO()
        error_output = io.StringIO()
        
        try:
            # 重定向标准输出和错误输出
            with redirect_stdout(output):
                # 在独立的命名空间中执行代码
                namespace = {}
                exec(code, namespace)
            return output.getvalue(), None
        except Exception as e:
            error_msg = traceback.format_exc()
            return None, error_msg
        finally:
            output.close()
            error_output.close()

    def run_both_codes(self):
        """运行两份代码并显示结果"""
        self.result_display.delete('1.0', tk.END)
        
        # 运行标准代码
        standard_code = self.standard_code.get('1.0', tk.END)
        self.result_display.insert(tk.END, "标准代码运行结果：\n", 'info')
        standard_output, standard_error = self.run_code(standard_code)
        
        if standard_output is not None:
            self.result_display.insert(tk.END, standard_output + "\n", 'add')
        if standard_error is not None:
            self.result_display.insert(tk.END, "错误：\n" + standard_error + "\n", 'remove')
        
        self.result_display.insert(tk.END, "\n" + "-" * 40 + "\n\n", 'info')
        
        # 运行待检查代码
        check_code = self.check_code.get('1.0', tk.END)
        self.result_display.insert(tk.END, "待检查代码运行结果：\n", 'info')
        check_output, check_error = self.run_code(check_code)
        
        if check_output is not None:
            self.result_display.insert(tk.END, check_output + "\n", 'add')
        if check_error is not None:
            self.result_display.insert(tk.END, "错误：\n" + check_error + "\n", 'remove')
            
        # 如果两份代码都运行成功，对比输出结果
        if standard_output is not None and check_output is not None:
            self.result_display.insert(tk.END, "\n" + "-" * 40 + "\n", 'info')
            if standard_output == check_output:
                self.result_display.insert(tk.END, "\n✅ 运行结果完全相同！\n", 'info')
            else:
                self.result_display.insert(tk.END, "\n❌ 运行结果不同！\n", 'remove')
                # 显示具体差异
                self.result_display.insert(tk.END, "\n输出差异对比：\n", 'info')
                differ = difflib.Differ()
                diff = list(differ.compare(standard_output.splitlines(), 
                                        check_output.splitlines()))
                for line in diff:
                    if line.startswith('+ '):
                        self.result_display.insert(tk.END, line + '\n', 'add')
                    elif line.startswith('- '):
                        self.result_display.insert(tk.END, line + '\n', 'remove')
                    elif line.startswith('? '):
                        continue
                    else:
                        self.result_display.insert(tk.END, line + '\n')

def main():
    root = tk.Tk()
    app = CodeCompareGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main() 