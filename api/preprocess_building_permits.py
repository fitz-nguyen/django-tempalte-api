import csv
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

csv.field_size_limit(2147483647)


def escape_quotes(field):
    return field.replace('"', '&quot;')


def convert_file(input_file, output_file, skip_null_state, lowercase_city, uppercase_state):
    with open(input_file, 'r', encoding='iso-8859-1') as infile, \
            open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        header = next(reader)  # Read the header
        writer.writerow(header)  # Write header to output file

        # Find the index of the property_address_state and property_address_city columns
        state_index = header.index('PropertyAddressState') if 'PropertyAddressState' in header else -1
        city_index = header.index('PropertyAddressCity') if 'PropertyAddressCity' in header else -1

        for row in reader:
            if skip_null_state and state_index != -1 and (len(row) <= state_index or not row[state_index].strip()):
                continue  # Skip this row

            # Convert PropertyAddressCity to lowercase if the option is selected
            if lowercase_city and city_index != -1 and len(row) > city_index:
                row[city_index] = row[city_index].lower() if row[city_index] is not None else ""

            # Convert PropertyAddressState to uppercase if the option is selected
            if uppercase_state and state_index != -1 and len(row) > state_index:
                row[state_index] = row[state_index].upper() if row[state_index] is not None else ""

            escaped_row = [escape_quotes(field) for field in row]
            writer.writerow(escaped_row)


def update_loading_animation():
    loading_chars = "←↖↑↗→↘↓↙"
    current_char = loading_chars[int(time.time() * 5) % len(loading_chars)]
    loading_char_label.config(text=current_char)
    if loading:
        root.after(100, update_loading_animation)


def select_file():
    global loading
    input_file = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
    )
    if input_file:
        # Generate default output filename
        input_filename = os.path.basename(input_file)
        input_name, input_ext = os.path.splitext(input_filename)
        default_output = f"{input_name}_output{input_ext}"

        output_file = filedialog.asksaveasfilename(
            title="Save converted file as",
            defaultextension=input_ext,
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")],
            initialfile=default_output
        )
        if output_file:
            # Disable the select file button and checkboxes, and show loading
            btn_select_file.config(state=tk.DISABLED)
            chk_skip_null.config(state=tk.DISABLED)
            chk_lowercase_city.config(state=tk.DISABLED)
            chk_uppercase_state.config(state=tk.DISABLED)
            loading_frame.pack()
            loading = True
            update_loading_animation()  # Start the loading animation
            root.update()

            # Run the conversion in a separate thread
            thread = threading.Thread(target=run_conversion, args=(input_file, output_file,
                                      skip_null_state.get(), lowercase_city.get(), uppercase_state.get()))
            thread.start()


def run_conversion(input_file, output_file, skip_null_state, lowercase_city, uppercase_state):
    global loading
    start_time = time.time()
    try:
        convert_file(input_file, output_file, skip_null_state, lowercase_city, uppercase_state)
        execution_time = time.time() - start_time
        root.after(0, conversion_complete, "Success", f"File converted successfully!\nExecution time: {execution_time:.2f} seconds")
    except Exception as e:
        root.after(0, conversion_complete, "Error", f"An error occurred: {e}")
    finally:
        loading = False


def conversion_complete(title, message):
    global loading
    # Hide loading and re-enable the select file button and checkboxes
    loading_frame.pack_forget()
    btn_select_file.config(state=tk.NORMAL)
    chk_skip_null.config(state=tk.NORMAL)
    chk_lowercase_city.config(state=tk.NORMAL)
    chk_uppercase_state.config(state=tk.NORMAL)
    loading = False

    # Show the result message
    messagebox.showinfo(title, message)


# Create the main window
root = tk.Tk()
root.title("Django Template - Preprocessing Tool")
root.geometry("600x600")  # Set fixed window size

# Center the window on the screen
window_width = 600
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Create variables to hold the checkbox states
skip_null_state = tk.BooleanVar(value=True)
lowercase_city = tk.BooleanVar(value=True)  # Default to True
uppercase_state = tk.BooleanVar(value=True)  # Default to True

# Create and place the "Select File" button at the top
btn_select_file = tk.Button(root, text="Select File", command=select_file)
btn_select_file.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

# Create and place the checkboxes below the button
chk_skip_null = tk.Checkbutton(root, text="Skip rows with null PropertyAddressState", variable=skip_null_state)
chk_skip_null.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

chk_lowercase_city = tk.Checkbutton(root, text="Convert PropertyAddressCity to lowercase", variable=lowercase_city)
chk_lowercase_city.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

chk_uppercase_state = tk.Checkbutton(root, text="Convert PropertyAddressState to uppercase", variable=uppercase_state)
chk_uppercase_state.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# Create a frame for loading labels
loading_frame = tk.Frame(root)
loading_label = tk.Label(loading_frame, text="Processing...", font=("Arial", 12))
loading_label.pack(side=tk.LEFT)
loading_char_label = tk.Label(loading_frame, text="", font=("Arial", 12))
loading_char_label.pack(side=tk.LEFT)

# Add this near the top of your script, after imports
loading = False

# Run the application
root.mainloop()
