
import os
import json
import hashlib
import ctypes
import tkinter as tk

from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from PIL import Image

APP_NAME = "MovieFolderCovers"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp",
    ".webp", ".tif", ".tiff"
}

# مجلد حفظ البيانات على جهاز المستخدم
LOCAL_APPDATA = Path(
    os.environ.get("LOCALAPPDATA", str(Path.home()))
)

DATA_DIR = LOCAL_APPDATA / APP_NAME
ICONS_DIR = DATA_DIR / "icons"
CONFIG_FILE = DATA_DIR / "settings.json"

for directory in (DATA_DIR, ICONS_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def get_id(folder):
    value = os.path.normcase(os.path.abspath(folder))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_network(folder):
    """اكتشاف مجلدات الشبكة."""

    folder = os.path.abspath(folder)

    if folder.startswith("\\\\"):
        return True

    if os.name == "nt":
        drive = os.path.splitdrive(folder)[0]

        if drive:
            try:
                return ctypes.windll.kernel32.GetDriveTypeW(
                    drive + "\\"
                ) == 4
            except Exception:
                return False

    return False


def create_icon(image_path, icon_path):
    """تحويل صورة إلى أيقونة ICO."""

    with Image.open(image_path) as image:
        image = image.convert("RGB")

        width, height = image.size
        side = min(width, height)

        left = (width - side) // 2
        top = (height - side) // 2

        image = image.crop((
            left,
            top,
            left + side,
            top + side
        ))

        image = image.resize(
            (256, 256),
            Image.Resampling.LANCZOS
        )

        image.save(
            str(icon_path),
            format="ICO",
            sizes=[
                (256, 256),
                (128, 128),
                (64, 64),
                (48, 48),
                (32, 32),
                (16, 16)
            ]
        )


def find_image(folder):
    """البحث عن أول صورة داخل المجلد مباشرة."""

    try:
        images = sorted(
            file for file in Path(folder).iterdir()
            if file.is_file()
            and file.suffix.lower() in IMAGE_EXTENSIONS
        )

        return str(images[0]) if images else None

    except (OSError, PermissionError):
        return None


def apply_local_icon(folder, image_path):
    """تطبيق الغلاف على مجلد محلي فقط."""

    folder = Path(folder)

    if is_network(str(folder)):
        raise RuntimeError(
            "لا يمكن تعديل مجلد شبكة."
        )

    desktop_ini = folder / "desktop.ini"
    icon_path = folder / "folder_cover.ico"

    # عدم استبدال تخصيص موجود
    if desktop_ini.exists():
        raise RuntimeError(
            "يوجد desktop.ini مسبقاً. "
            "تم تجاوز المجلد حفاظاً على إعداداته."
        )

    create_icon(image_path, icon_path)

    desktop_ini.write_text(
        "[.ShellClassInfo]\n"
        "IconResource=folder_cover.ico,0\n",
        encoding="utf-16"
    )

    HIDDEN = 0x02
    SYSTEM = 0x04
    READONLY = 0x01

    set_attributes = (
        ctypes.windll.kernel32.SetFileAttributesW
    )

    get_attributes = (
        ctypes.windll.kernel32.GetFileAttributesW
    )

    if not set_attributes(
        str(desktop_ini),
        HIDDEN | SYSTEM
    ):
        raise RuntimeError(
            "تعذر ضبط خصائص desktop.ini"
        )

    old_attributes = get_attributes(str(folder))

    if old_attributes != 0xFFFFFFFF:
        if not set_attributes(
            str(folder),
            old_attributes | READONLY
        ):
            raise RuntimeError(
                "تعذر ضبط خصائص المجلد."
            )

    # تحديث مستكشف Windows
    ctypes.windll.shell32.SHChangeNotify(
        0x08000000, 0, None, None
    )


def create_network_shortcut(folder, image_path, output_dir):
    """إنشاء اختصار محلي لمجلد الشبكة دون الكتابة عليها."""

    import win32com.client

    output_dir = Path(output_dir)

    if is_network(str(output_dir)):
        raise RuntimeError(
            "مكان الاختصارات يجب أن يكون محلياً."
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    key = get_id(folder)

    icon_path = ICONS_DIR / f"{key}.ico"

    create_icon(image_path, icon_path)

    folder_name = Path(folder).name or "Network Folder"

    shortcut_path = (
        output_dir / f"{folder_name}_{key[:8]}.lnk"
    )

    shell = win32com.client.Dispatch(
        "WScript.Shell"
    )

    shortcut = shell.CreateShortcut(
        str(shortcut_path)
    )

    shortcut.TargetPath = os.path.abspath(folder)
    shortcut.WorkingDirectory = os.path.abspath(folder)
    shortcut.IconLocation = f"{icon_path},0"
    shortcut.Description = "Movie Folder Covers"

    shortcut.Save()

    return shortcut_path


class MovieFolderCovers:

    def __init__(self, root):

        self.root = root

        self.root.title("Movie Folder Covers")
        self.root.geometry("850x600")
        self.root.minsize(650, 450)

        self.config = self.load_config()

        self.folders = list(self.config.keys())

        self.network_output = (
            Path.home() / "Desktop" / "أغلفة الشبكة"
        )

        self.build_interface()
        self.refresh_list()

    def load_config(self):

        if CONFIG_FILE.exists():
            try:
                return json.loads(
                    CONFIG_FILE.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception:
                pass

        return {}

    def save_config(self):

        CONFIG_FILE.write_text(
            json.dumps(
                self.config,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

    def build_interface(self):

        header = tk.Frame(
            self.root,
            bg="#14213d",
            height=75
        )

        header.pack(fill="x")

        tk.Label(
            header,
            text="🎬 أغلفة المجلدات والأفلام",
            font=("Arial", 20, "bold"),
            bg="#14213d",
            fg="white"
        ).pack(pady=18)

        tk.Label(
            self.root,
            text="اختر المجلدات التي تريد إظهار أغلفتها",
            font=("Arial", 12)
        ).pack(pady=10)

        buttons = tk.Frame(self.root)
        buttons.pack(fill="x", padx=12)

        ttk.Button(
            buttons,
            text="إضافة مجلد",
            command=self.add_folder
        ).pack(side="right", padx=4)

        ttk.Button(
            buttons,
            text="إزالة المحدد",
            command=self.remove_folder
        ).pack(side="right", padx=4)

        ttk.Button(
            buttons,
            text="اختيار صورة الغلاف",
            command=self.choose_cover
        ).pack(side="right", padx=4)

        ttk.Button(
            buttons,
            text="تحديث الأغلفة",
            command=self.update_covers
        ).pack(side="right", padx=4)

        self.listbox = tk.Listbox(
            self.root,
            font=("Arial", 10),
            selectmode=tk.EXTENDED,
            height=17
        )

        self.listbox.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        ttk.Button(
            self.root,
            text="اختيار مكان حفظ اختصارات الشبكة",
            command=self.choose_network_output
        ).pack(pady=5)

        tk.Label(
            self.root,
            text="المحلي: تغيير أيقونة المجلد | الشبكة: اختصار محلي",
            font=("Arial", 10, "bold"),
            fg="#087443"
        ).pack(pady=7)

        tk.Label(
            self.root,
            text="لا يتم تعديل أو حذف أي ملف داخل مجلدات الشبكة.",
            fg="#555555"
        ).pack(pady=5)

    def refresh_list(self):

        self.listbox.delete(0, tk.END)

        for folder in self.folders:

            if is_network(folder):
                label = "🌐 شبكة - قراءة فقط"
            else:
                label = "💻 محلي"

            self.listbox.insert(
                tk.END,
                f"{label} | {folder}"
            )

    def add_folder(self):

        folder = filedialog.askdirectory(
            title="اختر مجلداً"
        )

        if not folder:
            return

        folder = os.path.abspath(folder)

        if folder not in self.folders:

            self.folders.append(folder)

            self.config[folder] = {
                "image": ""
            }

            self.save_config()
            self.refresh_list()

    def selected_folders(self):

        return [
            self.folders[index]
            for index in self.listbox.curselection()
        ]

    def remove_folder(self):

        selected = self.selected_folders()

        if not selected:
            messagebox.showwarning(
                "تنبيه",
                "حدد مجلداً أولاً."
            )
            return

        for folder in selected:

            if folder in self.folders:
                self.folders.remove(folder)

            self.config.pop(folder, None)

        self.save_config()
        self.refresh_list()

    def choose_cover(self):

        selected = self.selected_folders()

        if len(selected) != 1:
            messagebox.showwarning(
                "تنبيه",
                "حدد مجلداً واحداً لاختيار غلافه."
            )
            return

        folder = selected[0]

        image = filedialog.askopenfilename(
            title="اختر صورة الغلاف من داخل المجلد",
            initialdir=folder,
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff")
            ]
        )

        if not image:
            return

        if Path(image).parent.resolve() != Path(folder).resolve():
            messagebox.showwarning(
                "تنبيه",
                "اختر صورة موجودة مباشرة داخل المجلد."
            )
            return

        self.config.setdefault(folder, {})
        self.config[folder]["image"] = image

        self.save_config()

        messagebox.showinfo(
            "تم",
            "تم حفظ صورة الغلاف."
        )

    def choose_network_output(self):

        folder = filedialog.askdirectory(
            title="اختر مكان حفظ اختصارات الشبكة"
        )

        if not folder:
            return

        if is_network(folder):
            messagebox.showerror(
                "تنبيه",
                "اختر مكاناً محلياً على جهازك."
            )
            return

        self.network_output = Path(folder)

        messagebox.showinfo(
            "تم",
            f"سيتم حفظ الاختصارات هنا:\n{folder}"
        )

    def update_covers(self):

        selected = self.selected_folders()

        if not selected:
            messagebox.showwarning(
                "تنبيه",
                "حدد مجلداً واحداً أو أكثر."
            )
            return

        success = 0
        errors = []

        for folder in selected:

            try:

                if not os.path.isdir(folder):
                    raise RuntimeError(
                        "المجلد غير موجود أو غير متاح."
                    )

                saved = self.config.get(folder, {})
                image = saved.get("image", "")

                if not image or not os.path.isfile(image):
                    image = find_image(folder)

                if not image:
                    raise RuntimeError(
                        "لم يتم العثور على صورة داخل المجلد."
                    )

                if is_network(folder):

                    create_network_shortcut(
                        folder,
                        image,
                        self.network_output
                    )

                else:

                    apply_local_icon(
                        folder,
                        image
                    )

                self.config.setdefault(folder, {})
                self.config[folder]["image"] = image
                self.config[folder]["network"] = is_network(folder)

                success += 1

            except Exception as error:

                errors.append(
                    f"{folder}\n{error}"
                )

        self.save_config()

        result = f"تمت معالجة {success} مجلد بنجاح."

        if errors:
            result += "\n\nالمجلدات التي لم تكتمل:\n"
            result += "\n\n".join(errors[:8])

        messagebox.showinfo(
            "نتيجة العملية",
            result
        )


if __name__ == "__main__":

    if os.name != "nt":
        raise SystemExit(
            "هذا البرنامج مخصص لنظام Windows."
        )

    root = tk.Tk()

    app = MovieFolderCovers(root)

    root.mainloop()
