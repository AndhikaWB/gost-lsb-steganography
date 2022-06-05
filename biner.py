class Biner:
    @staticmethod
    def teks_ke_biner(teks:str, bit:int = 8) -> str:
        """
        ### Deskripsi:
        Fungsi untuk mengubah teks menjadi biner

        ### Masukan:
        - teks (str) = teks untuk diubah ke biner
        - bit (int) = panjang bit biner untuk tiap karakter teks

        ### Keluaran:
        - biner (str) = teks yang sudah diubah ke biner
        """

        # Referensi 1: https://stackoverflow.com/q/18815820
        # Referensi 2: https://stackoverflow.com/a/47664902
        return "".join(f"{ord(i):0{bit}b}" for i in teks)
    
    @staticmethod
    def tkb(*args, **kwargs):
        """Alias untuk fungsi teks ke biner"""
        return Biner.teks_ke_biner(*args, **kwargs)

    @staticmethod
    def biner_ke_teks(biner:str, padding:bool = True, bit:int = 8) -> str:
        """
        ### Deskripsi:
        Fungsi untuk mengubah biner menjadi teks

        ### Masukan:
        - biner (str) = biner untuk diubah ke teks
        - bit (int) = panjang bit biner untuk dianggap sebagai suatu karakter

        ### Keluaran:
        - teks (str) = biner yang sudah diubah ke teks
        """

        # Konversi biner ke teks berdasarkan jumlah bit
        # Referensi: https://stackoverflow.com/a/40559005
        teks = "".join(chr(int(biner[i*bit:i*bit+bit], 2)) for i in range(len(biner) // bit))
        
        # Jika tanpa padding, maka hapus kode ASCII 0 (null) di depan teks
        if not padding: teks = teks.replace("\0", "")

        return teks
    
    @staticmethod
    def bkt(*args, **kwargs):
        """Alias untuk fungsi biner ke teks"""
        return Biner.biner_ke_teks(*args, **kwargs)

    @staticmethod
    def angka_ke_biner(angka:int, bit:int = 8) -> str:
        """
        ### Deskripsi:
        Fungsi untuk mengubah angka menjadi biner

        ### Masukan:
        - angka (int) = angka untuk diubah ke biner
        - bit (int) = panjang bit biner dari angka

        ### Keluaran:
        - biner (str) = angka yang sudah diubah ke biner
        """

        # Konversi angka ke biner berdasarkan jumlah bit
        # Referensi: https://stackoverflow.com/q/699866
        return format(angka, f"0{bit}b")
    
    @staticmethod
    def akb(*args, **kwargs):
        """Alias untuk fungsi angka ke biner"""
        return Biner.angka_ke_biner(*args, **kwargs)

    @staticmethod
    def biner_ke_angka(biner:str, bit:int = 8) -> int:
        """
        ### Deskripsi:
        Fungsi untuk mengubah biner menjadi angka

        ### Masukan:
        - biner (int) = biner untuk diubah ke angka
        - bit (int) = panjang bit biner untuk dianggap sebagai suatu nilai

        ### Keluaran:
        - angka (int) = biner yang sudah diubah ke angka
        """

        # Konversi biner ke angka berdasarkan jumlah bit
        if len(biner) // bit > 1:
            return [ int(biner[i*bit:i*bit+bit], 2) for i in range(len(biner) // bit) ]
        else:
            return int(biner[:bit], 2)
    
    @staticmethod
    def bka(*args, **kwargs):
        """Alias untuk fungsi biner ke angka"""
        return Biner.biner_ke_angka(*args, **kwargs)