import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import eleanor
import numpy as np


global_data = {
    "time": None,
    "flux": None,
    "flux_label": None
}


def generate_light_curve():
    object_name = entry.get().strip()
    flux_type = flux_option.get()
    
    if not object_name:
        messagebox.showerror("Input Error", "Please enter a valid TIC ID!")
        return

    try:
   
        star = eleanor.Source(tic=int(object_name))
        data = eleanor.TargetData(star, height=15, width=15, bkg_size=31, do_psf=False)

        print('Found TIC {0} (Gaia {1}), with TESS magnitude {2}, RA {3}, and Dec {4}'
              .format(star.tic, star.gaia, star.tess_mag, star.coords[0], star.coords[1]))

        q = data.quality == 0
        time = data.time[q]

    
        if flux_type == "Raw Flux":
            flux = data.raw_flux[q] / np.nanmedian(data.raw_flux[q])
            flux_label = "Raw Flux"
        elif flux_type == "Corrected Flux":
            flux = data.corr_flux[q] / np.nanmedian(data.corr_flux[q])
            flux_label = "Corrected Flux"
        elif flux_type == "PCA Flux":
            if data.pca_flux is None:  
                messagebox.showerror("Data Error", "PCA flux is not available for this TIC ID.")
                return
            flux = data.pca_flux[q] / np.nanmedian(data.pca_flux[q])
            flux_label = "PCA Flux"
        else:
            messagebox.showerror("Flux Error", "Invalid flux type selected!")
            return

      
        global_data["time"] = time
        global_data["flux"] = flux
        global_data["flux_label"] = flux_label

       
        bjd_min.set(np.floor(time.min()))
        bjd_max.set(np.ceil(time.max()))

       
        refresh_plot()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate light curve: {str(e)}")


def refresh_plot():
    time = global_data["time"]
    flux = global_data["flux"]
    flux_label = global_data["flux_label"]

    if time is None or flux is None:
        messagebox.showerror("Error", "No light curve data to refresh!")
        return

    try:
       
        t_min = float(bjd_min.get())
        t_max = float(bjd_max.get())

        if t_min >= t_max:
            messagebox.showerror("Input Error", "BJD min must be less than BJD max!")
            return

        
        mask = (time >= t_min) & (time <= t_max)
        filtered_time = time[mask]
        filtered_flux = flux[mask]

        if len(filtered_time) == 0:
            messagebox.showerror("Range Error", "No data points found in the selected BJD range!")
            return

       
        for widget in plot_frame.winfo_children():
            widget.destroy()

       
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(filtered_time, filtered_flux, s=15, label=flux_label)
        ax.set_ylabel('Normalized Flux')
        ax.set_xlabel('Time [BJD - 2457000]')
        ax.set_title(f'Light Curve for TIC {entry.get().strip()}')
        ax.set_xlim(t_min, t_max)
        ax.legend()
        ax.grid()

        
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for BJD range!")


root = tk.Tk()
root.title("TESS Light Curve Generator (powered by eleanor)")

#input
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Enter TIC ID:").grid(row=0, column=0, padx=5, pady=5)
entry = tk.Entry(input_frame, width=20)
entry.grid(row=0, column=1, padx=5, pady=5)
generate_button = tk.Button(input_frame, text="Generate Light Curve", command=generate_light_curve)
generate_button.grid(row=0, column=3, padx=5, pady=5)

#flux
flux_frame = tk.Frame(root)
flux_frame.pack(pady=5)

tk.Label(flux_frame, text="Select Flux Type:").pack(side=tk.LEFT, padx=5)
flux_option = ttk.Combobox(flux_frame, values=["Raw Flux", "Corrected Flux", "PCA Flux"])
flux_option.pack(side=tk.LEFT, padx=5)
flux_option.set("Corrected Flux") 

#bjd range
bjd_frame = tk.Frame(root)
bjd_frame.pack(pady=5)

tk.Label(bjd_frame, text="BJD Min:").pack(side=tk.LEFT, padx=5)
bjd_min = tk.StringVar()
bjd_min_entry = tk.Entry(bjd_frame, textvariable=bjd_min, width=10)
bjd_min_entry.pack(side=tk.LEFT, padx=5)

tk.Label(bjd_frame, text="BJD Max:").pack(side=tk.LEFT, padx=5)
bjd_max = tk.StringVar()
bjd_max_entry = tk.Entry(bjd_frame, textvariable=bjd_max, width=10)
bjd_max_entry.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(bjd_frame, text="Refresh Plot", command=refresh_plot)
refresh_button.pack(side=tk.LEFT, padx=10)

#plot 
plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()

