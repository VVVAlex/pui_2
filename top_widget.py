import customtkinter as ctk
from PIL import Image
import os


class CTkTop(ctk.CTkToplevel):

    def __init__(self,
                 widget: any = None,
                 title: str = "",
                 width: int = 400,
                 height: int = 200,
                 border_width: int = 0,
                 border_color: str = None,
                 bg_color: str = "default",
                 title_color: str = "default",
                 corner_radius: int = 15,
                 alpha: float = 0.95,
                 font: tuple = None,
                 icon: str = "",
                 btn_close: bool = True,
                 ):
        
        super().__init__()
        self.widget = widget
        # self.withdraw()
        self.width = 250 if width < 250 else width
        self.height = 150 if height < 150 else height
        self.spawn_x = int((self.winfo_screenwidth() - self.width) / 2)
        self.spawn_y = int((self.winfo_screenheight() - self.height) / 2) + 150
        self.after(10)
        self.geometry(f"{self.width}x{self.height}+{self.spawn_x}+{self.spawn_y}")
        self.alpha = alpha

        if icon:
            size = (25, 25)
            image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons', icon + '.png')
            self.icon = ctk.CTkImage(Image.open(image_path), size=size)
        else:
            self.icon = None

        self.btn_close = btn_close

        # self.after(200, lambda: self.overrideredirect(True))
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes('-alpha', self.alpha)
        self.grab_set()
        self.focus_set()
        # self.wait_window()
        
        self.transparent_color = self._apply_appearance_mode(self.cget("fg_color"))        # str
        # self.transparent_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkToplevel"]["fg_color"])
        # self.transparent_color = ctk.ThemeManager.theme["CTkToplevel"]["fg_color"]       # [str, str]
        self.attributes("-transparentcolor", self.transparent_color)
        self.transient()
     
        self.title = title
        self.resizable(width=True, height=True)
        self.lift()
        
        self.config(background=self.transparent_color)
        self.corner_radius = corner_radius
        self.font = font
        self.border_width = border_width

        # self.text_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        # self.selected_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        # self.bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

        if bg_color == "default":
            self.bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        else:
            self.bg_color = bg_color
        
        if title_color == "default":
            self.title_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        else:
            self.title_color = title_color
            
        if border_color == "default":
            self.border_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["border_color"])
        else:
            self.border_color = border_color
        
        self.frame = ctk.CTkFrame(self,
                                  bg_color=self.transparent_color,
                                  corner_radius=self.corner_radius,
                                  border_width=self.border_width,
                                  border_color=self.border_color)
        self.frame.grid(sticky="nsew")

        if self.btn_close:
            self.button_close = ctk.CTkButton(self.frame, corner_radius=10, width=0, height=0,
                                              hover=False, border_width=0,
                                              text_color=self.title_color,
                                              text="✕", fg_color="transparent", command=self.destroy)           # close
            self.button_close.grid(row=0, column=1, sticky="ne", padx=5+self.border_width, pady=5+self.border_width)
        if self.title or self.icon:
            self.title_label = ctk.CTkLabel(self.frame, text=self.title, text_color=self.title_color, font=self.font,
                                            image=self.icon, justify="left", padx=10, compound='left'
                                            )
            self.title_label.grid(row=0, column=0, sticky="nw", padx=(15, 30), pady=5)

        if not self.btn_close and not self.title and not self.icon:
            fr = ctk.CTkFrame(self.frame, width=1, height=1, fg_color="transparent")
            fr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5+self.border_width,
                    pady=5+self.border_width)
        
        self.frame.bind("<B1-Motion>", self.move_window)
        self.frame.bind("<ButtonPress-1>", self.oldxyset)
        
        # self.w_get = ctk.CTkLabel(self.frame, text='Message_!',
        #                           font=self.font, width=self.width/2, height=self.height/2)

        self.w_get = ctk.CTkFrame(self.frame)
        self.w_get.grid(row=1, column=0, columnspan=2, padx=5, sticky="nsew")
        
        # self.label = ctk.CTkLabel(self.frame, text='-', width=1, height=1)
        self.label = ctk.CTkFrame(self.frame, width=1, height=1, fg_color="transparent")
        self.label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5+self.border_width, pady=5+self.border_width)
        self.bind("<Escape>", lambda e: self.destroy())

    def oldxyset(self, event):
        self.oldx = event.x
        self.oldy = event.y
    
    def move_window(self, event):
        self.y = event.y_root - self.oldy
        self.x = event.x_root - self.oldx
        self.geometry(f'+{self.x}+{self.y}')

    # def close(self, arg=None):
    #     if self.widget:
    #         if hasattr(self.widget, 'close'):
    #             self.widget.close()
    #     self.destroy()
        
        
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    # ctk.set_appearance_mode("Light")
    app = ctk.CTk()
    # bg_color = app._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
    x = CTkTop('Test', font=("Roboto Medium", -16), border_width=2, title_color='red', width=800, height=600)
    f = ctk.CTkFrame(x.w_get)
    lb = ctk.CTkLabel(f, text='Message_!',    # width=x.width/2, height=x.height/2,
                      width=400, height=200
                      # bg_color=bg_color, font=("Roboto Medium", -16)
                      )
    lb.pack(fill="both", expand=True)
    f.pack(fill="both", expand=True)
    app.mainloop()
    