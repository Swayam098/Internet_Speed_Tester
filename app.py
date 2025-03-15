import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import speedtest
import threading
from ttkbootstrap import Style

class SpeedTestApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Internet Speed Test")
        self.master.geometry("500x400")
        self.style = Style(theme='flatly')

        # Initialize speedtest
        try:
            self.st = speedtest.Speedtest()
            self.st.get_best_server()  # Get the best server immediately
            self.server_info = self.st.results.server
        except Exception as e:
            messagebox.showerror("Error", f"Initialization failed: {str(e)}")
            self.master.destroy()
            return

        self.results_available = False
        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Heading
        heading = ttk.Label(main_frame, text="Internet Speed Test", 
                          font=('Helvetica', 20, 'bold'))
        heading.pack(pady=10)

        # Test button
        self.test_btn = ttk.Button(main_frame, text="Start Test", 
                                command=self.start_test, bootstyle='primary')
        self.test_btn.pack(pady=20)

        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill='x', pady=10)

        # Server Info
        ttk.Label(results_frame, text="Server:", font=('Helvetica', 12)).grid(row=0, column=0, sticky='w', padx=10)
        self.server_label = ttk.Label(results_frame, text=f"{self.server_info['host']} ({self.server_info['country']})", font=('Helvetica', 12, 'bold'))
        self.server_label.grid(row=0, column=1, sticky='w', padx=10)

        # Ping
        ttk.Label(results_frame, text="Ping:", font=('Helvetica', 12)).grid(row=1, column=0, sticky='w', padx=10)
        self.ping_label = ttk.Label(results_frame, text="—", font=('Helvetica', 12, 'bold'))
        self.ping_label.grid(row=1, column=1, sticky='w', padx=10)

        # Download Speed
        ttk.Label(results_frame, text="Download:", font=('Helvetica', 12)).grid(row=2, column=0, sticky='w', padx=10)
        self.download_label = ttk.Label(results_frame, text="—", font=('Helvetica', 12, 'bold'))
        self.download_label.grid(row=2, column=1, sticky='w', padx=10)

        # Upload Speed
        ttk.Label(results_frame, text="Upload:", font=('Helvetica', 12)).grid(row=3, column=0, sticky='w', padx=10)
        self.upload_label = ttk.Label(results_frame, text="—", font=('Helvetica', 12, 'bold'))
        self.upload_label.grid(row=3, column=1, sticky='w', padx=10)

        # Progress indicator
        self.progress_label = ttk.Label(main_frame, text="", font=('Helvetica', 10))
        self.progress_label.pack(pady=10)

        # Status message
        self.status_label = ttk.Label(main_frame, text="", font=('Helvetica', 10))
        self.status_label.pack(pady=5)

    def start_test(self):
        self.test_btn.config(state='disabled')
        self.progress_label.config(text="Testing...")
        self.status_label.config(text="")
        threading.Thread(target=self.run_speed_test).start()
        self.master.after(100, self.check_results)

    def run_speed_test(self):
        try:
            ping = self.st.results.ping  # Get the ping
            download_speed = self.st.download() / 1_000_000  # Convert to Mbps
            upload_speed = self.st.upload() / 1_000_000  # Convert to Mbps
            self.results = (ping, download_speed, upload_speed)
            self.results_available = True
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
