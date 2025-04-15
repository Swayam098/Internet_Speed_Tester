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
            # Initialize Speedtest CLI object
            st = speedtest.Speedtest()

            # Get the best server based on ping
            st.get_best_server()

            # Get the best server's details
            best_server = st.results.server
            self.servers.append((best_server['id'], f"{best_server['name']}, {best_server['country']}"))

            if self.servers:
                # Update dropdown with the best server
                self.server_dropdown['values'] = [details for _, details in self.servers]

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch server: {str(e)}")

    def start_test(self):
        selected_server_index = self.server_dropdown.current()  # ✅ Get selected server index
        if selected_server_index == -1:
            messagebox.showwarning("Warning", "Please select a server before running the test")
            return

        selected_server_id = self.servers[selected_server_index][0]  # ✅ Get selected server ID

        self.test_btn.config(state='disabled')  # ✅ Disable the button while testing
        self.progress_label.config(text="Testing...")
        self.status_label.config(text="")

        # ✅ Run the test in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.run_speed_test, args=(selected_server_id,)).start()

        # ✅ Check for results every 100ms (non-blocking loop using Tkinter's event loop)
        self.master.after(100, self.check_results)

    def run_speed_test(self, server_id):
        try:
            # Initialize Speedtest CLI object
            st = speedtest.Speedtest()

            # Set the server for the speed test
            st.get_best_server()  # This automatically selects the best server by ping
            st.get_servers([server_id])  # Select the server by ID (if it's a valid server)

            # Perform the test
            ping = st.results.ping
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps

            # Store the results
            self.results = (ping, download_speed, upload_speed)
            self.results_available = True

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground='red')
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
