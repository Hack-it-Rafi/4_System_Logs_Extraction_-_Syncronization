import tkinter as tk
import time

def update_time():
    current_time = time.strftime('%H:%M:%S')
    label.config(text=current_time)
    root.after(1000, update_time)  # Update every 1000ms (1 second)

root = tk.Tk()
root.title("Always on Top Clock")

# Make sure these attributes are set after the main window is created
root.attributes("-topmost", True)
root.overrideredirect(True)  # Removes window decorations

# Adjust geometry - try different positions if needed
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"+{screen_width-250}+20")  # Position near top-right corner

# Set transparent background
root.wm_attributes("-transparentcolor", "black")

# Make sure the label has proper contrast and padding
label = tk.Label(root, 
                font=('Arial', 30), 
                bg='black',  # Match the transparent color
                fg='white',
                padx=10,
                pady=5)
label.pack()

# Force update the window immediately
root.update_idletasks()
root.update()

update_time()
root.mainloop()