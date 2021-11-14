import tkinter as tk
import ToolTip
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog

available_scripts = ["Serial link","DMVPN link"]

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class ScriptBuilder(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Script Builder")
        self.resizable(False,False)
        self.frames = dict()
        self.selected_script = ""
        self.clean_entries = {}
        self.calculable_variables = []
        self.calculated_variables = {}
        self.container = ttk.Frame(self)
        self.container.grid()
        self.previous_frame = ""
        self.final_script = ""

        for FrameClass in (HomePage, SerialBuildPage, DmvpnBuildPage, ScriptSavePage):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass] = frame
            frame.grid(row=0, column=0, sticky="NSEW")

        self.show_frame(HomePage, HomePage)

    def show_frame(self, page, previous_frame):
        self.previous_frame = previous_frame
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[page]
        if page == ScriptSavePage:
            script_save_frame = ScriptSavePage(self.container, self)
            self.frames[ScriptSavePage] = script_save_frame
            script_save_frame.grid(row=0, column=0, sticky="NSEW")
        else:
            frame.grid()

    def next_frame(self, selected_frame):
        self.selected_script = selected_frame
        if selected_frame == "":
            tk.messagebox.showerror(message="You must select a script to continue.",
                                    title="Script Builder: Error!")
        elif selected_frame == "Serial link":
            self.show_frame(SerialBuildPage,HomePage)
        elif selected_frame == "DMVPN link":
            self.show_frame(DmvpnBuildPage,HomePage)

    def generate_script(self):
        self.calculable_variables = read_required_inputs_from_file(self.selected_script, "calculable")
        self.calculated_variables = generate_variables(self.calculable_variables, self.clean_entries)
        self.final_script = load_only_the_script(self.selected_script)
        self.final_script = replace_variables_in_script(self.final_script, self.clean_entries, self.calculated_variables)
        self.final_script = convert_list_to_string(self.final_script)


class HomePage(ttk.Frame):
    def __init__(self, container, controller):
        self.controller = controller
        super().__init__(container)
        self.selected_script = tk.StringVar()
        label_frame_title = tk.Label(self, text="Script Builder", font=("Ariel", 25))
        label_frame_title.grid(row=0,column=0,columnspan = 2)
        label_selection_box = tk.Label(self, text="Please select your desired script:", font=("Ariel", 15))
        script_selector = ttk.Combobox(self, state="readonly", font=("Ariel", 15),
                                       textvariable=self.selected_script, values=available_scripts)
        label_selection_box.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        script_selector.grid(row=1, column=1, padx=5)
        next_button = tk.Button(self, text="Next", font=("Ariel", 15), bd=4,
                                command=lambda: controller.next_frame(self.selected_script.get()))
        next_button.grid(row=2, column=1, sticky="E", padx=5, pady=5)
        quit_button = tk.Button(self, text="Quit", font=("Ariel", 15), bd=4,command=quit)
        quit_button.grid(row=2, column=0, sticky="W", padx=5, pady=5)


class SerialBuildPage(ttk.Frame):
    def __init__(self, container, controller):
        self.controller = controller
        super().__init__(container)
        self.required_user_inputs = read_required_inputs_from_file("Serial link","user")
        self.text_entry_tooltips = read_help_tooltips_from_file("Serial link")
        self.number_required_inputs = len(self.required_user_inputs)
        self.raw_text_entries = {}
        self.clean_entries = {}

        label_frame_title = tk.Label(self, text="Serial Link Form", font=("Ariel", 25))
        next_button = tk.Button(self, text="Next", font=("Ariel", 15), bd=4,
                                command = self.check_before_next_page)
        quit_button = tk.Button(self, text="Quit", font=("Ariel", 15), bd=4,command=quit)
        back_button = tk.Button(self, text="Back", font=("Ariel", 15), bd=4,
                                command=lambda:controller.show_frame(HomePage,SerialBuildPage))

        label_frame_title.grid(row=0,column=0,columnspan=3)
        next_button.grid(row=self.number_required_inputs + 1, column=2, sticky="E", padx=5, pady=5)
        quit_button.grid(row=self.number_required_inputs + 1, column=1, sticky="W", padx=5, pady=5)
        back_button.grid(row=self.number_required_inputs + 1, column=0, sticky="W", padx=5, pady=5)

        for i in range(len(self.required_user_inputs)):
            label = tk.Label(self, text = self.required_user_inputs[i], font=("Ariel", 15))
            label.grid(row=i+1, column=0, sticky = "W", padx=5, pady=5)
            self.raw_text_entries[self.required_user_inputs[i]] = tk.Entry(self)
            self.raw_text_entries[self.required_user_inputs[i]].grid(row=1 + i, column=1,sticky = "E",padx=5, pady=5)
            ToolTip.CreateToolTip(self.raw_text_entries[self.required_user_inputs[i]], text = self.text_entry_tooltips[i])

    def check_before_next_page(self):
        for inputs in self.raw_text_entries:
            self.clean_entries[inputs] = self.raw_text_entries[inputs].get()
        if check_generic_errors(self.clean_entries):
            self.controller.clean_entries = self.clean_entries
            self.controller.generate_script()
            self.controller.show_frame(ScriptSavePage,SerialBuildPage)


class DmvpnBuildPage(ttk.Frame):
    def __init__(self, container, controller):
        self.controller = controller
        super().__init__(container)
        self.required_user_inputs = read_required_inputs_from_file("DMVPN link","user")
        self.text_entry_tooltips = read_help_tooltips_from_file("DMVPN link")
        self.number_required_inputs = len(self.required_user_inputs)
        self.raw_text_entries = {}
        self.clean_entries = {}

        label_frame_title = tk.Label(self, text="DMVPN Link Form", font=("Ariel", 25))
        next_button = tk.Button(self, text="Next", font=("Ariel", 15), bd=4,
                                command = self.check_before_next_page)
        quit_button = tk.Button(self, text="Quit", font=("Ariel", 15), bd=4,command=quit)
        back_button = tk.Button(self, text="Back", font=("Ariel", 15), bd=4,
                                command=lambda:controller.show_frame(HomePage,DmvpnBuildPage))

        label_frame_title.grid(row=0,column=0,columnspan=3)
        next_button.grid(row=self.number_required_inputs + 1, column=2, sticky="E", padx=5, pady=5)
        quit_button.grid(row=self.number_required_inputs + 1, column=1, sticky="W", padx=5, pady=5)
        back_button.grid(row=self.number_required_inputs + 1, column=0, sticky="W", padx=5, pady=5)

        for i in range(len(self.required_user_inputs)):
            label = tk.Label(self, text = self.required_user_inputs[i], font=("Ariel", 15))
            label.grid(row=i+1, column=0, sticky = "W", padx=5, pady=5)
            self.raw_text_entries[self.required_user_inputs[i]] = tk.Entry(self)
            self.raw_text_entries[self.required_user_inputs[i]].grid(row=1 + i, column=1,sticky = "E",padx=5, pady=5)
            ToolTip.CreateToolTip(self.raw_text_entries[self.required_user_inputs[i]], text = self.text_entry_tooltips[i])

    def check_before_next_page(self):
        for inputs in self.raw_text_entries:
            self.clean_entries[inputs] = self.raw_text_entries[inputs].get()
        if check_generic_errors(self.clean_entries):
            self.controller.clean_entries = self.clean_entries
            self.controller.generate_script()
            self.controller.show_frame(ScriptSavePage, DmvpnBuildPage)


class ScriptSavePage(ttk.Frame):
    def __init__(self, container, controller):
        self.controller = controller
        super().__init__(container)
        self.final_inputs = {}
        self.final_script = ""
        label_frame_title = tk.Label(self, text="Script preview and save", font=("Ariel", 25))
        save_button = tk.Button(self, text="Save", font=("Ariel", 15), bd=4, command = self.save_file)
        quit_button = tk.Button(self, text="Quit", font=("Ariel", 15), bd=4,command=quit)
        back_button = tk.Button(self, text="Back", font=("Ariel", 15), bd=4, command =
                                lambda : controller.show_frame(controller.previous_frame, ScriptSavePage))
        script_display = tk.Text(self)
        script_display.insert("end",controller.final_script)
        script_display.configure(state="disabled", wrap = "none")
        text_v_scroll = tk.Scrollbar(self, orient="vertical", command=script_display.yview)
        text_h_scroll = tk.Scrollbar(self, orient="horizontal", command=script_display.xview)
        script_display.configure(wrap = None, yscrollcommand=text_v_scroll.set, xscrollcommand=text_h_scroll.set)
        text_v_scroll.grid(row=1, column=3, sticky="nsew")
        text_h_scroll.grid(row=3, column=0,columnspan = 3, sticky="nsew")
        label_frame_title.grid(row=0,column=0,columnspan=3)
        script_display.grid(row=1, column=0, columnspan=3)
        save_button.grid(row=4, column=2, sticky="E", padx=5, pady=5)
        quit_button.grid(row=4, column=1, padx=5, pady=5)
        back_button.grid(row=4, column=0, sticky="W", padx=5, pady=5)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension = ".txt")
        with open(file_path, "w") as text_file:
            text_file.write(self.controller.final_script)
            text_file.close()


def convert_list_to_string(script_list):
    script_string = "".join(script_list)
    return script_string


def replace_variables_in_script(template_script, user_inputs, calculated_inputs):
    all_variables = {}
    all_variables.update(calculated_inputs)
    all_variables.update(user_inputs)
    line_number = 0
    new_script = template_script
    for lines in new_script:
        for variables in all_variables:
            if variables in lines and lines[0] != "#":
                new_line = lines.replace(variables, str(all_variables[variables]))
                new_line = new_line.replace("*", "")
                new_script.pop(line_number)
                new_script.insert(line_number, new_line)
        line_number += 1
    return new_script


def generate_variables(calculable_variables, user_inputs):
    calculated_variables = {}
    if "Management IP" in calculable_variables:
        management_ip = calculate_management_ip(user_inputs["Asset Number"])
        calculated_variables["Management IP"] = management_ip
    if "Loopback IP" in calculable_variables:
        loopback_ip = calculate_loopback_ip(user_inputs["Asset Number"])
        calculated_variables["Loopback IP"] = loopback_ip
    if "DHCP Start" in calculable_variables:
        dhcp_start = calculate_dhcp_start(user_inputs["Asset Number"])
        calculated_variables["DHCP Start"] = dhcp_start
    if "DHCP End" in calculable_variables:
        dhcp_end = calculate_dhcp_end(user_inputs["Asset Number"])
        calculated_variables["DHCP End"] = dhcp_end
    if "LAN IP" in calculable_variables:
        lan_ip = calculate_lan_ip(user_inputs["Asset Number"])
        calculated_variables["LAN IP"] = lan_ip
    if "WAN IP" in calculable_variables:
        wan_ip = calculate_wan_ip(user_inputs["Asset Number"])
        calculated_variables["WAN IP"] = wan_ip
    return calculated_variables


def calculate_wan_ip(asset_number):
    asset_number = str(asset_number)
    asset_number.lstrip("0")
    asset_number = int(asset_number)
    ip = f"172.16.{asset_number}.1"
    return ip


def calculate_lan_ip(asset_number):
    asset_number = str(asset_number)
    asset_number.lstrip("0")
    asset_number = int(asset_number)
    ip = f"172.29.232.{asset_number}"
    return ip

def calculate_dhcp_end(asset_number):
    asset_number = str(asset_number)
    asset_number.lstrip("0")
    asset_number = int(asset_number)
    if (asset_number / 2) % 2 == 0:
        ip = f"192.168.{int(asset_number / 2)}.3"
    else:
        ip = f"192.168.{int(asset_number / 2)}.131"
    return ip


def calculate_dhcp_start(asset_number):
    asset_number = str(asset_number)
    asset_number.lstrip("0")
    asset_number = int(asset_number)
    if (asset_number / 2) % 2 == 0:
        ip = f"192.168.{int(asset_number / 2)}.2"
    else:
        ip = f"192.168.{int(asset_number / 2)}.130"
    return ip


def calculate_loopback_ip(asset_number):
    asset_number = str(asset_number)
    asset_number.lstrip("0")
    asset_number = int(asset_number)
    if (asset_number / 2) % 2 == 0:
        ip = f"192.168.{int(asset_number / 2)}.126"
    else:
        ip = f"192.168.{int(asset_number / 2)}.254"
    return ip


def calculate_management_ip(asset_number):
    asset_number = str(asset_number)
    asset_number.lstrip("0")
    asset_number = int(asset_number)
    if (asset_number / 2) % 2 == 0:
        ip = f"192.168.{int(asset_number / 2)}.1"
    else:
        ip = f"192.168.{int(asset_number / 2)}.129"
    return ip


def load_only_the_script(required_script):
    entire_script = []
    line_number = 0
    line_script_starts = 0
    script = load_required_script_file(required_script)

    for lines in script:
        if "start of script" in lines:
            line_script_starts = line_number
        line_number += 1
    for values in script[line_script_starts+1:]:
        entire_script.append(values)
    return entire_script


def load_required_script_file(required_script):
    if required_script == "Serial link":
        file_path = "Serial_Script.txt"
    elif required_script == "DMVPN link":
        file_path = "Dmvpn_Script.txt"
    with open(file_path) as f:
        template_script = f.readlines()
    f.close()
    return template_script


def read_required_inputs_from_file(required_script,user_or_calculable):
    template_script = load_required_script_file(required_script)
    line_number = 0
    required_user_inputs = []
    required_calculable_inputs = []
    text_lines = []

    for lines in template_script:
        line_number += 1
        text_lines.append(lines)
        if lines[0] == "#" and lines[1] == "*":
            required_user_inputs.append(lines.lstrip("#*").rstrip("\n"))
        elif lines[0] == "#" and lines[1] == "+":
            required_calculable_inputs.append(lines.lstrip("#+").rstrip("\n"))
    if user_or_calculable == "user":
        return required_user_inputs
    else:
        return required_calculable_inputs


def read_help_tooltips_from_file(required_script):
    template_script = load_required_script_file(required_script)
    line_number = 0
    text_entry_help_tooltips = []
    text_lines = []

    for lines in template_script:
        line_number += 1
        text_lines.append(lines)
        if lines[0] == "#" and lines[1] == "@":
            text_entry_help_tooltips.append(lines.lstrip("#@").rstrip("\n"))
    return text_entry_help_tooltips


def check_generic_errors(input_fields):
    if "Asset Number" in input_fields:
        try:
            input_fields["Asset Number"] = int(input_fields["Asset Number"])
        except ValueError:
            tk.messagebox.showerror(message="Asset number is not a valid number",
                                    title="Script Builder: Error!")
            return False
        if input_fields["Asset Number"] > 250:
            tk.messagebox.showerror(message="Asset number cannot be greater than 250",
                                    title="Script Builder: Error!")
            return False
        if input_fields["Asset Number"] == 0:
            tk.messagebox.showerror(message="Asset number cannot be 0",
                                    title="Script Builder: Error!")
            return False
    for values in input_fields:
        if input_fields[values] == "":
            tk.messagebox.showerror(message="Please complete all the required fields before continuing",
                                    title="Script Builder: Error!")
            return False
    return True


if __name__ == "__main__":
    app = ScriptBuilder()
    app.mainloop()