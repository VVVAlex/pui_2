# import tkinter
from tkinter import ttk
import customtkinter

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("250x300")
root.title("Treeview x Customtkinter")

frame_1 = customtkinter.CTkFrame(master=root)
frame_1.pack(pady=20, padx=20, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame_1, text="Treeview")
label.grid(pady=10)

# Treeview Customisation (theme colors are selected)
bg_color = root._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
text_color = root._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])
selected_color = root._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
print(bg_color, text_color, selected_color)

treestyle = ttk.Style()
treestyle.theme_use('default')
treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
root.bind("<<TreeviewSelect>>", lambda event: root.focus_set())

# Treeview widget data
treeview = ttk.Treeview(frame_1, height=6, show="tree")     # show="tree"
treeview.grid(padx=10)
treeview.insert('', '0', 'i1', text='Python')
treeview.insert('', '1', 'i2', text='Customtkinter')
treeview.insert('', '2', 'i3', text='Tkinter')
treeview.insert('i2', 'end', 'Frame', text='Frame')
treeview.insert('i2', 'end', 'Label', text='Label')
treeview.insert('i3', 'end', 'Treeview', text='Treeview')
treeview.move('i2', 'i1', 'end')
treeview.move('i3', 'i1', 'end')

root.mainloop()
