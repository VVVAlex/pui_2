import customtkinter as ctk


class Screen(ctk.CTkFrame):
    """Центральный фрейм"""

    def __init__(self, root):
        super().__init__(root, corner_radius=0, border_width=2, border_color="grey75")
        self.root = root
        self.frame_fild_50 = ctk.CTkFrame(
            master=self,
            corner_radius=0,
            border_width=1,
            border_color="green",
        )
        self.frame_fild_50.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.frame_fild_25 = ctk.CTkFrame(
            master=self,
            corner_radius=0,
            border_width=1,
            border_color="green",
        )
        self.frame_fild_25.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
