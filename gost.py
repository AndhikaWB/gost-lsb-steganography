from biner import Biner

DEBUG = False
def print_debug(*args, **kwargs):
    if DEBUG: print(*args, **kwargs)

# Referensi (dengan penyesuaian)
# DOI: 10.13140/RG.2.2.35980.21125

class GOST:
    @staticmethod
    def _masukan_kunci(kunci:str) -> str:
        """
        ### Deskripsi:
        Fungsi untuk membuat kunci sesuai spesifikasi GOST

        ### Masukan:
        - kunci (str) = kunci dalam bentuk teks biasa

        ### Keluaran:
        - kunci (str) = list kunci dalam 8 bagian
        - kunci_biner (str) = list biner kunci dalam 8 bagian
        """

        if len(kunci) < 32:
            # Gunakan auto-key jika panjang kunci kurang dari 32 byte (256 bit)
            kunci = kunci * (32 // len(kunci) + 1)
        # Jika kunci terlalu panjang, ambil 32 byte pertama
        kunci = kunci[:32]
        print_debug("Kunci (32 byte):", kunci)

        # Bagi kunci menjadi 8 sub-kunci (K0-K7)
        # Panjang tiap kunci 32 byte / 8 = 4 byte
        # Referensi: https://stackoverflow.com/q/13673060

        kunci = [ kunci[i:4+i] for i in range(0, len(kunci), 4) ]
        print_debug("Kunci (8 x 4 byte):", kunci)

        # Ubah kunci ke dalam format biner
        kunci_biner = [ Biner.teks_ke_biner(i) for i in kunci ]
        print_debug("Kunci dalam biner (8 x 4 byte):", kunci_biner)

        # Balik posisi biner kunci
        # Bit paling kanan menjadi paling kiri, dan sebaliknya

        kunci_biner = [ i[::-1] for i in kunci_biner ]
        print_debug("Kunci dalam biner setelah dibalik (8 x 4 byte):", kunci_biner)

        return kunci, kunci_biner

    @staticmethod
    def _masukan_plainteks(plainteks:str) -> str:
        """
        ### Deskripsi:
        Fungsi untuk membuat plainteks sesuai spesifikasi GOST

        ### Masukan:
        - plainteks (str) = plainteks dalam bentuk teks biasa

        ### Keluaran:
        - plainteks (str) = list plainteks untuk tiap-tiap blok
        - plainteks_biner (str) = list biner plainteks untuk tiap-tiap blok
        """

        # Bagi plainteks menjadi beberapa blok dengan panjang 8 byte (64 bit)
        plainteks = [ plainteks[i:8+i] for i in range(0, len(plainteks), 8) ]
        print_debug("Plainteks (8 byte per blok):", plainteks)

        # Tambahkan padding NULL di depan jika panjang teks kurang dari 8 byte
        for i in range(len(plainteks)):
            if len(plainteks[i]) < 8:
                plainteks[i] = ("\0" * (8 - len(plainteks[i]))) + plainteks[i]
        print_debug("Plainteks dengan padding (8 byte per blok):", plainteks)

        # Konversi tiap blok plainteks ke biner
        plainteks_biner = [ Biner.teks_ke_biner(i) for i in plainteks ]

        print_debug("Plainteks dalam biner (8 byte per blok):")
        for i in range(len(plainteks_biner)):
            print_debug(f"Plainteks {i} -", f"['{plainteks_biner[i]}']")

        # Bagi tiap blok plainteks menjadi 2 bagian (yaitu R0 dan L0)
        # Tiap blok berukuran 8 byte, maka R0 = byte 0-3 dan L0 = byte 4-8

        for i in range(len(plainteks_biner)):
            # Pecah biner plainteks ke dalam list setiap 8 bit
            tmp_biner = [ plainteks_biner[i][j:8+j] for j in range(0, len(plainteks_biner[i]), 8) ]
            # Gabung kembali menjadi 2 bagian terpisah (R0 dan L0)
            plainteks_biner[i] = [ "".join(tmp_biner[0:4]),  "".join(tmp_biner[4:8]) ]

        print_debug("Plainteks R0 dan L0 dalam biner (2 x 4 byte per blok):")
        for i in range(len(plainteks_biner)):
            print_debug(f"Plainteks {i} -", plainteks_biner[i])

        return plainteks, plainteks_biner
    
    @staticmethod
    def _masukan_cipherteks(cipherteks_biner:str) -> str:
        """
        ### Deskripsi:
        Fungsi untuk membuat cipherteks sesuai spesifikasi GOST

        ### Masukan:
        - cipherteks_biner (str) = biner cipherteks yang tergabung tanpa spasi

        ### Keluaran:
        - cipherteks (str) = list cipherteks untuk tiap-tiap blok
        - cipherteks_biner (str) = list biner cipherteks untuk tiap-tiap blok
        """

        # Bagi cipherteks menjadi beberapa blok dengan panjang 8 byte (64 bit)
        cipherteks_biner = [ cipherteks_biner[i:64+i] for i in range(0, len(cipherteks_biner), 64) ]
        cipherteks = [ Biner.biner_ke_teks(i) for i in cipherteks_biner ]

        print_debug("Cipherteks dalam biner (8 byte per blok):")
        for i in range(len(cipherteks_biner)):
            print_debug(f"Cipherteks {i} -", f"['{cipherteks_biner[i]}']")

        # Bagi tiap blok cipherteks menjadi 2 bagian (yaitu R0 dan L0)
        # Tiap blok berukuran 8 byte, maka R0 = byte 0-3 dan L0 = byte 4-8

        for i in range(len(cipherteks_biner)):
            # Pecah biner cipherteks ke dalam list setiap 8 bit
            tmp_biner = [ cipherteks_biner[i][j:8+j] for j in range(0, len(cipherteks_biner[i]), 8) ]
            # Gabung kembali menjadi 2 bagian terpisah (R0 dan L0)
            cipherteks_biner[i] = [ "".join(tmp_biner[0:4]),  "".join(tmp_biner[4:8]) ]

        print_debug("Cipherteks R0 dan L0 dalam biner (2 x 4 byte per blok):")
        for i in range(len(cipherteks_biner)):
            print_debug(f"Cipherteks {i} -", cipherteks_biner[i])

        return cipherteks, cipherteks_biner
    
    @staticmethod
    def _substitusi_sbox(biner:str) -> str:
        """
        ### Deskripsi:
        Fungsi untuk mensubstitusi biner ke dalam S-box menjadi biner baru

        ### Masukan:
        - biner (str) = biner yang akan disubstitusi

        ### Keluaran:
        - biner (str) = biner setelah disubstitusi dengan S-box
        """
        
        # Spesifikasi S-box untuk GOST R 34.12-2015
        sbox = [
            # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
            (12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1),
            (6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15),
            (11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0),
            (12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11),
            (7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12),
            (5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0),
            (8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7),
            (1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2)
        ]

        """
        Contoh Masukan:
            Biner: 1111 0000 0001 0011 ...
                   (SBOX0 = 15, SBOX1 = 0, SBOX2 = 1, SBOX3 = 3)
                   (SBOX sebagai baris, nilai sebagai kolom)
        Contoh Keluaran:
            Biner: 0001 0110 0011 0001 ...
                   (SBOX0 = 1, SBOX1 = 6, SBOX2 = 3, SBOX3 = 1)
        """

        # Pecah biner per 4 bit (SBOX0-SBOX15) untuk disubstitusi
        biner = [ biner[i:4+i] for i in range(0, len(biner), 4) ]

        # Substitusi (ubah) nilai biner saat ini menjadi biner baru
        for i in range(len(biner)):
            nilai = Biner.biner_ke_angka(biner[i], 4)
            biner[i] = Biner.angka_ke_biner(sbox[i][nilai], 4)
        
        return "".join(biner)

    @staticmethod
    def enkripsi(plainteks:str, kunci:str) -> str:
        """
        ### Deskripsi:
        Fungsi bantuan untuk mengenkripsi plainteks berkali-kali (per blok)

        ### Masukan:
        - plainteks (str) = plainteks dalam bentuk teks biasa
        - kunci (str) = kunci dalam bentuk teks biasa

        ### Keluaran:
        - cipherteks_biner (str) = biner cipherteks yang tergabung tanpa spasi
        """

        plainteks, plainteks_biner = GOST._masukan_plainteks(plainteks)
        kunci, kunci_biner = GOST._masukan_kunci(kunci)

        # Balik posisi biner plainteks
        # Bit paling kanan menjadi paling kiri, dan sebaliknya

        for i in range(len(plainteks_biner)):
            for j in range(len(plainteks_biner[i])):
                plainteks_biner[i][j] = plainteks_biner[i][j][::-1]

        print_debug("Plainteks R0 dan L0 dalam biner setelah dibalik (2 x 4 byte per blok):")
        for i in range(len(plainteks_biner)):
            print_debug(f"Plainteks {i} -", plainteks_biner[i])

        # Fungsi enkripsi GOST didesain hanya untuk 1 blok plainteks
        # Oleh karena itu, digunakan fungsi bantuan ini untuk menjalankan enkripsi berkali-kali

        cipherteks_biner = []
        for i in plainteks_biner:
            # Bila plainteks lebih dari 1 blok, maka enkripsi berkali-kali sesuai jumlah blok
            cipherteks_biner.append(GOST._enkripsi_blok(i, kunci_biner))
            print_debug(f"Hasil cipherteks (1 blok): {Biner.biner_ke_teks(cipherteks_biner[-1])} ({cipherteks_biner[-1]})\n")

        cipherteks = [ Biner.biner_ke_teks(i) for i in cipherteks_biner ]

        if len(cipherteks_biner) > 1:
            print_debug(f"Hasil akhir cipherteks (semua blok): {cipherteks}")
            print_debug(f"Hasil akhir cipherteks (semua blok, dalam biner): {cipherteks_biner}")
    
        return "".join(cipherteks_biner)

    def _enkripsi_blok(plainteks_biner, kunci_biner):
        """
        ### Deskripsi:
        Fungsi enkripsi GOST yang sebenarnya (hanya untuk 1 blok)

        ### Masukan:
        - plainteks_biner (str) = plainteks dalam bentuk biner
        - kunci_biner (str) = kunci dalam bentuk biner

        ### Keluaran:
        - cipherteks_biner (str) = cipherteks dalam bentuk biner
        """

        # Inisiasi RX dan LX (0-31) untuk tiap round nantinya
        # Ambil R0 dan L0 untuk digunakan pertama kali
        # R1, L1, dan seterusnya baru akan dibentuk setelah R0 dan L0 dipakai
        R = [ plainteks_biner[0] ]
        L = [ plainteks_biner[1] ]

        # Kunci (K0-K7)
        K = kunci_biner

        # j = Indeks kunci yang sedang digunakan (K0-K7)
        # i = Putaran (round) saat ini
        # X = Nilai i/j saat ini (tergantung konteks)

        j = 0
        for i in range(32):
            if i < 24:
                print_debug(f"R{i}: {R[i]}, L{i}: {L[i]}, K{j}: {K[j]}")
                # Tambahkan nilai RX dan KX kemudian modulus dengan 2^32
                hasil = (Biner.biner_ke_angka(R[i], 32) + Biner.biner_ke_angka(K[j], 32)) % (2 ** 32)
                print_debug(f"R{i} + K{j} % 2^32: {Biner.angka_ke_biner(hasil, 32)}")
                # Ulang indeks kunci tiap 7 putaran (K0-K7) selama masih dibawah 24 putaran
                if j == 7: j = 0
                else: j = j + 1
            else:
                # Jika sudah 24 putaran maka indeks kunci dibalik (dari K7-K0)
                if i == 24: j = 7
                print_debug(f"R{i}: {R[i]}, L{i}: {L[i]}, K{j}: {K[j]}")
                # Tambahkan nilai RX dan KX kemudian modulus dengan 2^32
                hasil = (Biner.biner_ke_angka(R[i], 32) + Biner.biner_ke_angka(K[j], 32)) % (2 ** 32)
                print_debug(f"R{i} + K{j} % 2^32: {Biner.angka_ke_biner(hasil, 32)}")
                j = j - 1
            
            # Konversi biner ke angka
            hasil_biner = Biner.angka_ke_biner(hasil, 32)
            # Substitusi (ubah) biner sesuai isi S-box
            hasil_biner = GOST._substitusi_sbox(hasil_biner)
            print_debug(f"Hasil S-box: {hasil_biner}")
            # Geser posisi 11 bit pertama menjadi 11 bit terakhir (rotate left shift)
            hasil_biner = hasil_biner[11:] + hasil_biner[:11]
            print_debug(f"RLS S-box: {hasil_biner}")
            
            if i < 31:
                # Hasilkan RX+1 untuk perulangan selanjutnya
                R.append(
                    # RLS hasil biner kemudian XOR-kan dengan LX
                    Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)
                )
                # Hasilkan LX+1 untuk perulangan selanjutnya
                L.append(R[i])
                
                print_debug(f"RLS S-box XOR L{i}: {Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)}\n")
            else:
                # Hasilkan RX+1 (R32)
                R.append(R[i])
                # Hasilkan LX+1 (L32)
                L.append(
                    # RLS hasil biner kemudian XOR-kan dengan LX
                    Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)
                )

                print_debug(f"RLS S-box XOR L{i}: {Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)}")

                # Balik posisi bit kedua variabel kemudian hasilkan cipherteks
                R[i+1] = R[i+1][::-1]
                L[i+1] = L[i+1][::-1]
                return R[i+1] + L[i+1]

    @staticmethod
    def dekripsi(cipherteks_biner:str, kunci:str) -> str:
        """
        ### Deskripsi:
        Fungsi bantuan untuk mendekripsi teks berkali-kali (per blok)

        ### Masukan:
        - cipherteks_biner (str) = cipherteks dalam bentuk biner
        - kunci (str) = kunci dalam bentuk teks biasa

        ### Keluaran:
        - plainteks (str) = plainteks hasil dekripsi
        """

        cipherteks, cipherteks_biner = GOST._masukan_cipherteks(cipherteks_biner)
        kunci, kunci_biner = GOST._masukan_kunci(kunci)

        # Balik posisi biner cipherteks
        # Bit paling kanan menjadi paling kiri, dan sebaliknya

        for i in range(len(cipherteks_biner)):
            for j in range(len(cipherteks_biner[i])):
                cipherteks_biner[i][j] = cipherteks_biner[i][j][::-1]

        print_debug("Cipherteks R0 dan L0 dalam biner setelah dibalik (2 x 4 byte per blok):")
        for i in range(len(cipherteks_biner)):
            print_debug(f"Cipherteks {i} -", cipherteks_biner[i])

        # Fungsi dekripsi GOST didesain hanya untuk 1 blok cipherteks
        # Oleh karena itu, digunakan fungsi bantuan ini untuk menjalankan dekripsi berkali-kali

        plainteks_biner = []
        for i in cipherteks_biner:
            # Bila cipherteks lebih dari 1 blok, maka dekripsi berkali-kali sesuai jumlah blok
            plainteks_biner.append(GOST._dekripsi_blok(i, kunci_biner))
            print_debug(f"Hasil plainteks (1 blok): {Biner.biner_ke_teks(plainteks_biner[-1])} ({plainteks_biner[-1]})\n")

        # Konversi biner ke plainteks tanpa padding NULL
        plainteks = [ Biner.biner_ke_teks(i, padding = False) for i in plainteks_biner ]

        if len(plainteks_biner) > 1:
            print_debug(f"Hasil akhir plainteks (semua blok): {plainteks}")
            print_debug(f"Hasil akhir plainteks (semua blok, dalam biner): {plainteks_biner}")
    
        return "".join(plainteks)
    
    def _dekripsi_blok(cipherteks_biner, kunci_biner):
        """
        ### Deskripsi:
        Fungsi enkripsi GOST yang sebenarnya (hanya untuk 1 blok)

        ### Masukan:
        - plainteks_biner (str) = plainteks dalam bentuk biner
        - kunci_biner (str) = kunci dalam bentuk biner

        ### Keluaran:
        - cipherteks_biner (str) = cipherteks dalam bentuk biner
        """

        # Inisiasi RX dan LX (0-31) untuk tiap round nantinya
        # Ambil R0 dan L0 untuk digunakan pertama kali
        # R1, L1, dan seterusnya baru akan dibentuk setelah R0 dan L0 dipakai
        R = [ cipherteks_biner[0] ]
        L = [ cipherteks_biner[1] ]

        # Kunci (K0-K7)
        K = kunci_biner

        # j = Indeks kunci yang sedang digunakan (K0-K7)
        # i = Putaran (round) saat ini
        # X = Nilai i/j saat ini (tergantung konteks)

        j = 0
        for i in range(32):
            if i < 8:
                print_debug(f"R{i}: {R[i]}, L{i}: {L[i]}, K{j}: {K[j]}")
                # Tambahkan nilai RX dan KX kemudian modulus dengan 2^32
                hasil = (Biner.biner_ke_angka(R[i], 32) + Biner.biner_ke_angka(K[j], 32)) % (2 ** 32)
                print_debug(f"R{i} + K{j} % 2^32: {Biner.angka_ke_biner(hasil, 32)}")
                # Urutan indeks kunci K0-K7 selama dibawah 8 putaran
                if j < 7: j = j + 1
            else:
                print_debug(f"R{i}: {R[i]}, L{i}: {L[i]}, K{j}: {K[j]}")
                # Tambahkan nilai RX dan KX kemudian modulus dengan 2^32
                hasil = (Biner.biner_ke_angka(R[i], 32) + Biner.biner_ke_angka(K[j], 32)) % (2 ** 32)
                print_debug(f"R{i} + K{j} % 2^32: {Biner.angka_ke_biner(hasil, 32)}")
                # Ulangi indeks kunci dari K7-K0 bila diatas 8 putaran
                if j == 0: j = 7
                else: j = j - 1
            
            # Konversi biner ke angka
            hasil_biner = Biner.angka_ke_biner(hasil, 32)
            # Substitusi (ubah) biner sesuai isi S-box
            hasil_biner = GOST._substitusi_sbox(hasil_biner)
            print_debug(f"Hasil S-box: {hasil_biner}")
            # Geser posisi 11 bit pertama menjadi 11 bit terakhir (rotate left shift)
            hasil_biner = hasil_biner[11:] + hasil_biner[:11]
            print_debug(f"RLS S-box: {hasil_biner}")
            
            if i < 31:
                # Hasilkan RX+1 untuk perulangan selanjutnya
                R.append(
                    # RLS hasil biner kemudian XOR-kan dengan LX
                    Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)
                )
                # Hasilkan LX+1 untuk perulangan selanjutnya
                L.append(R[i])

                print_debug(f"RLS S-box XOR L{i}: {Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)}\n")
            else:
                # Hasilkan RX+1 (R32)
                R.append(R[i])
                # Hasilkan LX+1 (L32)
                L.append(
                    # RLS hasil biner kemudian XOR-kan dengan LX
                    Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)
                )

                print_debug(f"RLS S-box XOR L{i}: {Biner.angka_ke_biner(int(hasil_biner, 2) ^ int(L[i], 2), 32)}")

                # Balik posisi bit kedua variabel kemudian hasilkan plainteks
                R[i+1] = R[i+1][::-1]
                L[i+1] = L[i+1][::-1]
                return R[i+1] + L[i+1]

if __name__ == "__main__":
    # Contoh penggunaan kode GOST
    # Untuk fungsi enkripsi dan dekripsi pesan

    cipherteks_biner = GOST.enkripsi("HelloWorld", "kriptografi2022")
    plainteks = GOST.dekripsi(cipherteks_biner, "kriptografi2022")

    if not DEBUG:
        print("Cipherteks:", Biner.biner_ke_teks(cipherteks_biner))
        print(cipherteks_biner + "\n")

        print("Plainteks:", plainteks)
        print(Biner.teks_ke_biner(plainteks))