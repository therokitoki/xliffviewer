import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from lxml import etree
import os
import ctypes

class UniversalXliffViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("XLIFF Viewer")
        self.geometry("1000x600")
        
        icon_path = os.path.join(os.path.dirname(__file__), "data", "viewer.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self._setup_ui()

    def _setup_ui(self):
        
        top_frame = tk.Frame(self, pady=10)
        top_frame.pack(fill="x")

        tk.Button(top_frame, text="Open file", command=self.load_file, padx=10).pack(side="left", padx=20)

        # search bar
        tk.Label(top_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_tree)
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side="left", padx=5)

        self.status_label = tk.Label(top_frame, text="No file loaded", fg="gray")
        self.status_label.pack(side="right", padx=20)

    
        table_frame = tk.Frame(self)
        table_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # XLIFF view

        columns = ("id", "source", "target", "state")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("source", width=400, anchor="w", stretch=True)
        self.tree.column("target", width=400, anchor="w", stretch=True)
        self.tree.column("state", width=100, anchor="center")

        self.tree.heading("id", text="ID")
        self.tree.heading("source", text="Source")
        self.tree.heading("target", text="Target")
        self.tree.heading("state", text="Status")

        # Scrollbars
        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vertical_scrollbar.grid(row=0, column=1, sticky='ns')
        horizontal_scrollbar.grid(row=1, column=0, sticky='ew')

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Reading Pane
        self.preview_text = tk.Text(self, height=6, state="disabled", wrap="word", font=("Segoe UI", 10))
        self.preview_text.pack(fill="x", padx=20, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.segment_select)

        self.all_data = []

    def segment_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        source, target = item["values"][1], item["values"][2]
        
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, f"SOURCE:\n{source}\n\nTARGET:\n{target}")
        self.preview_text.config(state="disabled")
        
    def load_file(self):
        file_types = [
            ("XLIFF Files", "*.xliff *.sdlxliff *.mxliff *.mqxliff"),
            ("All files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select XLIFF File", filetypes=file_types)
        
        if path:
            try:
                self.parse_xliff(path)
                self.status_label.config(text=f"File: {os.path.basename(path)}", fg="green")
            except Exception as e:
                messagebox.showerror("Parser Error", f"Could not read the file:\n{str(e)}")

    def parse_xliff(self, path):
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.all_data = []

            parser = etree.XMLParser(recover=True)
            tree = etree.parse(path, parser)
            units = tree.xpath("//*[local-name()='trans-unit']")
            
            if not units:
                messagebox.showwarning("Warning", "No translation units found.")
                return

            for unit in units:
                u_id = unit.get("id", "-")
                if u_id.startswith("lockTU_"):
                    continue

                src_nodes = unit.xpath(".//*[local-name()='source']")
                tgt_nodes = unit.xpath(".//*[local-name()='target']")
                
                if len(src_nodes) > 0:
                    source_text = "".join(src_nodes[0].itertext()).strip()
                    if not source_text:
                        continue
                    
                    target_text = "".join(tgt_nodes[0].itertext()).strip() if tgt_nodes else ""
                    status_nodes = unit.xpath(".//@*[local-name()='conf' or local-name()='state']")
                    state = str(status_nodes[-1]) if status_nodes else "n/a"

                    row_values = (u_id, source_text, target_text, state)
                    self.all_data.append(row_values) 
                    
                    self.tree.insert("", "end", values=row_values)

    def filter_tree(self, *args):
            query = self.search_var.get().lower()
            
            # Clean the table
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for row in self.all_data:
                # Searches in Source, Target or Status
                if query in row[1].lower() or query in row[2].lower() or query in row[3].lower():
                    self.tree.insert("", "end", values=row)
if __name__ == "__main__":
    if os.name == 'nt':
        myappid = 'roki.viewer.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = UniversalXliffViewer()
    app.mainloop()