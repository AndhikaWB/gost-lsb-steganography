from biner import Biner
from PIL import Image

import numpy as np
import random
import math
import hashlib

# Selalu simpan gambar stego ke dalam format tertentu
# Tuliskan nama ekstensi tanpa tanda titik
FORMAT_STEGO = ""

DEBUG = False
def print_debug(*args, **kwargs):
    if DEBUG: print(*args, **kwargs)

# Referensi (dengan penyesuaian)
# DOI: 10.1109/ComPE49325.2020.9200077

class LSB:
    @staticmethod
    def encode(pesan_biner:str, kunci:str, gambar_cover:str, pesan:str = None) -> str:
        """
        ### Deskripsi:
        Fungsi untuk menyisipkan pesan tersembunyi ke suatu gambar

        ### Masukan:
        - pesan_biner (str) = biner pesan tanpa spasi yang ingin disisipkan
        - kunci (str) = kunci untuk penentuan seed (samakan saja dengan kunci enkripsi)
        - gambar_cover (str) = path menuju gambar cover yang ingin disisipkan pesan
        - pesan (str) = pesan yang ingin disisipkan (alternatif dari biner pesan)

        ### Keluaran:
        - gambar_stego (str) = path menuju gambar stego yang telah disisipkan pesan
        """

        # Bila pesan dalam bentuk teks biasa maka konversi dulu ke biner
        if pesan: pesan_biner = Biner.teks_ke_biner(pesan)

        # Tambahkan penanda awal dan akhir biner pesan (untuk proses pengeluaran pesan nantinya)
        # Penanda awal dan akhir tidak boleh sama karena tidak ada pengecekan tertentu

        penanda = [ "$T3", "G0$" ]
        pesan_biner = Biner.tkb(penanda[0]) + pesan_biner + Biner.tkb(penanda[1])
        print_debug("Biner pesan plus penanda:", pesan_biner)

        # Buka gambar sebagai array
        cover = Image.open(gambar_cover).convert(colors = 256)
        cover_array = np.asarray(cover)

        # Inisiasi seed agar hasil tidak acak sepenuhnya
        random.seed(kunci)

        # Iterasi piksel berdasarkan ukuran gambar
        # Selama biner pesan masih tersisa untuk disisipkan

        for i in range(cover.height):
            if len(pesan_biner) == 0: break
            for j in range(cover.width):
                if len(pesan_biner) == 0: break

                def xor_msb_pesan():
                    nonlocal pesan_biner
                    nonlocal bit_idk

                    if len(pesan_biner) >= 1:
                        # Akses dan keluarkan MSB dari biner pesan (sampai habis)
                        # Panjang biner pesan akan berkurang satu tiap kali diakses
                        bit_msb = pesan_biner[0]
                        pesan_biner = pesan_biner[1:]
                        # Lakukan XOR bit indikator dengan MSB pesan saat ini
                        # Hasil XOR kemudian akan diletakkan pada LSB piksel gambar
                        return Biner.angka_ke_biner(int(bit_idk) ^ int(bit_msb), 1)
                    else:
                        # Jika biner pesan sudah kosong maka XOR-kan bit indikator dengan nol
                        # Untuk menjaga agar bit piksel gambar tidak berubah nantinya
                        return Biner.angka_ke_biner(int(bit_idk) ^ 0, 1)

                def sisipkan_pesan():
                    nonlocal indikator
                    nonlocal cover_array

                    # Cek 3 digit MSB suatu channel warna untuk penentuan penyisipan bit pesan
                    # Bila 0 berarti sisipkan 1 bit pesan, bila 1 maka sisipkan 2 bit pesan

                    for idk in range(len(indikator[:3])):
                        # Nilai biner salah satu channel warna (bukan ketiganya sekaligus)
                        rgb = Biner.angka_ke_biner(cover_array[i][j][idk])
                        print_debug(f"Nilai [{i}][{j}][{idk}] sebelum diubah:", rgb)

                        if indikator[idk] == "0":
                            # Sisipkan 1 MSB pesan di akhir bit warna
                            cover_array[i][j][idk] = Biner.biner_ke_angka(
                                rgb[:-1] + xor_msb_pesan()
                            )
                        elif indikator[idk] == "1":
                            # Sisipkan 2 MSB pesan di akhir bit warna
                            cover_array[i][j][idk] = Biner.biner_ke_angka(
                                rgb[:-2] + xor_msb_pesan() + xor_msb_pesan()
                            )
                        
                        print_debug(f"Nilai [{i}][{j}][{idk}] sesudah diubah:",
                            Biner.angka_ke_biner(cover_array[i][j][idk]) + "\n"
                        )
                
                # PRNG untuk penentuan channel dan XOR pesan
                bit_idk = random.randint(1, 6)

                if bit_idk == 1 or bit_idk == 4:
                    # Channel merah (red) maka indeksnya 0
                    indikator = Biner.angka_ke_biner(cover_array[i][j][0])
                    # Simpan nilai biner bit indikator untuk di-XOR dengan MSB pesan
                    bit_idk = indikator[bit_idk-1]
                    # XOR bit indikator dengan MSB pesan lalu sisipkan
                    sisipkan_pesan()

                elif bit_idk == 2 or bit_idk == 5:
                    # Channel hijau (green) maka indeksnya 1
                    indikator = Biner.angka_ke_biner(cover_array[i][j][1])
                    # Simpan nilai biner bit indikator untuk di-XOR dengan MSB pesan
                    bit_idk = indikator[bit_idk-1]
                    # XOR bit indikator dengan MSB pesan lalu sisipkan
                    sisipkan_pesan()
                
                elif bit_idk == 3 or bit_idk == 6:
                    # Channel biru (blue) maka indeksnya 2
                    indikator = Biner.angka_ke_biner(cover_array[i][j][2])
                    # Simpan nilai biner bit indikator untuk di-XOR dengan MSB pesan
                    bit_idk = indikator[bit_idk-1]
                    # XOR bit indikator dengan MSB pesan lalu sisipkan
                    sisipkan_pesan()

        # Tambahkan kata "_stego" setelah nama gambar cover (tanpa ekstensi)
        gambar_stego = gambar_cover.rsplit(".", 1)[0] + "_stego"

        try:
            # Simpan gambar stego ke format tertentu bila dispesifikasikan
            if FORMAT_STEGO: gambar_stego += f".{FORMAT_STEGO}"
            # Coba simpan gambar stego sesuai ekstensi gambar cover (bila didukung)
            else:
                ekstensi = "." + gambar_cover.rsplit(".", 1)[1]
                gambar_stego += ekstensi
        except (IndexError, ValueError):
            # Simpan gambar stego sebagai PNG bila terjadi masalah
            gambar_stego = gambar_cover.rsplit(".", 1)[0] + "_stego"
            gambar_stego += ".png"
        
        kwargs = {}
        if "ekstensi" in locals():
            # Simpan WEBP sebagai lossless agar bisa diekstraksi pesan
            if ekstensi == ".webp": kwargs = { "lossless": True }
            # TODO: Cari cara agar GIF dapat diekstraksi pesan
            elif ekstensi == ".gif": kwargs = { "save_all": True }
            # Optimisasi JPEG meskipun hasilnya tetap buruk
            elif ekstensi in (".jpg", ".jpeg"): kwargs = {
                "quality": 100, "subsampling": 0, "qtables": "maximum"
            }
        
        Image.fromarray(cover_array).save(gambar_stego, **kwargs)
        print_debug("Gambar stego disimpan ke:", gambar_stego)
        
        # Tutup gambar cover setelah tidak dibutuhkan
        cover.close()

        return gambar_stego
    
    @staticmethod
    def decode(kunci:str, gambar_stego:str) -> str:
        """
        ### Deskripsi:
        Fungsi untuk mengeluarkan pesan tersembunyi dari suatu gambar

        ### Masukan:
        - kunci (str) = kunci untuk penentuan seed (samakan saja dengan kunci enkripsi)
        - gambar_stego (str) = path menuju gambar stego yang telah disisipkan pesan

        ### Keluaran:
        - pesan (str) = keluaran pesan yang disisipkan ke gambar
        - pesan_biner (str) = keluaran biner pesan yang disisipkan ke gambar
        """

        # Buka gambar sebagai array
        stego = Image.open(gambar_stego).convert(colors = 256)
        stego_array = np.asarray(stego)

        # Inisiasi seed agar hasil tidak acak sepenuhnya
        random.seed(kunci)

        # Isi biner pesan yang disisipkan (mula-mula)
        pesan_biner = ""
        # Penanda awal dan akhir pesan (samakan dengan fungsi encode)
        penanda = [ "$T3", "G0$" ]

        # Iterasi piksel berdasarkan ukuran gambar
        for i in range(stego.height):
            # Jika semua penanda telah ditemukan pada pesan, maka hentikan pencarian
            if all(i in Biner.biner_ke_teks(pesan_biner) for i in penanda): break

            # Penanda akan selalu disimpan dan dicek di bagian awal gambar stego
            # Jika tidak ada penanda awal yang ditemukan, maka pesan dianggap tidak ada
            # Panjang ditambah 8 untuk antisipasi karakter pesan yang belum berjumlah 8 bit

            if len(Biner.biner_ke_teks(pesan_biner)) <= 8 + len(penanda[0]):
                if penanda[0] in Biner.biner_ke_teks(pesan_biner): komplet = True
            elif "komplet" not in locals(): break

            for j in range(stego.width):
                # Jika semua penanda telah ditemukan pada pesan, maka hentikan pencarian
                if all(i in Biner.biner_ke_teks(pesan_biner) for i in penanda): break

                def xor_lsb_piksel(bit_lsb):
                    nonlocal bit_idk
                    # Lakukan XOR bit indikator dengan LSB warna saat ini
                    return Biner.angka_ke_biner(int(bit_idk) ^ int(bit_lsb), 1)

                def keluarkan_pesan():
                    nonlocal indikator
                    nonlocal stego_array
                    nonlocal pesan_biner

                    # Cek 3 digit MSB suatu channel warna untuk penentuan pengeluaran bit pesan
                    # Bila 0 berarti keluarkan 1 bit pesan, bila 1 maka keluarkan 2 bit pesan

                    for idk in range(len(indikator[:3])):
                        # Nilai biner salah satu channel warna (bukan ketiganya sekaligus)
                        rgb = Biner.angka_ke_biner(stego_array[i][j][idk])

                        if indikator[idk] == "0":
                            # Keluarkan 1 bit pesan di akhir bit warna
                            pesan_biner += xor_lsb_piksel(rgb[-1])
                            print_debug("Menyisipkan 1 bit pesan")
                        elif indikator[idk] == "1":
                            # Keluarkan 2 bit pesan di akhir bit warna
                            pesan_biner += xor_lsb_piksel(rgb[-2]) + xor_lsb_piksel(rgb[-1])
                            print_debug("Menyisipkan 2 bit pesan")

                # Bit untuk penentuan channel dan XOR piksel
                bit_idk = random.randint(1, 6)

                if bit_idk == 1 or bit_idk == 4:
                    # Channel merah (red) maka indeksnya 0
                    indikator = Biner.angka_ke_biner(stego_array[i][j][0])
                    # Simpan nilai biner bit indikator untuk di-XOR dengan LSB warna
                    bit_idk = indikator[bit_idk-1]
                    # XOR bit indikator dengan LSB warna lalu sisipkan
                    keluarkan_pesan()

                elif bit_idk == 2 or bit_idk == 5:
                    # Channel hijau (green) maka indeksnya 1
                    indikator = Biner.angka_ke_biner(stego_array[i][j][1])
                    # Simpan nilai biner bit indikator untuk di-XOR dengan LSB warna
                    bit_idk = indikator[bit_idk-1]
                    # XOR bit indikator dengan LSB warna lalu sisipkan
                    keluarkan_pesan()
                
                elif bit_idk == 3 or bit_idk == 6:
                    # Channel biru (blue) maka indeksnya 2
                    indikator = Biner.angka_ke_biner(stego_array[i][j][2])
                    # Simpan nilai biner bit indikator untuk di-XOR dengan LSB warna
                    bit_idk = indikator[bit_idk-1]
                    # XOR bit indikator dengan LSB warna lalu sisipkan
                    keluarkan_pesan()
        
        # Cek apakah semua penanda pesan ditemukan (secara terurut)
        pesan = Biner.biner_ke_teks(pesan_biner)
        komplet = False if pesan.find(penanda[0]) >= pesan.find(penanda[1]) else True
        
        # Tutup gambar stego setelah tidak dibutuhkan
        stego.close()

        if pesan_biner and komplet:
            # Ambil pesan asli di antara kedua penanda pesan
            pesan_biner = pesan_biner.split(Biner.tkb(penanda[0]))[1].split(Biner.tkb(penanda[1]))[0]
            # Kembalikan pesan asli
            return Biner.biner_ke_teks(pesan_biner), pesan_biner
        else: return "Pesan tidak terbaca dan/atau format gambar lossy!", None
    
    @staticmethod
    def kalkulasi_kualitas(gambar_cover:str, gambar_stego:str) -> str:
        """
        ### Deskripsi:
        Fungsi untuk membandingkan kualitas antara gambar cover dan gambar stego

        ### Masukan:
        - gambar_cover (str) = path menuju gambar cover yang belum disisipkan pesan
        - gambar_stego (str) = path menuju gambar stego yang telah disisipkan pesan

        ### Keluaran:
        - mse (float) = mean squared error, untuk perhitungan PSNR
        - psnr (float) = peak signal-to-noise ratio, lebih dari 50 dB sudah baik
        """

        # Buka masing-masing gambar dahulu
        cover = Image.open(gambar_cover).convert(colors = 256)
        stego = Image.open(gambar_stego).convert(colors = 256)

        # Kalkulasi MSE
        mse = np.mean((np.asarray(cover) - np.asarray(stego)) ** 2)
        print_debug("Nilai MSE:", mse)

        # Kalkulasi PSNR
        if (mse == 0): psnr = 100
        else: psnr = 20 * math.log10(255 / math.sqrt(mse))
        print_debug("Nilai PSNR:", psnr, "dB")

        # Tutup gambar cover dan stego setelah tidak dibutuhkan
        cover.close()
        stego.close()

        return mse, psnr
    
    # Kalkulasi hash
    # Dapat memakan memori cukup besar tergantung buffer dan ukuran file

    @staticmethod
    def kalkulasi_hash(gambar:str, teks:str = None) -> str:
        """
        ### Deskripsi:
        Fungsi untuk menghasilkan checksum (SHA256) dari teks atau file

        ### Masukan:
        - gambar (str) = path menuju gambar yang ingin dicek checksum-nya
        - teks (str) = teks yang ingin dicek checksum-nya (alternatif dari gambar)

        ### Keluaran:
        - checksum (str) = checksum dari teks atau file masukan
        """

        if not teks:
            # Baca isi file per 65536 Byte (64 kB)
            # Dapat ditambah/kurangi sesuai jumlah memori
            buffer = 65536
            # Jenis fungsi hash yang digunakan
            hash = hashlib.sha256()

            # Buka file dan kalkulasi hash
            with open(gambar, "rb") as f:
                while True:
                    data = f.read(buffer)
                    if not data: break
                    hash.update(data)
        
            print_debug("SHA256 gambar:", hash.hexdigest())
            return hash.hexdigest()
        else: return hashlib.md5(teks.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    # Contoh penggunaan kode LSB
    # Untuk fungsi encode dan decode pesan serta pengecekan kualitas gambar

    gambar_stego = LSB.encode(
        # Biner hasil enkripsi GOST, disimpan dalam biner agar terjaga nilainya
        "00011100010010111111111110110001100101101110001101011111111011011010010011011110000110111101101100000011011100011110101010100011",
        "kriptografi2022",
        "gambar.png"
    )

    pesan, pesan_biner = LSB.decode(
        "kriptografi2022",
        gambar_stego
    )

    mse, psnr = LSB.kalkulasi_kualitas(
        "gambar.png", gambar_stego
    )

    checksum_cover = LSB.kalkulasi_hash("gambar.png")
    checksum_stego = LSB.kalkulasi_hash(gambar_stego)

    if not DEBUG:
        print("Nilai MSE:", mse)
        print("Nilai PSNR:", psnr)
        print("SHA256 gambar cover:", checksum_cover)
        print("SHA256 gambar stego:", checksum_stego)
        print("Pesan yang disisipkan:", pesan)