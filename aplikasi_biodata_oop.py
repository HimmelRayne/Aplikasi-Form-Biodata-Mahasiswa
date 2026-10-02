import datetime
import logging
import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


logging.basicConfig(
    filename="aplikasi_biodata.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class AplikasiBiodata(tk.Tk):

    USER_THEMES = {
        "admin": {
            "bg": "#e2e8f0",
            "primary": "#1e293b",
            "text": "#ffffff",
        },
        "user1": {
            "bg": "#d1fae5",
            "primary": "#065f46",
            "text": "#ffffff",
        },
        "mahasiswa": {
            "bg": "#fef3c7",
            "primary": "#78350f",
            "text": "#ffffff",
        },
        "ridwan": {
            "bg": "#e0e7ff",
            "primary": "#3730a3",
            "text": "#ffffff",
        },
    }

    DEFAULT_THEME = {
        "bg": "#ccfbf1",
        "primary": "#134e4a",
        "text": "#ffffff",
    }

    def __init__(self):
        super().__init__()

        self.title("Aplikasi Biodata Mahasiswa")
        self.geometry("600x850")
        self.resizable(True, True)

        self.users_db = {
            "admin": "123",
            "user1": "password1",
            "mahasiswa": "123456",
            "ridwan": "24106050043",
        }

        self.current_user = None
        self.frame_aktif = None
        self.data_sudah_disubmit = False
        self.data_biodata = None

        self.last_user_file = Path(__file__).with_name("last_user.txt")

        self._buat_tampilan_login()
        self._buat_tampilan_biodata()

        self._pindah_ke(self.frame_login)

        logging.info("Aplikasi dimulai")

    def _pindah_ke(self, frame_tujuan):
        """Berpindah antar frame."""
        if self.frame_aktif is not None:
            self.frame_aktif.pack_forget()

        self.frame_aktif = frame_tujuan
        self.frame_aktif.pack(fill=tk.BOTH, expand=True)

        if frame_tujuan == self.frame_login:
            self._muat_remembered_user()
            self.after(100, lambda: self.entry_username.focus_set())

        elif frame_tujuan == self.frame_biodata:
            self.after(100, lambda: self.entry_nama.focus_set())

    def _coba_login(self):
        """Memproses login pengguna."""
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        logging.info(f"Login attempt for username: {username}")

        if not username or not password:
            logging.warning(
                f"Empty credentials attempt for username: {username}"
            )
            messagebox.showwarning(
                "Login Gagal",
                "Username dan Password tidak boleh kosong."
            )
            self.entry_username.focus_set()
            return

        if len(username) < 3:
            logging.warning(f"Username too short: {username}")
            messagebox.showwarning(
                "Login Gagal",
                "Username minimal 3 karakter."
            )
            self.entry_username.focus_set()
            return

        if username in self.users_db and self.users_db[username] == password:
            self.current_user = username

            if self.check_remember.get():
                self._remember_user(username)
            else:
                self._hapus_remembered_user()

            logging.info(f"Successful login for user: {username}")

            messagebox.showinfo(
                "Login Berhasil",
                f"Selamat Datang, {username}!"
            )

            self._terapkan_tema_user()
            self._reset_form_biodata()
            self._update_title_with_user()
            self._pindah_ke(self.frame_biodata)

            self.entry_password.delete(0, tk.END)

            if not self.check_remember.get():
                self.entry_username.delete(0, tk.END)

            self._buat_menu()

        else:
            logging.warning(
                f"Failed login attempt for username: {username}"
            )

            messagebox.showerror(
                "Login Gagal",
                "Username atau Password salah."
            )

            self.entry_password.delete(0, tk.END)
            self.entry_username.focus_set()

    def _terapkan_tema_user(self):
        """Menerapkan tema berdasarkan user yang sedang login."""
        theme = self.USER_THEMES.get(
            self.current_user,
            self.DEFAULT_THEME
        )

        self.frame_biodata.config(bg=theme["bg"])

        self.label_judul.config(
            bg=theme["bg"],
            fg=theme["primary"]
        )

        self.frame_tombol_aksi.config(bg=theme["bg"])

        self.label_hasil.config(
            bg=theme["bg"],
            fg=theme["primary"],
            font=("Arial", 11, "bold"),
            padx=12,
            pady=10,
            relief=tk.FLAT,
            bd=0,
        )

    def _toggle_password(self):
        if self.entry_password.cget("show") == "*":
            self.entry_password.configure(show="")
            self.btn_toggle_pwd.configure(text="🙈")
        else:
            self.entry_password.configure(show="*")
            self.btn_toggle_pwd.configure(text="👁")

    def _remember_user(self, username):
        try:
            with self.last_user_file.open(
                "w",
                encoding="utf-8"
            ) as file:
                file.write(username)

            logging.info(f"Last user saved: {username}")

        except OSError as e:
            logging.error(
                f"Error saving last user: {str(e)}"
            )

    def _muat_remembered_user(self):
        try:
            if self.last_user_file.exists():
                username = self.last_user_file.read_text(
                    encoding="utf-8"
                ).strip()

                if username in self.users_db:
                    self.entry_username.delete(0, tk.END)
                    self.entry_username.insert(0, username)
                    self.check_remember.set(1)
                else:
                    self.check_remember.set(0)
            else:
                self.check_remember.set(0)

        except (OSError, UnicodeError) as e:
            logging.error(
                f"Error loading last user: {str(e)}"
            )
            self.check_remember.set(0)

    def _hapus_remembered_user(self):
        try:
            self.last_user_file.unlink(missing_ok=True)

        except OSError as e:
            logging.error(
                f"Error removing last user: {str(e)}"
            )

    def _update_title_with_user(self):
        if self.current_user:
            self.title(
                "Aplikasi Biodata Mahasiswa - "
                f"Logged in as: {self.current_user}"
            )
        else:
            self.title("Aplikasi Biodata Mahasiswa")

    def _reset_form_biodata(self):
        theme = self.USER_THEMES.get(
            self.current_user,
            self.DEFAULT_THEME
        )

        self.var_nama.set("")
        self.var_nim.set("")
        self.var_jurusan.set("")
        self.var_email.set("")
        self.var_telepon.set("")
        self.var_tanggal_lahir.set("")

        self.text_alamat.delete("1.0", tk.END)

        self.var_jk.set("Pria")
        self.var_setuju.set(0)

        self.data_sudah_disubmit = False
        self.data_biodata = None

        self.label_hasil.config(
            text="",
            bg=theme["bg"],
            fg=theme["primary"]
        )

        self.entry_nama.configure(bg="white")
        self.entry_nim.configure(bg="white")
        self.entry_jurusan.configure(bg="white")
        self.entry_email.configure(bg="white")
        self.entry_telepon.configure(bg="white")
        self.entry_tanggal_lahir.configure(bg="white")

        self.validate_form()

    def _hapus_menu(self):
        empty_menu = tk.Menu(self)
        self.config(menu=empty_menu)

    def _buat_tampilan_login(self):
        self._hapus_menu()

        self.frame_login = tk.Frame(
            master=self,
            padx=20,
            pady=100,
            bg="lightblue"
        )

        self.frame_login.grid_columnconfigure(0, weight=1)
        self.frame_login.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.frame_login,
            text="HALAMAN LOGIN",
            font=("Arial", 16, "bold"),
            bg="lightblue",
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            pady=20
        )

        tk.Label(
            self.frame_login,
            text="Username:",
            font=("Arial", 12),
            bg="lightblue"
        ).grid(
            row=1,
            column=0,
            sticky="W",
            pady=5
        )

        self.entry_username = tk.Entry(
            self.frame_login,
            font=("Arial", 12)
        )

        self.entry_username.grid(
            row=1,
            column=1,
            pady=5,
            sticky="EW"
        )

        tk.Label(
            self.frame_login,
            text="Password:",
            font=("Arial", 12),
            bg="lightblue"
        ).grid(
            row=2,
            column=0,
            sticky="W",
            pady=5
        )

        self.frame_pwd = tk.Frame(
            self.frame_login,
            bg="lightblue"
        )

        self.frame_pwd.grid(
            row=2,
            column=1,
            pady=5,
            sticky="EW"
        )

        self.frame_pwd.columnconfigure(0, weight=1)

        self.entry_password = tk.Entry(
            self.frame_pwd,
            font=("Arial", 12),
            show="*"
        )

        self.entry_password.grid(
            row=0,
            column=0,
            sticky="EW"
        )

        self.btn_toggle_pwd = tk.Button(
            self.frame_pwd,
            text="👁",
            font=("Arial", 9),
            width=3,
            command=self._toggle_password,
        )

        self.btn_toggle_pwd.grid(
            row=0,
            column=1,
            padx=(5, 0)
        )

        self.btn_login = tk.Button(
            self.frame_login,
            text="Login",
            font=("Arial", 12, "bold"),
            command=self._coba_login,
        )

        self.btn_login.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=20,
            sticky="EW"
        )

        self.entry_username.bind(
            "<Return>",
            lambda e: self.entry_password.focus_set()
        )

        self.entry_password.bind(
            "<Return>",
            lambda e: self._coba_login()
        )

        info_label = tk.Label(
            self.frame_login,
            text=(
                "Info: Username yang tersedia:\n"
                "admin (Tema Slate): 123\n"
                "user1 (Tema Emerald): password1 \n"
                "mahasiswa (Tema Amber): 123456\n"
                "ridwan (Tema Indigo): 24106050043"
            ),
            font=("Arial", 9),
            fg="gray",
            justify=tk.LEFT,
            bg="lightblue",
        )

        info_label.grid(
            row=4,
            column=0,
            columnspan=2,
            pady=10
        )

        self.check_remember = tk.IntVar()

        self.check_remember_user = tk.Checkbutton(
            self.frame_login,
            text="Ingat saya",
            variable=self.check_remember,
            font=("Arial", 10),
            bg="lightblue",
        )

        self.check_remember_user.grid(
            row=5,
            column=0,
            columnspan=2,
            pady=5
        )

    def _logout(self):
        if messagebox.askyesno(
            "Logout",
            f"Apakah {self.current_user} yakin ingin logout?"
        ):
            logging.info(
                f"User logout: {self.current_user}"
            )

            self.current_user = None

            self._update_title_with_user()

            self.entry_password.delete(0, tk.END)

            self.entry_password.configure(show="*")
            self.btn_toggle_pwd.configure(text="👁")

            self._reset_form_biodata()
            self._pindah_ke(self.frame_login)
            self._hapus_menu()

    def _buat_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(
            master=menu_bar,
            tearoff=0
        )

        file_menu.add_command(
            label="Simpan Hasil",
            command=self.simpan_hasil
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Logout",
            command=self._logout
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Keluar",
            command=self.keluar_aplikasi
        )

        menu_bar.add_cascade(
            label="File",
            menu=file_menu
        )

    def simpan_hasil(self):
        try:
            if not self.data_sudah_disubmit or not self.data_biodata:
                messagebox.showwarning(
                    "Peringatan",
                    "Tidak ada data untuk disimpan. "
                    "Mohon submit terlebih dahulu."
                )
                return

            hasil_tersimpan = self.label_hasil.cget("text")

            if not hasil_tersimpan:
                messagebox.showwarning(
                    "Peringatan",
                    "Tidak ada hasil biodata yang dapat disimpan."
                )
                return

            timestamp = datetime.datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            filename = (
                f"biodata_{self.current_user}_{timestamp}.txt"
            )

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    f"Data disimpan oleh: {self.current_user}\n"
                )

                file.write(
                    "Waktu penyimpanan: "
                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )

                file.write("-" * 50 + "\n")
                file.write(hasil_tersimpan)

            logging.info(
                f"Biodata saved by user: {self.current_user}"
            )

            messagebox.showinfo(
                "Info",
                f"Data berhasil disimpan ke file '{filename}'."
            )

        except PermissionError:
            messagebox.showerror(
                "Error",
                "Tidak memiliki izin untuk menyimpan "
                "file di lokasi ini."
            )

        except OSError as e:
            logging.error(
                f"Error saving biodata: {str(e)}"
            )

            messagebox.showerror(
                "Error",
                f"Terjadi kesalahan saat menyimpan file:\n{str(e)}"
            )

        except Exception as e:
            logging.error(
                f"Unexpected error while saving biodata: {str(e)}"
            )

            messagebox.showerror(
                "Error",
                f"Terjadi kesalahan:\n{str(e)}"
            )

    def _on_typing(self, event):
        event.widget.configure(bg="white")

    def _buat_tampilan_biodata(self):
        self.var_nama = tk.StringVar()
        self.var_nim = tk.StringVar()
        self.var_jurusan = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telepon = tk.StringVar()
        self.var_tanggal_lahir = tk.StringVar()
        self.var_jk = tk.StringVar(value="Pria")
        self.var_setuju = tk.IntVar()

        self.var_nama.trace_add(
            "write",
            self.validate_form
        )

        self.var_nim.trace_add(
            "write",
            self.validate_form
        )

        self.var_jurusan.trace_add(
            "write",
            self.validate_form
        )

        self.var_email.trace_add(
            "write",
            self.validate_form
        )

        self.var_telepon.trace_add(
            "write",
            self.validate_form
        )

        self.var_tanggal_lahir.trace_add(
            "write",
            self.validate_form
        )

        self.frame_biodata = tk.Frame(
            master=self,
            padx=20,
            pady=20,
            bg="lightblue"
        )

        self.frame_biodata.columnconfigure(
            1,
            weight=1
        )

        self.label_judul = tk.Label(
            master=self.frame_biodata,
            text="FORM BIODATA MAHASISWA",
            font=("Arial", 16, "bold"),
            bg="lightblue",
        )

        self.label_judul.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=20
        )

        self.frame_input = tk.Frame(
            master=self.frame_biodata,
            relief=tk.GROOVE,
            borderwidth=2,
            padx=10,
            pady=10,
        )

        self.label_nama = tk.Label(
            master=self.frame_input,
            text="Nama Lengkap:",
            font=("Arial", 12)
        )

        self.label_nama.grid(
            row=0,
            column=0,
            sticky="W",
            pady=2
        )

        self.entry_nama = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_nama,
        )

        self.entry_nama.grid(
            row=0,
            column=1,
            pady=2
        )

        self.label_nim = tk.Label(
            master=self.frame_input,
            text="NIM:",
            font=("Arial", 12)
        )

        self.label_nim.grid(
            row=1,
            column=0,
            sticky="W",
            pady=2
        )

        self.entry_nim = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_nim,
        )

        self.entry_nim.grid(
            row=1,
            column=1,
            pady=2
        )

        self.label_jurusan = tk.Label(
            master=self.frame_input,
            text="Jurusan:",
            font=("Arial", 12)
        )

        self.label_jurusan.grid(
            row=2,
            column=0,
            sticky="W",
            pady=2
        )

        self.entry_jurusan = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_jurusan,
        )

        self.entry_jurusan.grid(
            row=2,
            column=1,
            pady=2
        )

        self.label_email = tk.Label(
            master=self.frame_input,
            text="Email:",
            font=("Arial", 12)
        )

        self.label_email.grid(
            row=3,
            column=0,
            sticky="W",
            pady=2
        )

        self.entry_email = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_email,
        )

        self.entry_email.grid(
            row=3,
            column=1,
            pady=2
        )

        self.label_telepon = tk.Label(
            master=self.frame_input,
            text="Telepon:",
            font=("Arial", 12)
        )

        self.label_telepon.grid(
            row=4,
            column=0,
            sticky="W",
            pady=2
        )

        self.entry_telepon = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_telepon,
        )

        self.entry_telepon.grid(
            row=4,
            column=1,
            pady=2
        )

        self.label_tanggal_lahir = tk.Label(
            master=self.frame_input,
            text="Tanggal Lahir:",
            font=("Arial", 12)
        )

        self.label_tanggal_lahir.grid(
            row=5,
            column=0,
            sticky="W",
            pady=2
        )

        self.entry_tanggal_lahir = tk.Entry(
            master=self.frame_input,
            width=30,
            font=("Arial", 12),
            textvariable=self.var_tanggal_lahir,
        )

        self.entry_tanggal_lahir.grid(
            row=5,
            column=1,
            pady=2
        )

        tk.Label(
            master=self.frame_input,
            text="(DD-MM-YYYY)",
            font=("Arial", 8),
            fg="gray"
        ).grid(
            row=6,
            column=1,
            sticky="W"
        )

        self.label_alamat = tk.Label(
            master=self.frame_input,
            text="Alamat:",
            font=("Arial", 12)
        )

        self.label_alamat.grid(
            row=7,
            column=0,
            sticky="NW",
            pady=2
        )

        self.frame_alamat = tk.Frame(
            master=self.frame_input,
            relief=tk.SUNKEN,
            borderwidth=1
        )

        self.scrollbar_alamat = tk.Scrollbar(
            master=self.frame_alamat
        )

        self.scrollbar_alamat.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.text_alamat = tk.Text(
            master=self.frame_alamat,
            height=5,
            width=28,
            font=("Arial", 12)
        )

        self.text_alamat.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.scrollbar_alamat.config(
            command=self.text_alamat.yview
        )

        self.text_alamat.config(
            yscrollcommand=self.scrollbar_alamat.set
        )

        self.frame_alamat.grid(
            row=7,
            column=1,
            pady=2
        )

        self.label_jk = tk.Label(
            master=self.frame_input,
            text="Jenis Kelamin:",
            font=("Arial", 12)
        )

        self.label_jk.grid(
            row=8,
            column=0,
            sticky="W",
            pady=2
        )

        self.frame_jk = tk.Frame(
            master=self.frame_input
        )

        self.frame_jk.grid(
            row=8,
            column=1,
            sticky="W"
        )

        self.radio_pria = tk.Radiobutton(
            master=self.frame_jk,
            text="Pria",
            variable=self.var_jk,
            value="Pria"
        )

        self.radio_pria.pack(
            side=tk.LEFT
        )

        self.radio_wanita = tk.Radiobutton(
            master=self.frame_jk,
            text="Wanita",
            variable=self.var_jk,
            value="Wanita"
        )

        self.radio_wanita.pack(
            side=tk.LEFT
        )

        self.check_setuju = tk.Checkbutton(
            master=self.frame_input,
            text="Saya menyetujui pengumpulan data ini.",
            variable=self.var_setuju,
            font=("Arial", 10),
            command=self.validate_form,
        )

        self.check_setuju.grid(
            row=9,
            column=0,
            columnspan=2,
            pady=10,
            sticky="W"
        )

        self.frame_input.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="EW"
        )

        self.frame_tombol_aksi = tk.Frame(
            master=self.frame_biodata,
            bg="lightblue"
        )

        self.frame_tombol_aksi.grid(
            row=6,
            column=0,
            columnspan=2,
            pady=20,
            sticky="EW"
        )

        self.frame_tombol_aksi.columnconfigure(
            0,
            weight=3
        )

        self.frame_tombol_aksi.columnconfigure(
            1,
            weight=1
        )

        self.btn_submit = tk.Button(
            master=self.frame_tombol_aksi,
            text="Submit Biodata",
            font=("Arial", 12, "bold"),
            command=self.submit_data,
            state=tk.DISABLED,
        )

        self.btn_submit.grid(
            row=0,
            column=0,
            sticky="EW",
            padx=(0, 5)
        )

        self.btn_reset = tk.Button(
            master=self.frame_tombol_aksi,
            text="Reset Form",
            font=("Arial", 12),
            command=self._reset_form_biodata,
        )

        self.btn_reset.grid(
            row=0,
            column=1,
            sticky="EW"
        )

        self.btn_submit.bind(
            "<Enter>",
            self.on_enter
        )

        self.btn_submit.bind(
            "<Leave>",
            self.on_leave
        )

        self.tooltip_submit = None
        self.tooltip_hide_id = None

        self.entry_nama.bind(
            "<Return>",
            lambda event: self.entry_nim.focus_set()
        )

        self.entry_nim.bind(
            "<Return>",
            lambda event: self.entry_jurusan.focus_set()
        )

        self.entry_jurusan.bind(
            "<Return>",
            lambda event: self.entry_email.focus_set()
        )

        self.entry_email.bind(
            "<Return>",
            lambda event: self.entry_telepon.focus_set()
        )

        self.entry_telepon.bind(
            "<Return>",
            lambda event: self.entry_tanggal_lahir.focus_set()
        )

        self.entry_tanggal_lahir.bind(
            "<Return>",
            lambda event: self.text_alamat.focus_set()
        )

        for widget in (
            self.entry_nama,
            self.entry_nim,
            self.entry_jurusan,
            self.entry_email,
            self.entry_telepon,
            self.entry_tanggal_lahir,
            self.text_alamat,
        ):
            widget.bind(
                "<Shift-Return>",
                self.submit_shortcut
            )

        for widget in (
            self.entry_nama,
            self.entry_nim,
            self.entry_jurusan,
            self.entry_email,
            self.entry_telepon,
            self.entry_tanggal_lahir,
        ):
            widget.bind(
                "<Key>",
                self._on_typing
            )

        self.label_hasil = tk.Label(
            master=self.frame_biodata,
            text="",
            font=("Arial", 12, "italic"),
            justify=tk.LEFT,
            bg="lightblue",
        )

        self.label_hasil.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="EW",
            padx=10,
            pady=10
        )

    def _validasi_email(self, email):
        pola_email = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.fullmatch(pola_email, email) is not None

    def _validasi_telepon(self, telepon):
        pola_telepon = r"^(?:08[1-9][0-9]{7,11}|\+628[1-9][0-9]{7,11})$"
        return re.fullmatch(pola_telepon, telepon) is not None

    def _validasi_tanggal_lahir(self, tanggal):
        try:
            tanggal_lahir = datetime.datetime.strptime(
                tanggal,
                "%d-%m-%Y"
            ).date()

            tanggal_hari_ini = datetime.date.today()

            if tanggal_lahir > tanggal_hari_ini:
                return False

            return True

        except ValueError:
            return False

    def submit_data(self):
        try:
            if self.var_setuju.get() == 0:
                messagebox.showwarning(
                    "Peringatan",
                    "Anda harus menyetujui pengumpulan data!"
                )
                return

            nama = self.entry_nama.get().strip()
            nim = self.entry_nim.get().strip()
            jurusan = self.entry_jurusan.get().strip()
            email = self.entry_email.get().strip()
            telepon = self.entry_telepon.get().strip()
            tanggal_lahir = self.entry_tanggal_lahir.get().strip()
            alamat = self.text_alamat.get(
                "1.0",
                tk.END
            ).strip()

            jenis_kelamin = self.var_jk.get()

            for entry in (
                self.entry_nama,
                self.entry_nim,
                self.entry_jurusan,
                self.entry_email,
                self.entry_telepon,
                self.entry_tanggal_lahir,
            ):
                entry.configure(bg="white")

            if (
                not nama
                or not nim
                or not jurusan
                or not email
                or not telepon
                or not tanggal_lahir
            ):
                if not nama:
                    self.entry_nama.configure(bg="lightcoral")

                if not nim:
                    self.entry_nim.configure(bg="lightcoral")

                if not jurusan:
                    self.entry_jurusan.configure(bg="lightcoral")

                if not email:
                    self.entry_email.configure(bg="lightcoral")

                if not telepon:
                    self.entry_telepon.configure(bg="lightcoral")

                if not tanggal_lahir:
                    self.entry_tanggal_lahir.configure(
                        bg="lightcoral"
                    )

                messagebox.showwarning(
                    "Input Kosong",
                    "Nama, NIM, Jurusan, Email, Telepon, "
                    "dan Tanggal Lahir harus diisi!"
                )
                return

            if nama.isdigit():
                self.entry_nama.configure(bg="lightcoral")

                messagebox.showwarning(
                    "Format Nama Salah",
                    "Nama tidak boleh hanya berupa angka!"
                )

                self.entry_nama.focus_set()
                return

            if not nim.isdigit() or len(nim) < 8:
                self.entry_nim.configure(bg="lightcoral")

                messagebox.showwarning(
                    "Format NIM Salah",
                    "NIM harus berupa angka minimal 8 digit!"
                )

                self.entry_nim.focus_set()
                return

            if not self._validasi_email(email):
                self.entry_email.configure(bg="lightcoral")

                messagebox.showwarning(
                    "Format Email Salah",
                    "Masukkan email dengan format yang benar.\n"
                    "Contoh: nama@gmail.com"
                )

                self.entry_email.focus_set()
                return

            if not self._validasi_telepon(telepon):
                self.entry_telepon.configure(bg="lightcoral")

                messagebox.showwarning(
                    "Format Telepon Salah",
                    "Nomor telepon harus menggunakan format Indonesia.\n\n"
                    "Contoh:\n"
                    "081234567890\n"
                    "+6281234567890"
                )

                self.entry_telepon.focus_set()
                return

            if not self._validasi_tanggal_lahir(tanggal_lahir):
                self.entry_tanggal_lahir.configure(
                    bg="lightcoral"
                )

                messagebox.showwarning(
                    "Tanggal Lahir Salah",
                    "Tanggal harus menggunakan format DD-MM-YYYY "
                    "dan tidak boleh melebihi tanggal hari ini."
                )

                self.entry_tanggal_lahir.focus_set()
                return

            self.data_biodata = {
                "nama": nama,
                "nim": nim,
                "jurusan": jurusan,
                "email": email,
                "telepon": telepon,
                "tanggal_lahir": tanggal_lahir,
                "alamat": alamat,
                "jenis_kelamin": jenis_kelamin,
            }

            hasil = (
                f"Nama: {nama}\n"
                f"NIM: {nim}\n"
                f"Jurusan: {jurusan}\n"
                f"Email: {email}\n"
                f"Telepon: {telepon}\n"
                f"Tanggal Lahir: {tanggal_lahir}\n"
                f"Alamat: {alamat}\n"
                f"Jenis Kelamin: {jenis_kelamin}"
            )

            messagebox.showinfo(
                "Data Tersimpan",
                hasil
            )

            hasil_lengkap = (
                "BIODATA TERSIMPAN:\n"
                f"Diinput oleh: {self.current_user}\n\n"
                f"{hasil}"
            )

            theme = self.USER_THEMES.get(
                self.current_user,
                self.DEFAULT_THEME
            )

            self.label_hasil.config(
                text=hasil_lengkap,
                bg=theme["primary"],
                fg=theme["text"],
                font=("Arial", 11, "bold"),
                padx=12,
                pady=10,
                relief=tk.RAISED,
                bd=2,
            )

            self.data_sudah_disubmit = True

            logging.info(
                f"Data submitted by user: "
                f"{self.current_user} - NIM: {nim}"
            )

        except Exception as e:
            logging.error(
                f"Error in submit_data by "
                f"{self.current_user}: {str(e)}"
            )

            messagebox.showerror(
                "Error",
                f"Terjadi kesalahan saat memproses data:\n{str(e)}"
            )

    def validate_form(self, *args):
        nama_valid = self.var_nama.get().strip() != ""
        nim_valid = self.var_nim.get().strip() != ""
        jurusan_valid = self.var_jurusan.get().strip() != ""
        email_valid = self.var_email.get().strip() != ""
        telepon_valid = self.var_telepon.get().strip() != ""
        tanggal_valid = self.var_tanggal_lahir.get().strip() != ""
        setuju_valid = self.var_setuju.get() == 1

        if (
            nama_valid
            and nim_valid
            and jurusan_valid
            and email_valid
            and telepon_valid
            and tanggal_valid
            and setuju_valid
        ):
            self.btn_submit.config(
                state=tk.NORMAL
            )
        else:
            self.btn_submit.config(
                state=tk.DISABLED
            )

    def on_enter(self, event):
        if self.btn_submit["state"] == tk.NORMAL:
            self.btn_submit.config(
                bg="lightblue"
            )

        if self.tooltip_hide_id is not None:
            self.after_cancel(
                self.tooltip_hide_id
            )
            self.tooltip_hide_id = None

        if self.tooltip_submit is None:
            self.tooltip_submit = tk.Toplevel(self)

            self.tooltip_submit.wm_overrideredirect(
                True
            )

            tk.Label(
                self.tooltip_submit,
                text="Gunakan Shift+Enter untuk mengirim",
                bg="#fffbe6",
                relief=tk.SOLID,
                borderwidth=1,
                padx=6,
                pady=3,
            ).pack()

            self.tooltip_submit.bind(
                "<Enter>",
                self._tahan_tooltip_submit
            )

            self.tooltip_submit.bind(
                "<Leave>",
                self._jadwalkan_tutup_tooltip
            )

        self.tooltip_submit.update_idletasks()

        x = (
            self.btn_submit.winfo_rootx()
            + (
                self.btn_submit.winfo_width()
                - self.tooltip_submit.winfo_width()
            ) // 2
        )

        y = (
            self.btn_submit.winfo_rooty()
            - self.tooltip_submit.winfo_height()
            - 4
        )

        self.tooltip_submit.geometry(
            f"+{x}+{y}"
        )

    def on_leave(self, event):
        self.btn_submit.config(
            bg="SystemButtonFace"
        )

        self._jadwalkan_tutup_tooltip(event)

    def _tahan_tooltip_submit(self, event):
        if self.tooltip_hide_id is not None:
            self.after_cancel(
                self.tooltip_hide_id
            )
            self.tooltip_hide_id = None

    def _jadwalkan_tutup_tooltip(self, event):
        if self.tooltip_hide_id is None:
            self.tooltip_hide_id = self.after(
                150,
                self._tutup_tooltip_submit
            )

    def _tutup_tooltip_submit(self):
        self.tooltip_hide_id = None

        if self.tooltip_submit is not None:
            self.tooltip_submit.destroy()
            self.tooltip_submit = None

    def submit_shortcut(self, event=None):
        if self.btn_submit["state"] == tk.NORMAL:
            self.submit_data()

        return "break"

    def keluar_aplikasi(self):
        if messagebox.askokcancel(
            "Keluar",
            "Apakah Anda yakin ingin keluar dari aplikasi?"
        ):
            logging.info(
                f"Application closed by user: "
                f"{self.current_user}"
            )

            self.destroy()


if __name__ == "__main__":
    app = AplikasiBiodata()
    app.mainloop()
