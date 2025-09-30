# Image Resizer (Tkinter + Pillow)
# This app lets you select multiple images (JPG/PNG), choose an output folder,
# define target width/height, optionally keep aspect ratio and auto-rotate via EXIF,
# then batch-resize and save them. 
# Quick .exe (Windows) build with PyInstaller:
#   pyinstaller --onefile --noconsole your_script.py

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps

APP_TITLE = "Image Resizer"

def resource_path(rel_path: str) -> str:
    """Support function for PyInstaller to locate bundled resources."""
    try:
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

class ImageResizerApp:
    def __init__(self, master: tk.Tk):
        """Initialize the GUI and state."""
        self.master = master
        master.title(APP_TITLE)
        master.minsize(720, 480)

        # --- Main containers
        self.root_frame = tk.Frame(master)
        self.root_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: listbox (input images)
        self.left = tk.Frame(self.root_frame)
        self.left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll = tk.Scrollbar(self.left)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(self.left, selectmode=tk.SINGLE, yscrollcommand=self.scroll.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll.config(command=self.listbox.yview)

        # Right: controls
        self.right = tk.Frame(self.root_frame)
        self.right.pack(side=tk.LEFT, fill=tk.Y, padx=12)

        # -- File controls
        tk.Label(self.right, text="Files").pack(anchor="w")
        tk.Button(self.right, text="Add images", command=self.add_images).pack(fill="x", pady=2)
        tk.Button(self.right, text="Remove selected", command=self.remove_selected).pack(fill="x", pady=2)
        tk.Button(self.right, text="Clear list", command=self.clear_list).pack(fill="x", pady=2)

        tk.Label(self.right, text=" ").pack()  # spacer

        # -- Output folder
        tk.Label(self.right, text="Output folder").pack(anchor="w")
        self.out_dir_var = tk.StringVar(value="")
        out_row = tk.Frame(self.right)
        out_row.pack(fill="x")
        self.out_dir_entry = tk.Entry(out_row, textvariable=self.out_dir_var)
        self.out_dir_entry.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Button(out_row, text="Browse", command=self.choose_output_dir).pack(side=tk.LEFT, padx=4)

        tk.Label(self.right, text=" ").pack()  # spacer

        # -- Size options
        tk.Label(self.right, text="Target size (pixels)").pack(anchor="w")
        size_row = tk.Frame(self.right)
        size_row.pack(fill="x")
        tk.Label(size_row, text="Width").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value="")
        tk.Entry(size_row, textvariable=self.width_var, width=7).pack(side=tk.LEFT, padx=4)

        tk.Label(size_row, text="Height").pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value="")
        tk.Entry(size_row, textvariable=self.height_var, width=7).pack(side=tk.LEFT, padx=4)

        # options
        self.keep_ratio_var = tk.BooleanVar(value=True)
        self.autorotate_var = tk.BooleanVar(value=True)
        self.add_suffix_var = tk.BooleanVar(value=True)

        tk.Checkbutton(self.right, text="Keep aspect ratio", variable=self.keep_ratio_var).pack(anchor="w")
        tk.Checkbutton(self.right, text="Auto-rotate (EXIF)", variable=self.autorotate_var).pack(anchor="w")
        tk.Checkbutton(self.right, text="Append size suffix to filename", variable=self.add_suffix_var).pack(anchor="w")

        tk.Label(self.right, text=" ").pack()  # spacer

        # -- Run + Help
        tk.Button(self.right, text="Resize & Save", command=self.resize_and_save, height=2).pack(fill="x", pady=6)
        tk.Button(self.right, text="Help", command=self.show_help).pack(fill="x", pady=2)

    # ----------------- UI Actions -----------------
    def add_images(self):
        """Add multiple images to the listbox."""
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
        """Remove currently selected list item."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Attention", "Select an item to remove.")
            return
        self.listbox.delete(sel[0])

    def clear_list(self):
        """Clear the files list."""
        self.listbox.delete(0, tk.END)

    def choose_output_dir(self):
        """Select the output directory."""
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.out_dir_var.set(folder)

    def show_help(self):
        """Show usage instructions."""
        msg = (
            "How to use:\n"
            "1) Click 'Add images' and select JPG/PNG files.\n"
            "2) Choose an output folder.\n"
            "3) Set target WIDTH and/or HEIGHT (pixels).\n"
            "   - If 'Keep aspect ratio' is ON:\n"
            "       * If both width and height are filled, image will be FIT within the box.\n"
            "       * If only one is filled, the other dimension is computed.\n"
            "   - If OFF, image is stretched to exactly width x height.\n"
            "4) (Optional) Auto-rotate via EXIF.\n"
            "5) Click 'Resize & Save'."
        )
        messagebox.showinfo("Help", msg)

    # ----------------- Core Logic -----------------
    def parse_int(self, s: str) -> int | None:
        """Parse a positive integer from string; return None if empty/invalid."""
        s = (s or "").strip()
        if not s:
            return None
        try:
            val = int(s)
            return val if val > 0 else None
        except Exception:
            return None

    def compute_target_size(self, w0: int, h0: int, w_t: int | None, h_t: int | None, keep_ratio: bool) -> tuple[int, int]:
        """
        Compute target (width, height) based on source size and user inputs.
        - If keep_ratio:
            * Both provided: fit inside box preserving ratio.
            * One provided: scale by that dimension.
        - If not keep_ratio:
            * Missing width or height falls back to original dimension.
        """
        if keep_ratio:
            if w_t and h_t:
                # Fit inside (w_t, h_t)
                scale = min(w_t / w0, h_t / h0)
                return max(1, int(w0 * scale)), max(1, int(h0 * scale))
            elif w_t and not h_t:
                scale = w_t / w0
                return w_t, max(1, int(h0 * scale))
            elif h_t and not w_t:
                scale = h_t / h0
                return max(1, int(w0 * scale)), h_t
            else:
                # Nothing provided -> keep original
                return w0, h0
        else:
            # Stretch to exact provided values; if missing, keep original
            return (w_t or w0), (h_t or h0)

    def resize_and_save(self):
        """Batch-resize selected images and save them to the chosen output folder."""
        count = self.listbox.size()
        if count == 0:
            messagebox.showwarning("Empty list", "Add at least one image.")
            return

        out_dir = self.out_dir_var.get().strip()
        if not out_dir:
            messagebox.showwarning("Missing output folder", "Choose an output folder first.")
            return
        os.makedirs(out_dir, exist_ok=True)

        w_t = self.parse_int(self.width_var.get())
        h_t = self.parse_int(self.height_var.get())
        keep_ratio = self.keep_ratio_var.get()
        autorotate = self.autorotate_var.get()
        add_suffix = self.add_suffix_var.get()

        if w_t is None and h_t is None:
            messagebox.showwarning("Missing size", "Provide at least WIDTH or HEIGHT.")
            return

        processed = 0
        errors = []

        for i in range(count):
            path = self.listbox.get(i)
            try:
                im = Image.open(path)

                # Auto-rotate using EXIF if requested
                if autorotate:
                    im = ImageOps.exif_transpose(im)

                w0, h0 = im.size
                new_w, new_h = self.compute_target_size(w0, h0, w_t, h_t, keep_ratio)

                # High-quality resampling
                im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Build output filename
                base = os.path.basename(path)
                name, ext = os.path.splitext(base)
                ext_lower = ext.lower()
                if ext_lower not in {".jpg", ".jpeg", ".png"}:
                    # default to .jpg if unknown
                    ext_lower = ".jpg"

                if add_suffix:
                    out_name = f"{name}_{new_w}x{new_h}{ext_lower}"
                else:
                    out_name = f"{name}{ext_lower}"

                out_path = os.path.join(out_dir, out_name)

                # Save preserving format by extension
                save_params = {}
                if ext_lower in {".jpg", ".jpeg"}:
                    # Ensure RGB for JPEG
                    if im_resized.mode in ("RGBA", "P"):
                        im_resized = im_resized.convert("RGB")
                    save_params["quality"] = 95  # good default
                    save_params["optimize"] = True

                im_resized.save(out_path, **save_params)
                processed += 1

            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        # Report
        if errors:
            messagebox.showwarning(
                "Completed with warnings",
                f"Processed: {processed}\nErrors: {len(errors)}\n\n" + "\n".join(errors[:10]) + ("\n..." if len(errors) > 10 else "")
            )
        else:
            messagebox.showinfo("Done!", f"Processed images: {processed}")

def main():
    """Create Tk root and run the application."""
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
