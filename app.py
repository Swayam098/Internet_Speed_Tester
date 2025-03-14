import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import subprocess
import json
import threading
from ttkbootstrap import Style

class SpeedTestApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Internet Speed Test")
        self.master.geometry("500x400")
        self.style = Style(theme='flatly')

        self.servers = []
        self.results_available = False
        self.create_widgets()

        # Fetch servers in a separate thread
        threading.Thread(target=self.get_available_servers).start()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Heading
        heading = ttk.Label(main_frame, text="Internet Speed Test", font=('Helvetica', 20, 'bold'))
        heading.pack(pady=10)

        # Server selection dropdown
        self.server_var = tk.StringVar()
        self.server_dropdown = ttk.Combobox(main_frame, textvariable=self.server_var, state='readonly')
        self.server_dropdown.pack(pady=10)

        # Test button
        self.test_btn = ttk.Button(main_frame, text="Start Test", command=self.start_test, bootstyle='primary')
        self.test_btn.pack(pady=20)

        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill='x', pady=10)

        # Ping
        ttk.Label(results_frame, text="Ping:", font=('Helvetica', 12)).grid(row=0, column=0, sticky='w', padx=10)
        self.ping_label = ttk.Label(results_frame, text="—", font=('Helvetica', 12, 'bold'))
        self.ping_label.grid(row=0, column=1, sticky='w', padx=10)

        # Download Speed
        ttk.Label(results_frame, text="Download:", font=('Helvetica', 12)).grid(row=1, column=0, sticky='w', padx=10)
        self.download_label = ttk.Label(results_frame, text="—", font=('Helvetica', 12, 'bold'))
        self.download_label.grid(row=1, column=1, sticky='w', padx=10)

        # Upload Speed
        ttk.Label(results_frame, text="Upload:", font=('Helvetica', 12)).grid(row=2, column=0, sticky='w', padx=10)
        self.upload_label = ttk.Label(results_frame, text="—", font=('Helvetica', 12, 'bold'))
        self.upload_label.grid(row=2, column=1, sticky='w', padx=10)

        # Progress indicator
        self.progress_label = ttk.Label(main_frame, text="", font=('Helvetica', 10))
        self.progress_label.pack(pady=10)

        # Status message
        self.status_label = ttk.Label(main_frame, text="", font=('Helvetica', 10))
        self.status_label.pack(pady=5)

    def get_available_servers(self):
        try:
            # Fetch server information using Speedtest CLI
            result = subprocess.run(['speedtest', '-L'], capture_output=True, text=True)
            if result.returncode == 0:
                servers_output = result.stdout.splitlines()[2:]  # Skip first two lines of headers
                if servers_output:  # Check if servers were found
                    for line in servers_output:
                        server_id, details = line.split(")", 1)
                        server_id = server_id.strip() + ")"  # Including the closing parenthesis for proper formatting
                        self.servers.append((server_id, details.strip()))
                    self.server_dropdown['values'] = [details for _, details in self.servers]
                else:
                    messagebox.showerror("Error", "No servers available. Please check your connection.")
            else:
                messagebox.showerror("Error", "Failed to fetch servers. Ensure Speedtest CLI is working.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch servers: {str(e)}")

    def start_test(self):
        selected_server_index = self.server_dropdown.current()
        if selected_server_index == -1:
            messagebox.showwarning("Warning", "Please select a server before running the test")
            return
        
        selected_server_id = self.servers[selected_server_index][0]  # Get server ID

        # Disable the test button during testing
        self.test_btn.config(state='disabled')
        self.progress_label.config(text="Testing...")
        self.status_label.config(text="")
        
        # Run speed test in a separate thread
        threading.Thread(target=self.run_speed_test, args=(selected_server_id,)).start()

    def run_speed_test(self, server_id):
        try:
            # Run Speedtest CLI with selected server
            result = subprocess.run(['speedtest', '--server-id', server_id, '--format=json'], capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                ping = data['ping']['latency']
                download_speed = data['download']['bandwidth'] / 1_000_000  # Convert to Mbps
                upload_speed = data['upload']['bandwidth'] / 1_000_000  # Convert to Mbps
                self.results = (ping, download_speed, upload_speed)
                self.results_available = True
            else:
                self.status_label.config(text="Error: Speedtest failed")
                self.progress_label.config(text="")
                self.test_btn.config(state='normal')
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.progress_label.config(text="")
            self.test_btn.config(state='normal')

    def check_results(self):
        if self.results_available:
            self.update_gui()
            self.results_available = False
            self.test_btn.config(state='normal')
            self.progress_label.config(text="")
            self.status_label.config(text="Test complete!", foreground='green')
        else:
            self.master.after(100, self.check_results)

    def update_gui(self):
        self.ping_label.config(text=f"{self.results[0]:.2f} ms")
        self.download_label.config(text=f"{self.results[1]:.2f} Mbps")
        self.upload_label.config(text=f"{self.results[2]:.2f} Mbps")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()
