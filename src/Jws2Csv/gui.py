import os
import tkinter as tk
from tkinter import filedialog
from src.Jws2Csv.extractor import Extractor
from time import sleep

def select_folder():
    folder_path = filedialog.askdirectory(title="Select Folder")
    folder_var.set(folder_path)
    update_preview_list(folder_path)

def update_preview_list(folder_path):
    preview_listbox.delete(0, tk.END)  # Clear the listbox
    for filename in os.listdir(folder_path):
        if filename.endswith('.jws'):
            preview_listbox.insert(tk.END, filename)

def update_status_label(message):
    status_label.config(text=message)

def select_save_location():
    save_path = filedialog.askdirectory(title="Select Save Location")
    save_var.set(save_path)

def convert_selected_files():
    update_status_label("Converting...")
    jws_folder = folder_var.get()
    save_location = save_var.get()

    selected_files = preview_listbox.curselection()

    include_sample_name = sample_name_var.get()
    include_comment = comment_var.get()
    include_csv_filename = csv_filename_var.get()
    include_header = header_var.get()
    include_units = units_var.get()

    for index in selected_files:
        filename = preview_listbox.get(index)
        if filename.endswith('.jws'):
            convert_file(os.path.join(jws_folder, filename), save_location,
                         include_sample_name, include_comment,
                         include_csv_filename, include_header, include_units)

def convert_all_files():
    update_status_label("Converting...")
    jws_folder = folder_var.get()
    save_location = save_var.get()

    include_sample_name = sample_name_var.get()
    include_comment = comment_var.get()
    include_csv_filename = csv_filename_var.get()
    include_header = header_var.get()
    include_units = units_var.get()

    update_preview_list(jws_folder)  # Clear and update the preview list

    for filename in os.listdir(jws_folder):
        if filename.endswith('.jws'):
            convert_file(os.path.join(jws_folder, filename), save_location,
                         include_sample_name, include_comment,
                         include_csv_filename, include_header, include_units)

def convert_file(jws_file_path, save_location, include_sample_name, include_comment,
                 include_csv_filename, include_header, include_units):
    extractor = Extractor(jws_file_path)
    extractor.read_header()
    unpacked_data = extractor.read_data()
    csv_data = list(zip(*unpacked_data))
    csv_filename = os.path.splitext(os.path.basename(jws_file_path))[0] + '.csv'
    with open(os.path.join(save_location, csv_filename), 'w') as f:
        if include_sample_name:
            f.write(extractor.sample_name + ',' + '' + '\n')
        if include_comment:
            f.write(extractor.comment + ',' + '' + '\n')
        if include_csv_filename:
            f.write(csv_filename.split('.csv')[0] + ',' + '' + '\n')
        if include_header:
            f.write('Wavelength,Absorbance' + '\n')
        if include_units:
            f.write('nm,au' + '\n')
        for row in csv_data:
            f.write(','.join(map(str, row)) + '\n')

    update_status_label("Conversion Complete")

# Create the GUI
root = tk.Tk()
root.title("JWS to CSV Converter")

# Window geometry
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width = int(screen_width * 2/3)
height = int(screen_height * 2/3)
x = int(screen_width/2 - width/2)
y = int(screen_height/2 - height/2)
root.geometry(f'{width}x{height}+{x}+{y}')

# Input and buttons
folder_var = tk.StringVar()
save_var = tk.StringVar()

folder_label = tk.Label(root, text="Select JWS Folder:")
folder_label.pack()

folder_entry = tk.Entry(root, textvariable=folder_var)
folder_entry.pack(fill=tk.X, padx=20, pady=(0, 10))  # Span the full width of the window

folder_button = tk.Button(root, text="Browse", command=select_folder)
folder_button.pack()

save_label = tk.Label(root, text="Select Save Location:")
save_label.pack()

save_entry = tk.Entry(root, textvariable=save_var)
save_entry.pack(fill=tk.X, padx=20, pady=(0, 10))  # Span the full width of the window

save_button = tk.Button(root, text="Browse", command=select_save_location)
save_button.pack()

convert_selected_button = tk.Button(root, text="Convert Selected Files", command=convert_selected_files)
convert_selected_button.pack()

convert_all_button = tk.Button(root, text="Convert All Files", command=convert_all_files)
convert_all_button.pack()



# Preview Listbox
preview_frame = tk.Frame(root)
preview_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

preview_label = tk.Label(preview_frame, text="Preview .jws Files:")
preview_label.pack()

preview_scrollbar = tk.Scrollbar(preview_frame)
preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

preview_listbox = tk.Listbox(preview_frame, yscrollcommand=preview_scrollbar.set, selectmode=tk.MULTIPLE)
preview_listbox.pack(fill=tk.BOTH, expand=True)
preview_scrollbar.config(command=preview_listbox.yview)

status_label = tk.Label(root, text="Ready", fg="green")
status_label.pack()

sample_name_var = tk.BooleanVar()
sample_name_checkbox = tk.Checkbutton(root, text="Include Sample Name", variable=sample_name_var)
sample_name_checkbox.pack(side=tk.LEFT, padx=10)

comment_var = tk.BooleanVar()
comment_checkbox = tk.Checkbutton(root, text="Include Comment", variable=comment_var)
comment_checkbox.pack(side=tk.LEFT, padx=10)

csv_filename_var = tk.BooleanVar()
csv_filename_checkbox = tk.Checkbutton(root, text="Include CSV Filename", variable=csv_filename_var)
csv_filename_checkbox.pack(side=tk.LEFT, padx=10)

header_var = tk.BooleanVar()
header_checkbox = tk.Checkbutton(root, text="Include Header", variable=header_var)
header_checkbox.pack(side=tk.LEFT, padx=10)

units_var = tk.BooleanVar()
units_checkbox = tk.Checkbutton(root, text="Include Units", variable=units_var)
units_checkbox.pack(side=tk.LEFT, padx=10)



root.mainloop()
