from guizero import App, Text, PushButton, TextBox, Box
import json
import include.use_cam as scan

settings_dir = "/home/user/Desktop/include/settings.json"

def start_scan():
    settings_info = {
        "width":width_input.value,
        "height":height_input.value,
        "exposure_bw_length":exposure_bw_input.value,
        "exposure_r_length":exposure_r_input.value,
        "exposure_g_length":exposure_g_input.value,
        "exposure_b_length":exposure_b_input.value,
        "gain":gain_input.value,
        "led_amount":led_amount_input.value,
        "com_port":com_port_input.value
    }

    settings_json = json.dumps(settings_info, indent=4)
    with open(settings_dir,"w") as outfile:
        outfile.write(settings_json)
    
    scan.run_scanner(settings_info)

    app.destroy()

# Reads in from settings.json for previous settings to use as default
with open(settings_dir,'r') as settings_file:
    settings = json.load(settings_file)
painting_width = settings['width']
painting_height = settings['height']
exposure_bw = settings['exposure_bw_length']
exposure_r = settings['exposure_r_length']
exposure_g = settings['exposure_g_length']
exposure_b = settings['exposure_b_length']
gain = settings['gain']
led_amount = settings['led_amount']
com_port = settings['com_port']

text_width = 15

app = App(title="High-Resolution Scanner")
# Widgets

# Settings title box
settings_title_box = Box(app, width='fill', align='top')
settings_title = Text(settings_title_box, text="Settings")

# Takes in the settings
settings_box = Box(app, layout='grid', width='fill', align='top')


width_label = Text(settings_box, text="Enter Painting Width:", grid=[0,0], align='left')
width_input = TextBox(settings_box, grid=[1,0], width=text_width, text=painting_width)

height_label = Text(settings_box, text="Enter Painting Height:", grid=[0,1], align='left')
height_input = TextBox(settings_box, grid=[1,1], width=text_width, text=painting_height)

exposure_bw_label = Text(settings_box, text="Enter B&W Exposure Length(us):", grid=[0,2], align='left')
exposure_bw_input = TextBox(settings_box, grid=[1,2], width=text_width, text=exposure_bw)

exposure_r_label = Text(settings_box, text="Enter Red Exposure Length(us):", grid=[0,3], align='left')
exposure_r_input = TextBox(settings_box, grid=[1,3], width=text_width, text=exposure_r)

exposure_g_label = Text(settings_box, text="Enter Green Exposure Length(us):", grid=[0,4], align='left')
exposure_g_input = TextBox(settings_box, grid=[1,4], width=text_width, text=exposure_g)

exposure_b_label = Text(settings_box, text="Enter Blue Exposure Length(us):", grid=[0,5], align='left')
exposure_b_input = TextBox(settings_box, grid=[1,5], width=text_width, text=exposure_b)

gain_label = Text(settings_box, text="Enter Gain:", grid=[0,6], align='left')
gain_input = TextBox(settings_box, grid=[1,6], width=text_width, text=gain)

led_amount_label = Text(settings_box, text="Enter LED Amount:", grid=[0,7], align='left')
led_amount_input = TextBox(settings_box, grid=[1,7], width=text_width, text=led_amount)

com_port_label = Text(settings_box, text="Enter COM Port:", grid=[0,8], align='left')
com_port_input = TextBox(settings_box, grid=[1,8], width=text_width, text=com_port)

space1 = Text(settings_box, text=" ", grid=[0,9], align='left')
space2 = Text(settings_box, text=" ", grid=[1,9], align='left')

# Button to start the scan
button = PushButton(app, text="Start Scan", command=start_scan)

app.display()

