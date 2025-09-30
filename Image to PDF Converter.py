# Image to PDF Converter (Tkinter + Pillow)
# This program allows the user to select multiple JPEG/PNG images,
# reorder them in a list, and export all of them into a single PDF file.
# Quick instruction to create an .exe (Windows):
#   pyinstaller --onefile --noconsole your_script.py

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def resource_path(rel_path):
    """Support function for PyInstaller to locate resources"""
    try:
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

class ImageToPDFApp:
    def __init__(self, master):
        """Initialize the application GUI"""
        self.master = master
        master.title("Image to PDF")
        master.minsize(640, 400)

        # Main frame
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Listbox + Scrollbar
        self.scroll = tk.Scrollbar(self.frame)
        # self.scroll.pack(side=tk.RIGHT, fill=tk.Y)  # Uncomment if you want visible scrollbar

        self.listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE, yscrollcommand=self.scroll.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll.config(command=self.listbox.yview)

        # Buttons frame
        self.btns = tk.Frame(self.frame)
        self.btns.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Action buttons
        tk.Button(self.btns, text="Add images", command=self.add_images).pack(fill='x', pady=2)
        tk.Button(self.btns, text="Remove selected", command=self.remove_selected).pack(fill='x', pady=2)
        tk.Button(self.btns, text="Move ↑", command=lambda: self.move(-1)).pack(fill='x', pady=2)
        tk.Button(self.btns, text="Move ↓", command=lambda: self.move(1)).pack(fill='x', pady=2)
        tk.Button(self.btns, text="Clear list", command=self.clear_list).pack(fill='x', pady=2)

        # Spacer
        tk.Frame(self.btns, height=10).pack()

        # Save button
        tk.Button(self.btns, text="Save as PDF", command=self.save_pdf, height=2).pack(fill='x', pady=6)

        # Help button
        tk.Button(self.btns, text="Help", command=self.show_help).pack(fill='x', pady=2)

    def add_images(self):
        """Open file dialog and add selected images to the listbox"""
        filetypes = [
            ("Images", "*.jpg;*.jpeg;*.png"),
            ("JPEG", "*.jpg;*.jpeg"),
            ("PNG", "*.png"),
            ("All files", "*.*"),
        ]
        paths = filedialog.askopenfilenames(title="Select images", filetypes=filetypes)
        if not paths:
            return
        for p in paths:
            self.listbox.insert(tk.END, p)

    def remove_selected(self):
        """Remove the currently selected image from the listbox"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Attention", "Select an item to remove.")
            return
        self.listbox.delete(sel[0])

    def move(self, direction: int):
        """Move the selected image up or down in the list"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Attention", "Select an item to move.")
            return
        idx = sel[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= self.listbox.size():
            return
        text = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(new_idx, text)
        self.listbox.selection_set(new_idx)

    def clear_list(self):
        """Clear the listbox"""
        self.listbox.delete(0, tk.END)

    def show_help(self):
        """Show a message box with usage instructions"""
        message = (
            "How to use:\n"
            "1) Click 'Add images' and select JPEG/PNG files.\n"
            "2) Reorder with 'Move ↑' and 'Move ↓'.\n"
            "3) Click 'Save as PDF' to generate a single PDF file.\n\n"
            "Tips:\n"
            "- Images are automatically converted to RGB.\n"
            "- Each image becomes a page in the PDF.\n"
            "- If an image fails to open, check file integrity."
        )
        messagebox.showinfo("Help", message)

    def save_pdf(self):
        """Save all selected images into a single PDF file"""
        n = self.listbox.size()
        if n == 0:
            messagebox.showwarning("Empty list", "Add at least one image.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="images.pdf"
        )
        if not out_path:
            return

        try:
            images = []
            for i in range(n):
                path = self.listbox.get(i)
                im = Image.open(path)
                # Convert to RGB (PDF does not support transparency properly)
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                else:
                    im = im.convert("RGB")
                images.append(im)

            # Save: first image + append the rest
            first, rest = images[0], images[1:]
            first.save(out_path, save_all=True, append_images=rest, format="PDF")
            messagebox.showinfo("Done!", f"PDF saved at:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Save error", f"An error occurred:\n{e}")

def main():
    """Start the Tkinter application"""
    root = tk.Tk()
    app = ImageToPDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
