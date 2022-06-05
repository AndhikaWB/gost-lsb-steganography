from gost import GOST
from lsb import LSB
from biner import Biner

# Bila teks terlihat aneh, silahkan pasang font Rubik
# https://fonts.google.com/specimen/Rubik

from PIL import Image
from idlelib.tooltip import Hovertip
from pathlib import Path
from tkinter import (
    Tk,
    Canvas,
    Entry,
    Text,
    Button,
    PhotoImage,
    filedialog
)

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.geometry("800x530")
window.configure(bg = "#FFFFFF")

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 530,
    width = 800,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)
canvas.place(x = 0, y = 0)

canvas.create_text(
    437.0,
    36.0,
    anchor="nw",
    text="Pesan Rahasia",
    fill="#212121",
    font=("Rubik SemiBold", 16 * -1)
)

def sisipkan_pesan():
    # Ambil data dari form
    kunci = entry_1.get()
    gambar_cover = entry_2.get()
    plainteks = entry_4.get(1.0, "end-1c")

    if kunci and gambar_cover and plainteks:
        # Enkripsi dan sisipkan pesan ke gambar
        cipherteks_biner = GOST.enkripsi(plainteks, kunci)
        cipherteks = Biner.biner_ke_teks(cipherteks_biner)
        gambar_stego = LSB.encode(cipherteks_biner, kunci, gambar_cover)

        # Dapatkan checksum dari gambar
        checksum_stego = LSB.kalkulasi_hash(gambar_stego)

        # Kalkulasi MSE dan PSNR
        mse, psnr = LSB.kalkulasi_kualitas(gambar_cover, gambar_stego)

        # Tampilkan informasi debug
        entry_3.config(state="normal")
        entry_3.delete(1.0, "end")
        entry_3.insert("end", f"Pesan terenkripsi: {cipherteks}\n\n")
        entry_3.insert("end", f"SHA256 pesan terenkripsi: {LSB.kalkulasi_hash(None, cipherteks)}\n\n")
        entry_3.insert("end", f"Gambar stego disimpan ke: {gambar_stego}\n\n")
        entry_3.insert("end", f"Mean squared error: {mse}\n\n")
        entry_3.insert("end", f"Peak signal-to-noise ratio: {psnr}\n\n")
        if psnr <= 60:
            entry_3.insert("end", "Kualitas dibawah rata-rata! Harap tes pengambilan pesan untuk memastikan.\n\n")
        entry_3.insert("end", f"SHA256 gambar stego: {checksum_stego}")
        entry_3.config(state="disabled")

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=sisipkan_pesan,
    relief="flat"
)
button_1.place(
    x=436.0,
    y=457.0,
    width=160.0,
    height=37.0
)

def ambil_pesan():
    # Ambil data dari form
    kunci = entry_1.get()
    gambar_stego = entry_2.get()

    if kunci and gambar_stego:
        # Ambil pesan dan dapatkan checksum dari gambar
        cipherteks, cipherteks_biner = LSB.decode(kunci, gambar_stego)
        checksum_stego = LSB.kalkulasi_hash(gambar_stego)

        # Tampilkan informasi debug
        entry_3.config(state="normal")
        entry_3.delete(1.0, "end")
        if cipherteks_biner:
            entry_3.insert("end", f"Pesan asli: {cipherteks}\n\n")
            entry_3.insert("end", f"SHA256 pesan asli: {LSB.kalkulasi_hash(None, cipherteks)}\n\n")
        else: entry_3.insert("end", f"Terjadi kesalahan! Cek detail pada bagian pesan.\n\n")
        entry_3.insert("end", f"SHA256 gambar stego: {checksum_stego}")
        entry_3.config(state="disabled")

        # Dekripsi dan tampilkan pesan pada form
        if cipherteks_biner:
            plainteks = GOST.dekripsi(cipherteks_biner, kunci)
            entry_4.delete(1.0, "end")
            entry_4.insert("end", plainteks)
        else:
            entry_4.delete(1.0, "end")
            entry_4.insert("end", cipherteks)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=ambil_pesan,
    relief="flat"
)
button_2.place(
    x=604.0,
    y=457.0,
    width=160.0,
    height=37.0
)

canvas.create_rectangle(
    0.0,
    0.0,
    400.0,
    530.0,
    fill="#009688",
    outline="")

canvas.create_text(
    122.0,
    112.0,
    anchor="nw",
    text="GOST + LSB",
    fill="#FFFFFF",
    font=("Rubik Medium", 28 * -1)
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    200.0,
    224.0,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#F4F6F8",
    highlightthickness=0,
    font=("Rubik Regular", 12 * -1)
)
entry_1.place(
    x=44.0,
    y=208.0 + 4,
    width=312.0,
    height=30.0 - 4
)
entry_1_tooltip = Hovertip(
    anchor_widget=entry_1,
    text="Digunakan sebagai kunci GOST dan seed PRNG.\nBerikan bersama gambar ke penerima pesan.",
    hover_delay=500
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    180.0,
    303.0,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#F4F6F8",
    highlightthickness=0,
    font=("Rubik Regular", 12 * -1),
    disabledforeground="#000000",
    disabledbackground="#F4F6F8",
    state="disabled"
)
entry_2.place(
    x=44.0,
    y=287.0 + 4,
    width=272.0,
    height=30.0 - 4
)
entry_2_tooltip = Hovertip(
    anchor_widget=entry_2,
    text="Gambar untuk penyisipan atau pengambilan pesan.\nTidak semua format cocok untuk disisipkan pesan!",
    hover_delay=500
)

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    200.0,
    430.0,
    image=entry_image_3
)
entry_3 = Text(
    bd=0,
    bg="#F4F6F8",
    highlightthickness=0,
    font=("Rubik Regular", 12 * -1),
    state="disabled"
)
entry_3.place(
    x=44.0,
    y=366.0 + 4,
    width=312.0,
    height=126.0 - 4
)
entry_3_tooltip = Hovertip(
    anchor_widget=entry_3,
    text="Informasi lanjutan mengenai proses pada gambar.\nDapat berisi MSE, PSNR, dan checksum (SHA256).",
    hover_delay=500
)

canvas.create_text(
    36.0,
    177.0,
    anchor="nw",
    text="Kunci Rahasia",
    fill="#FFFFFF",
    font=("Rubik SemiBold", 16 * -1)
)

def pilih_gambar():
    # Tampilkan dialog untuk memilih gambar
    gambar = filedialog.askopenfilename(
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.gif *.webp *.tga"),
            ("PNG image", "*.png"),
            ("JPEG image", "*.jpg *.jpeg"),
            ("TIFF image", "*.tif *.tiff"),
            ("BMP image", "*.bmp"),
            ("GIF image", "*.gif"),
            ("WEBP image", "*.webp"),
            ("TGA image", "*.tga"),
            ("All files", "*.*")
        ]
    )

    if gambar:
        # Perbarui isi form dengan path ke gambar
        entry_2.config(state="normal")
        entry_2.delete(0, "end")
        entry_2.insert("end", gambar)
        entry_2.config(state="disabled")

        # Dapatkan resolusi gambar (lebar x tinggi)
        with Image.open(gambar) as gbr: lebar, tinggi = gbr.size

        # Tampilkan informasi debug
        entry_3.config(state="normal")
        entry_3.delete(1.0, "end")
        entry_3.insert("end", f"Lebar dan tinggi gambar: {lebar} x {tinggi}\n\n")
        entry_3.insert("end", f"SHA256 gambar: {LSB.kalkulasi_hash(gambar)}")
        entry_3.config(state="disabled")

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=pilih_gambar,
    relief="flat"
)
button_3.place(
    x=332.0,
    y=287.0,
    width=32.0,
    height=32.0
)

canvas.create_text(
    36.0,
    256.0,
    anchor="nw",
    text="Pilih Gambar",
    fill="#FFFFFF",
    font=("Rubik SemiBold", 16 * -1)
)

canvas.create_text(
    36.0,
    335.0,
    anchor="nw",
    text="Informasi Debug",
    fill="#FFFFFF",
    font=("Rubik SemiBold", 16 * -1)
)

entry_image_4 = PhotoImage(
    file=relative_to_assets("entry_4.png"))
entry_bg_4 = canvas.create_image(
    600.0,
    254.0,
    image=entry_image_4
)
entry_4 = Text(
    bd=0,
    bg="#F4F6F8",
    highlightthickness=0,
    font=("Rubik Regular", 12 * -1)
)
entry_4.place(
    x=444.0,
    y=67.0 + 8,
    width=312.0,
    height=372.0 - 14
)
entry_4_tooltip = Hovertip(
    anchor_widget=entry_4,
    text="Wajib diisi bila ingin menyisipkan pesan.\nKapasitas pesan adalah 3-6 bit per piksel.",
    hover_delay=500
)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    200.0,
    68.0,
    image=image_image_1
)

window.title("GOST (Kriptografi) + LSB (Steganografi)")
window.resizable(False, False)
window.mainloop()