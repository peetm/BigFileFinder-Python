#!/usr/bin/env python3
"""
File Scanner GUI - Recursively scan folders and display files sorted by size
Allows selection and deletion of files
"""

import os
import time
import threading
import tkinter   as tk
from collections import deque
from tkinter     import ttk, filedialog, messagebox
from pathlib     import Path



class FileScannerGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Large File Scanner")
        self.root.geometry("1000x700")

        # Data structures
        self.file_list      = []  # List of tuples: (size, path)
        self.scanning       = False
        self.scan_thread    = None

        # Sorting strategy: use a max-heap approach with periodic sorting
        # We'll collect files and sort every N files to maintain sorted order
        self.sort_threshold     = 100  # Sort every 1000 files
        self.files_since_sort   = 0

        self.setup_ui()

    def setup_ui(self):

        """Create the user interface"""

        # Top frame - controls
        top_frame = ttk.Frame(self.root, padding = "10")
        top_frame.pack(fill = tk.X)

        # Folder selection
        ttk.Label(top_frame, text = "Selected Path:").pack(side = tk.LEFT, padx = (0, 5))

        self.path_var = tk.StringVar(value = "No folder selected")
        path_label = ttk.Label(top_frame, textvariable = self.path_var,relief = tk.SUNKEN, width = 50)
        path_label.pack(side = tk.LEFT, padx = (0, 10))

        self.browse_btn = ttk.Button(top_frame, text = "Browse...", command = self.browse_folder)
        self.browse_btn.pack(side = tk.LEFT, padx = 5)

        self.scan_btn = ttk.Button(top_frame, text = "Start Scan", command = self.start_scan, state = tk.DISABLED)
        self.scan_btn.pack(side = tk.LEFT, padx = 5)

        self.stop_btn = ttk.Button(top_frame, text = "Stop", command = self.stop_scan, state = tk.DISABLED)
        self.stop_btn.pack(side = tk.LEFT, padx = 5)

        # Progress frame
        progress_frame = ttk.Frame(self.root, padding = "10")
        progress_frame.pack(fill = tk.X)

        self.status_var = tk.StringVar(value = "Ready")
        ttk.Label(progress_frame, textvariable = self.status_var).pack(side = tk.LEFT)

        self.progress = ttk.Progressbar(progress_frame, mode = 'indeterminate')
        self.progress.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = 10)

        # File list frame
        list_frame = ttk.Frame(self.root, padding = "10")
        list_frame.pack(fill = tk.BOTH, expand = True)

        # Treeview for file list
        columns = ("size", "size_mb", "path")
        self.tree = ttk.Treeview(list_frame, columns = columns, show = "headings", selectmode = 'extended')

        self.tree.heading("size", text = "Size (bytes)")
        self.tree.heading("size_mb", text = "Size (MB)")
        self.tree.heading("path", text = "File Path")

        self.tree.column("size", width = 120, anchor = tk.E)
        self.tree.column("size_mb", width = 100, anchor = tk.E)
        self.tree.column("path", width = 600)

        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient = "vertical", command = self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient = "horizontal", command = self.tree.xview)
        self.tree.configure(yscrollcommand = vsb.set, xscrollcommand = hsb.set)

        self.tree.grid(row = 0, column = 0, sticky = 'nsew')
        vsb.grid(row = 0, column = 1, sticky = 'ns')
        hsb.grid(row = 1, column = 0, sticky = 'ew')

        list_frame.grid_rowconfigure(0, weight = 1)
        list_frame.grid_columnconfigure(0, weight = 1)

        # Bottom frame - action buttons
        bottom_frame = ttk.Frame(self.root, padding = "10")
        bottom_frame.pack(fill = tk.X)

        self.delete_btn = ttk.Button(bottom_frame, text = "Delete Selected Files", command = self.delete_selected, state = tk.DISABLED)
        self.delete_btn.pack(side = tk.LEFT, padx = 5)

        self.select_all_btn = ttk.Button(bottom_frame, text = "Select All", command = self.select_all, state = tk.DISABLED)
        self.select_all_btn.pack(side = tk.LEFT, padx = 5)

        self.clear_btn = ttk.Button(bottom_frame, text = "Clear Selection", command = self.clear_selection, state = tk.DISABLED)
        self.clear_btn.pack(side = tk.LEFT, padx = 5)

        ttk.Label(bottom_frame, textvariable = self.get_selection_info()).pack(side = tk.RIGHT, padx = 10)

    def browse_folder(self):

        """Open folder selection dialog"""

        folder = filedialog.askdirectory(title = "Select Folder or Drive to Scan")
        if folder:
            self.path_var.set(folder)
            self.scan_btn.config(state = tk.NORMAL)

    def start_scan(self):

        """Start the folder scanning process"""

        if self.scanning:

            return

        # Clear previous results
        self.file_list.clear()
        self.tree.delete(*self.tree.get_children())
        self.files_since_sort = 0

        # Update UI
        self.scanning = True
        self.scan_btn.config(state = tk.DISABLED)
        self.stop_btn.config(state = tk.NORMAL)
        self.browse_btn.config(state = tk.DISABLED)
        self.delete_btn.config(state = tk.DISABLED)
        self.select_all_btn.config(state = tk.DISABLED)
        self.clear_btn.config(state = tk.DISABLED)
        self.progress.start()

        # Start scanning in a separate thread
        self.scan_thread = threading.Thread(target = self.scan_folder, daemon = True)
        self.scan_thread.start()

    def stop_scan(self):

        """Stop the scanning process"""

        self.scanning = False
        self.status_var.set("Stopping scan...")

    def scan_folder(self):

        """Recursively scan folder and collect file information"""

        root_path = self.path_var.get()
        file_count = 0

        try:
            # Use os.walk for efficient recursive scanning
            for dirpath, dirnames, filenames in os.walk(root_path):
                if not self.scanning:
                    break

                for filename in filenames:
                    if not self.scanning:
                        break

                    try:
                        filepath = os.path.join(dirpath, filename)
                        size = os.path.getsize(filepath)

                        # Add to our list
                        self.file_list.append((size, filepath))
                        file_count += 1
                        self.files_since_sort += 1

                        # Periodic sorting - use insertion sort for near-sorted data
                        if self.files_since_sort >= self.sort_threshold:
                            self.sort_files()
                            self.files_since_sort = 0

                        # Update status periodically
                        if file_count % 100 == 0:
                            self.root.after(0, self.update_status, f"Scanning... {file_count} files found")

                    except (PermissionError, FileNotFoundError, OSError) as e:
                        # Skip files we can't access
                        continue

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Scan Error", str(e))

        # Final sort and display
        if self.scanning:
            self.root.after(0, self.finalize_scan, file_count)
        else:
            self.root.after(0, self.scan_cancelled, file_count)

    def sort_files(self):

        """Sort the file list by size (largest first)"""

        # Using reverse = True to get largest files first
        self.file_list.sort(reverse = True, key = lambda x: x[0])

    def update_status(self, message):

        """Update status label (called from main thread)"""

        self.status_var.set(message)

    def finalize_scan(self, file_count):

        """Final sort and populate the tree view"""

        self.status_var.set(f"Finalizing... sorting {file_count} files")

        # Final sort
        self.sort_files()

        # Populate tree view
        self.populate_tree()

        # Update UI
        self.scanning = False
        self.progress.stop()
        self.scan_btn.config(state = tk.NORMAL)
        self.stop_btn.config(state = tk.DISABLED)
        self.browse_btn.config(state = tk.NORMAL)
        self.delete_btn.config(state = tk.NORMAL)
        self.select_all_btn.config(state = tk.NORMAL)
        self.clear_btn.config(state = tk.NORMAL)

        total_size = sum(size for size, _ in self.file_list)
        self.status_var.set\
        (
            f"Scan complete: {file_count} files found, "
            f"Total size: {self.format_size(total_size)}"
        )

    def scan_cancelled(self, file_count):

        """Handle cancelled scan"""

        self.status_var.set(f"Scan cancelled: {file_count} files found before stopping")

        # Still sort and show what we found
        self.sort_files()
        self.populate_tree()

        # Update UI
        self.scanning = False
        self.progress.stop()
        self.scan_btn.config(state = tk.NORMAL)
        self.stop_btn.config(state = tk.DISABLED)
        self.browse_btn.config(state = tk.NORMAL)
        self.delete_btn.config(state = tk.NORMAL)
        self.select_all_btn.config(state = tk.NORMAL)
        self.clear_btn.config(state = tk.NORMAL)

    def populate_tree(self):

        """Populate the treeview with sorted file list"""

        # Clear existing items
        self.tree.delete(*self.tree.get_children())

        # Add files to tree
        for size, path in self.file_list:
            size_mb = size / (1024 * 1024)
            self.tree.insert("", tk.END, values = \
            (
                f"{size:,}",
                f"{size_mb:.2f}",
                path
            ))

    def delete_selected(self):

        """Delete selected files after confirmation"""

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select files to delete")

            return

        # Get file paths and calculate total size
        files_to_delete = []
        total_size      = 0
        for item in selected:
            values = self.tree.item(item, "values")
            size   = int(values[0].replace(",", ""))
            path   = values[2]
            files_to_delete.append((size, path))
            total_size += size

        # Confirmation dialog
        message = \
        (
            f"Are you sure you want to delete {len(files_to_delete)} file(s)?\n\n"
            f"Total size: {self.format_size(total_size)}\n\n"
            f"This action cannot be undone!"
        )

        if not messagebox.askyesno("Confirm Deletion", message):

            return

        # Delete files
        deleted = 0
        failed  = []

        for size, path in files_to_delete:
            try:
                os.remove(path)
                deleted += 1
                # Remove from our data structures
                if (size, path) in self.file_list:
                    self.file_list.remove((size, path))
            except Exception as e:
                failed.append((path, str(e)))

        # Remove deleted items from tree
        for item in selected:
            values = self.tree.item(item, "values")
            path   = values[2]
            if path not in [f[0] for f in failed]:
                self.tree.delete(item)

        # Show results
        if failed:

            fail_msg = "\n".join([f"{p}: {e}" for p, e in failed[:10]])

            if len(failed) > 10:
                fail_msg += f"\n... and {len(failed) - 10} more"

            messagebox.showwarning\
            (
                "Deletion Complete with Errors",
                f"Deleted: {deleted} file(s)\nFailed: {len(failed)} file(s)\n\n{fail_msg}"
            )
        else:
            messagebox.showinfo\
            (
                "Deletion Complete",
                f"Successfully deleted {deleted} file(s)\n"
                f"Freed space: {self.format_size(total_size)}"
            )

    def select_all(self):

        """Select all items in the tree"""

        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def clear_selection(self):

        """Clear all selections"""

        self.tree.selection_remove(self.tree.selection())

    def get_selection_info(self):

        """Get information about current selection"""

        info_var = tk.StringVar(value = "")

        def update_info():
            selected = self.tree.selection()
            if selected:
                total_size = 0
                for item in selected:
                    values = self.tree.item(item, "values")
                    size = int(values[0].replace(",", ""))
                    total_size += size
                info_var.set(
                    f"Selected: {len(selected)} file(s), "
                    f"Total: {self.format_size(total_size)}"
                )
            else:
                info_var.set("")

            self.root.after(500, update_info)

        update_info()

        return info_var

    @staticmethod
    def format_size(size):

        """Format bytes to human readable format"""

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:

                return f"{size:.2f} {unit}"

            size /= 1024.0

        return f"{size:.2f} PB"


def main():
    root = tk.Tk()
    app  = FileScannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()