import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from platypus import NSGAIII, Problem, Real
import threading
import hashlib
import json
import time
import datetime

# -----------------------------------------------------------------------------------
# Bagian 1: Logika Inti (Simulasi, LSTM, NSGA-III)
# -----------------------------------------------------------------------------------

def generate_synthetic_data(num_wpps=10, num_ships_per_wpp=10, start_date='2023-01-01', end_date='2025-01-01'):
    """
    Membuat data tangkapan ikan sintetis.
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    num_days = len(dates)
    
    data = []
    wpp_ids = [f'WPP {711 + i}' for i in range(num_wpps)]
    
    for wpp_id in wpp_ids:
        for ship_id in range(1, num_ships_per_wpp + 1):
            ship_id_str = f'Kapal {ship_id}'
            
            trend = np.linspace(50, 150, num_days)
            seasonal = 30 * np.sin(2 * np.pi * dates.dayofyear / 365)
            noise = np.random.normal(0, 10, num_days)
            
            catches = np.maximum(0, trend + seasonal + noise).astype(int)
            
            for date, catch in zip(dates, catches):
                data.append({
                    'Tanggal': date,
                    'WPP': wpp_id,
                    'Kapal': ship_id_str,
                    'Hasil_Tangkapan_Kg': catch
                })
                
    return pd.DataFrame(data)

class LSTM(nn.Module):
    """
    Model Jaringan Saraf Tiruan LSTM untuk prediksi time series.
    """
    def __init__(self, input_size=1, hidden_layer_size=50, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size)
        self.linear = nn.Linear(hidden_layer_size, output_size)
        self.hidden_cell = (torch.zeros(1,1,self.hidden_layer_size),
                            torch.zeros(1,1,self.hidden_layer_size))

    def forward(self, input_seq):
        lstm_out, self.hidden_cell = self.lstm(input_seq.view(len(input_seq), 1, -1), self.hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]

def create_inout_sequences(input_data, tw):
    """
    Membuat sequence input dan output untuk model LSTM.
    """
    inout_seq = []
    L = len(input_data)
    for i in range(L-tw):
        train_seq = input_data[i:i+tw]
        train_label = input_data[i+tw:i+tw+1]
        inout_seq.append((train_seq, train_label))
    return inout_seq

def predict_lstm(data_frame, wpp_id, ship_id, forecast_days=30, epochs=150):
    """
    Melatih model LSTM dan memprediksi hasil tangkapan di masa depan.
    """
    device = torch.device('cpu')
    ship_data = data_frame[(data_frame['WPP'] == wpp_id) & (data_frame['Kapal'] == ship_id)]
    
    if ship_data.empty or len(ship_data) < 20:
        return np.zeros(forecast_days)
        
    ship_data = ship_data.sort_values(by='Tanggal')
    
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_data = scaler.fit_transform(ship_data['Hasil_Tangkapan_Kg'].values.reshape(-1, 1))
    
    train_window = 12
    train_sequences = create_inout_sequences(torch.FloatTensor(scaled_data).to(device).squeeze(), train_window)

    model = LSTM().to(device)
    loss_function = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for i in range(epochs):
        for seq, labels in train_sequences:
            optimizer.zero_grad()
            model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size).to(device),
                                 torch.zeros(1, 1, model.hidden_layer_size).to(device))
            y_pred = model(seq)
            single_loss = loss_function(y_pred, labels)
            single_loss.backward()
            optimizer.step()

    future_predicts = []
    last_seq = train_sequences[-1][0] if train_sequences else torch.zeros(train_window)  ### PERBAIKAN: Handle jika sequences kosong

    with torch.no_grad():
        for i in range(forecast_days):
            model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size).to(device),
                                 torch.zeros(1, 1, model.hidden_layer_size).to(device))
            future_pred = model(last_seq)
            future_predicts.append(future_pred.item())
            last_seq = torch.cat((last_seq[1:], future_pred), dim=0)

    predicts_unscaled = scaler.inverse_transform(np.array(future_predicts).reshape(-1, 1)).flatten()
    return predicts_unscaled

def optimize_nsga3(ships_data):
    """
    Fungsi optimasi NSGA-III untuk mengalokasikan kuota.
    """
    num_ships = len(ships_data)
    
    if num_ships == 0:
        return np.zeros(0)
    
    def objective_function(vars):
        ### PERBAIKAN: Skala quotas berdasarkan prediksi LSTM per kapal, bukan fixed 10000
        quotas = np.array(vars) * ships_data['Prediksi'].values
        total_catch = sum(quotas)
        fairness = np.std(quotas)
        costs = sum(quotas * 0.5)
        
        penalty = 0
        for i, quota in enumerate(quotas):
            predicted = ships_data['Prediksi'].iloc[i]
            ### PERBAIKAN: Ubah threshold penalty menjadi > predicted (lebih ketat, agar tidak over-allocate terlalu jauh)
            if quota > predicted:
                penalty += (quota - predicted) * 100
        
        return [-total_catch, fairness, costs + penalty]
    
    problem = Problem(num_ships, 3)
    problem.types[:] = Real(0.5, 1.5)
    problem.function = objective_function
    
    n_generations = 50  ### PERBAIKAN: Kurangi generations untuk mempercepat (dari 100 ke 50)
    n_population = 200
    
    algorithm = NSGAIII(problem, divisions_outer=12, divisions_inner=2)
    algorithm.run(n_population * n_generations)
    
    if not algorithm.result:
        return np.zeros(num_ships)

    best_quotas = np.array(algorithm.result[0].variables) * ships_data['Prediksi'].values  ### PERBAIKAN: Skala ulang quotas dengan prediksi
    return best_quotas

# -----------------------------------------------------------------------------------
# Bagian 2: Logika Blockchain dan Smart Contract
# -----------------------------------------------------------------------------------

class Block:
    """
    Kelas yang merepresentasikan sebuah blok dalam blockchain.
    """
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        """
        Menghitung hash SHA-256 dari seluruh isi blok.
        """
        block_dict = {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }
        block_string = json.dumps(block_dict, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    """
    Kelas yang mengelola rantai blok.
    """
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Membuat blok pertama (genesis block) dengan data awal.
        """
        genesis_block = Block(0, ["Genesis Block"], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """Mengembalikan blok terakhir dalam rantai."""
        return self.chain[-1]
    
    def add_transaction(self, transaction_data):
        """Menambahkan transaksi baru ke daftar yang tertunda."""
        self.pending_transactions.append(transaction_data)

    def mine_pending_transactions(self):
        """
        Mencatat semua transaksi yang tertunda ke dalam blok baru dan menambahkannya ke rantai.
        """
        if not self.pending_transactions:
            return False

        new_block = Block(
            index=self.last_block.index + 1,
            transactions=self.pending_transactions,
            timestamp=time.time(),
            previous_hash=self.last_block.hash
        )
        new_block.hash = new_block.compute_hash()
        self.chain.append(new_block)
        
        self.pending_transactions = []
        return new_block

    def is_chain_valid(self):
        """
        Memverifikasi integritas seluruh rantai.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.compute_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

class SmartContract:
    """
    Kelas ini menyimulasikan smart contract.
    """
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.base_pnbp_fee = 10000000
        self.quota_fee_percentage = 0.05

    def execute_pnbp_process(self, wpp_id, ship_quotas, ship_data, manual_catches=None):
        """
        Fungsi ini mengotomatisasi alokasi kuota dan perhitungan PNBP, menggunakan hasil tangkap manual jika tersedia.
        """
        transactions = []
        for idx, row in ship_data.iterrows():
            ship_id = row['Kapal']
            kuota_kg = ship_quotas[idx]
            harga_ikan_rp = 35000
            
            # Gunakan hasil tangkap manual jika tersedia, jika tidak gunakan kuota sebagai default
            actual_catch_kg = manual_catches.get(ship_id, kuota_kg) if manual_catches else kuota_kg
            actual_catch_kg = max(0, actual_catch_kg)  # Pastikan tidak negatif
            
            hasil_tangkap_rp = actual_catch_kg * harga_ikan_rp
            biaya_5_persen = hasil_tangkap_rp * self.quota_fee_percentage
            total_pnbp_final = self.base_pnbp_fee + biaya_5_persen
            
            transaction = {
                "wpp_id": wpp_id,
                "ship_id": ship_id,
                "kuota_kg": kuota_kg,
                "hasil_tangkap_kg": actual_catch_kg,
                "biaya_awal_rp": self.base_pnbp_fee,
                "hasil_tangkapan_rp": hasil_tangkap_rp,
                "biaya_5_persen_rp": biaya_5_persen,
                "total_pnbp_final_rp": total_pnbp_final
            }
            transactions.append(transaction)
            self.blockchain.add_transaction(transaction)
        
        self.blockchain.mine_pending_transactions()
        
        return transactions

# -----------------------------------------------------------------------------------
# Bagian 3: Antarmuka Pengguna (GUI)
# -----------------------------------------------------------------------------------

class FisheriesPNBPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi PNBP Perikanan dengan Evaluasi")
        self.root.geometry("1400x900")

        self.blockchain = Blockchain()
        self.smart_contract = SmartContract(self.blockchain)

        self.all_data = generate_synthetic_data()
        self.wpp_list = sorted(self.all_data['WPP'].unique())
        self.current_wpp = None
        self.predicted_data = None
        self.manual_catches = {}  # Store manual catch data
        
        self.create_menu()
        self.create_main_frames()
        self.create_control_panel()
        self.create_tabs()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        blockchain_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Blockchain", menu=blockchain_menu)
        blockchain_menu.add_command(label="Tampilkan Buku Besar", command=self.show_blockchain_ledger)
        blockchain_menu.add_command(label="Input Hasil Tangkap Manual", command=self.open_manual_catch_input)
        blockchain_menu.add_separator()
        blockchain_menu.add_command(label="Verifikasi Rantai", command=self.verify_blockchain)

    def create_main_frames(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill="both", expand=True)

    def create_control_panel(self):
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Kontrol Aplikasi", padding="10")
        self.control_frame.pack(fill="x", pady=10)
        
        ttk.Label(self.control_frame, text="Pilih WPP:").pack(side="left", padx=5)
        self.wpp_combo = ttk.Combobox(self.control_frame, values=self.wpp_list)
        self.wpp_combo.pack(side="left", padx=5)
        self.wpp_combo.bind("<<ComboboxSelected>>", self.on_wpp_selected)

        ttk.Label(self.control_frame, text="Epochs LSTM:").pack(side="left", padx=(10, 2))
        self.epochs_var = tk.IntVar(value=50)
        self.epochs_spinbox = ttk.Spinbox(self.control_frame, from_=10, to=200, increment=10, textvariable=self.epochs_var, width=5)
        self.epochs_spinbox.pack(side="left", padx=(0, 10))

        self.lstm_button = ttk.Button(self.control_frame, text="1. Jalankan Prediksi LSTM", command=self.start_lstm_thread, state="disabled")
        self.lstm_button.pack(side="left", padx=10)
        
        self.nsga3_button = ttk.Button(self.control_frame, text="2. Jalankan Optimasi NSGA-III", command=self.start_nsga3_thread, state="disabled")
        self.nsga3_button.pack(side="left", padx=10)

        self.pnbp_button = ttk.Button(self.control_frame, text="3. Hitung & Catat PNBP ke Blockchain", command=self.start_pnbp_thread, state="disabled")
        self.pnbp_button.pack(side="left", padx=10)

        self.status_label = ttk.Label(self.control_frame, text="Status: Silakan pilih WPP", font=("TkDefaultFont", 10, "italic"))
        self.status_label.pack(side="left", padx=10)

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=5)
        
        self.tab_lstm = ttk.Frame(self.notebook)
        self.tab_nsga3 = ttk.Frame(self.notebook)
        self.tab_pnbp = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_lstm, text="Prediksi LSTM")
        self.notebook.add(self.tab_nsga3, text="Optimasi NSGA-III")
        self.notebook.add(self.tab_pnbp, text="PNBP & Blockchain")
        
        self.create_lstm_tab()
        self.create_nsga3_tab()
        self.create_pnbp_tab()

    def create_lstm_tab(self):
        self.lstm_tree = ttk.Treeview(self.tab_lstm, columns=("Kapal", "Prediksi Total (kg)"))
        self.lstm_tree.heading("#0", text="", anchor="w")
        self.lstm_tree.column("#0", width=0, stretch=tk.NO)
        self.lstm_tree.heading("Kapal", text="Kapal")
        self.lstm_tree.heading("Prediksi Total (kg)", text="Prediksi Total (kg)")
        self.lstm_tree.pack(fill="both", expand=True)

    def create_nsga3_tab(self):
        self.nsga3_tree = ttk.Treeview(self.tab_nsga3, columns=("Kapal", "Prediksi (kg)", "Kuota yang Dialokasikan (kg)"))
        self.nsga3_tree.heading("#0", text="", anchor="w")
        self.nsga3_tree.column("#0", width=0, stretch=tk.NO)
        self.nsga3_tree.heading("Kapal", text="Kapal")
        self.nsga3_tree.heading("Prediksi (kg)", text="Prediksi (kg)")
        self.nsga3_tree.heading("Kuota yang Dialokasikan (kg)", text="Kuota yang Dialokasikan (kg)")
        self.nsga3_tree.pack(fill="both", expand=True)

    def create_pnbp_tab(self):
        self.pnbp_tree = ttk.Treeview(self.tab_pnbp, columns=("WPP", "Kapal", "Biaya Awal (Rp)", "Kuota (kg)", "Hasil Tangkap (kg)", "Hasil Tangkapan (Rp)", "Biaya 5% (Rp)", "Total PNBP (Rp)"))
        self.pnbp_tree.heading("#0", text="", anchor="w")
        self.pnbp_tree.column("#0", width=0, stretch=tk.NO)
        
        for col in self.pnbp_tree["columns"]:
            self.pnbp_tree.heading(col, text=col, anchor="center")
            self.pnbp_tree.column(col, anchor="center", width=110)
        
        self.pnbp_tree.pack(fill="both", expand=True)

    def open_manual_catch_input(self):
        if not self.current_wpp:
            messagebox.showwarning("Peringatan", "Pilih WPP terlebih dahulu!")
            return
        
        if self.predicted_data is None:
            messagebox.showwarning("Peringatan", "Jalankan prediksi LSTM dan optimasi NSGA-III terlebih dahulu!")
            return

        input_window = tk.Toplevel(self.root)
        input_window.title("Input Hasil Tangkap Manual")
        input_window.geometry("400x600")

        ttk.Label(input_window, text="Masukkan Hasil Tangkap (kg) untuk Setiap Kapal", font=("TkDefaultFont", 12)).pack(pady=10)

        input_frame = ttk.Frame(input_window)
        input_frame.pack(fill="both", expand=True, padx=10, pady=10)

        entries = {}
        for idx, row in self.predicted_data.iterrows():
            ship_id = row['Kapal']
            ttk.Label(input_frame, text=f"{ship_id}:").pack(anchor="w")
            entry = ttk.Entry(input_frame)
            entry.pack(fill="x", pady=2)
            entries[ship_id] = entry

        def save_catches():
            try:
                self.manual_catches = {}
                for ship_id, entry in entries.items():
                    value = entry.get().strip()
                    if value:
                        catch = float(value)
                        if catch < 0:
                            raise ValueError(f"Hasil tangkap untuk {ship_id} tidak boleh negatif!")
                        self.manual_catches[ship_id] = catch
                    else:
                        self.manual_catches[ship_id] = self.predicted_data[self.predicted_data['Kapal'] == ship_id]['Kuota_Kg'].iloc[0] if 'Kuota_Kg' in self.predicted_data.columns else 0  ### PERBAIKAN: Handle jika Kuota_Kg belum ada
                messagebox.showinfo("Sukses", "Hasil tangkap manual berhasil disimpan!")
                input_window.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(input_window, text="Simpan", command=save_catches).pack(pady=10)
        ttk.Button(input_window, text="Batal", command=input_window.destroy).pack(pady=5)

    def on_wpp_selected(self, event):
        self.current_wpp = self.wpp_combo.get()
        self.status_label.config(text=f"Status: WPP '{self.current_wpp}' dipilih. Siap untuk langkah 1.")
        self.lstm_button.config(state="normal")
        self.nsga3_button.config(state="disabled")
        self.pnbp_button.config(state="disabled")
        self.predicted_data = None
        self.optimized_quotas = None
        self.manual_catches = {}  # Reset manual catches on WPP change
        self.clear_trees()

    def clear_trees(self):
        for tree in [self.lstm_tree, self.nsga3_tree, self.pnbp_tree]:
            for item in tree.get_children():
                tree.delete(item)

    def start_lstm_thread(self):
        self.status_label.config(text="Status: Melakukan prediksi LSTM. Harap tunggu...")
        self.disable_buttons()
        process_thread = threading.Thread(target=self.run_lstm_prediction)
        process_thread.start()

    def run_lstm_prediction(self):
        try:
            epochs = self.epochs_var.get()
            wpp_data = self.all_data[self.all_data['WPP'] == self.current_wpp].copy()
            ships = wpp_data['Kapal'].unique()

            self.predicted_data = []
            for ship in ships:
                prediction = predict_lstm(wpp_data, self.current_wpp, ship, epochs=epochs)
                total_pred = sum(prediction)
                self.predicted_data.append({'Kapal': ship, 'Prediksi': total_pred})
            
            self.predicted_data = pd.DataFrame(self.predicted_data)
            self.display_lstm_results()

        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan pada prediksi LSTM: {e}")
            print(f"Error LSTM: {e}")  ### PERBAIKAN: Tambah print untuk debug
        finally:
            self.status_label.config(text="Status: Prediksi LSTM Selesai. Lanjut ke langkah 2.")
            self.enable_buttons()
            self.nsga3_button.config(state="normal")
            self.notebook.select(self.tab_lstm)

    def display_lstm_results(self):
        self.clear_trees()
        for _, row in self.predicted_data.iterrows():
            self.lstm_tree.insert("", "end", values=(row['Kapal'], f"{row['Prediksi']:.2f} kg"))

    def start_nsga3_thread(self):
        if self.predicted_data is None or self.predicted_data.empty:  ### PERBAIKAN: Tambah check empty
            messagebox.showwarning("Peringatan", "Jalankan prediksi LSTM terlebih dahulu atau data kosong!")
            return
        
        self.status_label.config(text="Status: Menjalankan optimasi NSGA-III. Harap tunggu...")
        self.disable_buttons()
        process_thread = threading.Thread(target=self.run_nsga3_optimization)
        process_thread.start()

    def run_nsga3_optimization(self):
        try:
            self.optimized_quotas = optimize_nsga3(self.predicted_data)
            if self.optimized_quotas.size > 0:
                self.predicted_data['Kuota_Kg'] = self.optimized_quotas.round(2)
                self.display_nsga3_results()
            else:
                self.status_label.config(text="Status: Optimasi NSGA-III Selesai. Tidak ada kuota yang dialokasikan.")
                messagebox.showwarning("Peringatan", "Tidak ada kapal yang dapat dialokasikan kuota.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan pada optimasi NSGA-III: {e}")
            print(f"Error NSGA-III: {e}")  ### PERBAIKAN: Tambah print untuk debug
        finally:
            self.status_label.config(text="Status: Optimasi NSGA-III Selesai. Lanjut ke langkah 3.")
            self.enable_buttons()
            self.pnbp_button.config(state="normal")
            self.notebook.select(self.tab_nsga3)

    def display_nsga3_results(self):
        self.clear_trees()
        for _, row in self.predicted_data.iterrows():
            self.nsga3_tree.insert("", "end", values=(row['Kapal'], f"{row['Prediksi']:.2f} kg", f"{row['Kuota_Kg']:.2f} kg"))

    def start_pnbp_thread(self):
        if self.predicted_data is None:
            messagebox.showwarning("Peringatan", "Jalankan optimasi NSGA-III terlebih dahulu!")
            return

        self.status_label.config(text="Status: Menghitung & mencatat PNBP ke Blockchain...")
        self.disable_buttons()
        process_thread = threading.Thread(target=self.run_pnbp_and_blockchain)
        process_thread.start()

    def run_pnbp_and_blockchain(self):
        try:
            pnbp_transactions = self.smart_contract.execute_pnbp_process(
                self.current_wpp, 
                self.predicted_data['Kuota_Kg'].values, 
                self.predicted_data,
                self.manual_catches
            )
            self.display_pnbp_data(pnbp_transactions)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan pada proses PNBP & Blockchain: {e}")
            print(f"Error PNBP: {e}")  ### PERBAIKAN: Tambah print untuk debug
        finally:
            self.status_label.config(text="Status: Proses selesai!")
            self.enable_buttons()
            self.notebook.select(self.tab_pnbp)

    def display_pnbp_data(self, pnbp_transactions):
        for item in self.pnbp_tree.get_children():
            self.pnbp_tree.delete(item)

        total_biaya_awal = 0
        total_kuota_kg = 0
        total_hasil_tangkap_kg = 0
        total_hasil_tangkap_rp = 0
        total_biaya_5_persen = 0
        total_pnbp_final = 0

        for transaction in pnbp_transactions:
            kuota_kg = transaction['kuota_kg']
            hasil_tangkap_kg = transaction['hasil_tangkap_kg']
            biaya_awal_rp = transaction['biaya_awal_rp']
            hasil_tangkap_rp = transaction['hasil_tangkapan_rp']
            biaya_5_persen = transaction['biaya_5_persen_rp']
            total_per_kapal = transaction['total_pnbp_final_rp']

            total_biaya_awal += biaya_awal_rp
            total_kuota_kg += kuota_kg
            total_hasil_tangkap_kg += hasil_tangkap_kg
            total_hasil_tangkap_rp += hasil_tangkap_rp
            total_biaya_5_persen += biaya_5_persen
            total_pnbp_final += total_per_kapal

            # PERBAIKAN: Handle NaN atau negatif di formatting
            kuota_kg = max(0, kuota_kg)
            hasil_tangkap_kg = max(0, hasil_tangkap_kg)

            self.pnbp_tree.insert("", "end", values=(
                transaction['wpp_id'],
                transaction['ship_id'],
                f"Rp {biaya_awal_rp:,.0f}".replace(",", "#").replace(".", ",").replace("#", "."),
                f"{kuota_kg:,.2f} kg".replace(",", "#").replace(".", ",").replace("#", "."),
                f"{hasil_tangkap_kg:,.2f} kg".replace(",", "#").replace(".", ",").replace("#", "."),
                f"Rp {hasil_tangkap_rp:,.0f}".replace(",", "#").replace(".", ",").replace("#", "."),
                f"Rp {biaya_5_persen:,.0f}".replace(",", "#").replace(".", ",").replace("#", "."),
                f"Rp {total_per_kapal:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
            ))
        
        self.pnbp_tree.insert("", "end", values=("TOTAL", "", 
            f"Rp {total_biaya_awal:,.0f}".replace(",", "#").replace(".", ",").replace("#", "."),
            f"{total_kuota_kg:,.2f} kg".replace(",", "#").replace(".", ",").replace("#", "."),
            f"{total_hasil_tangkap_kg:,.2f} kg".replace(",", "#").replace(".", ",").replace("#", "."),
            f"Rp {total_hasil_tangkap_rp:,.0f}".replace(",", "#").replace(".", ",").replace("#", "."),
            f"Rp {total_biaya_5_persen:,.0f}".replace(",", "#").replace(".", ",").replace("#", "."),
            f"Rp {total_pnbp_final:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
        ))

    def disable_buttons(self):
        self.lstm_button.config(state="disabled")
        self.nsga3_button.config(state="disabled")
        self.pnbp_button.config(state="disabled")

    def enable_buttons(self):
        self.lstm_button.config(state="normal")
        self.nsga3_button.config(state="normal")
        self.pnbp_button.config(state="normal")

    def show_blockchain_ledger(self):
        ledger_window = tk.Toplevel(self.root)
        ledger_window.title("Buku Besar Blockchain")
        ledger_window.geometry("800x600")

        ledger_tree = ttk.Treeview(ledger_window, columns=("Index", "Timestamp", "Previous Hash", "Current Hash", "Transactions"))
        ledger_tree.heading("#0", text="", anchor="w")
        ledger_tree.column("#0", width=0, stretch=tk.NO)

        ledger_tree.heading("Index", text="Index")
        ledger_tree.heading("Timestamp", text="Timestamp")
        ledger_tree.heading("Previous Hash", text="Previous Hash")
        ledger_tree.heading("Current Hash", text="Current Hash")
        ledger_tree.heading("Transactions", text="Transactions")

        for col in ("Index", "Timestamp", "Previous Hash", "Current Hash", "Transactions"):
            ledger_tree.column(col, anchor="center", width=150)
            
        ledger_tree.pack(fill="both", expand=True)

        for block in self.blockchain.chain:
            block_data_str = json.dumps(block.transactions, indent=2)
            if len(block_data_str) > 200:  ### PERBAIKAN: Potong string jika terlalu panjang untuk display
                block_data_str = block_data_str[:200] + "..."
            timestamp_str = datetime.datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')

            ledger_tree.insert("", "end", values=(
                block.index, 
                timestamp_str, 
                block.previous_hash[:10] + "...", 
                block.hash[:10] + "...",
                block_data_str
            ))

    def verify_blockchain(self):
        is_valid = self.blockchain.is_chain_valid()
        if is_valid:
            messagebox.showinfo("Verifikasi Berhasil", "Rantai blockchain terverifikasi. Tidak ada data yang diubah.")
        else:
            messagebox.showwarning("Verifikasi Gagal", "Rantai blockchain tidak valid! Data mungkin telah diubah.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FisheriesPNBPApp(root)
    root.mainloop()