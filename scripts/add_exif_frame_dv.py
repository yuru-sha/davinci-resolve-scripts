import os
import sys

# --- Configuration: Add Library Path ---
# VENV_PATH will be replaced during installation by Makefile
VENV_PATH = "{{VENV_PATH}}"

def find_site_packages():
    """Find site-packages directory for required libraries."""
    # 1. Check environment variable (highest priority)
    venv_path = os.environ.get("DAVINCI_RESOLVE_SCRIPTS_VENV")
    if venv_path and os.path.isdir(venv_path):
        return venv_path

    # 2. Use path embedded during installation
    if VENV_PATH != "{{VENV_PATH}}" and os.path.isdir(VENV_PATH):
        return VENV_PATH

    return None

site_packages_path = find_site_packages()
if not site_packages_path:
    print("ERROR: Could not find required libraries.")
    print("This script requires Python dependencies (Pillow, rawpy, exifread).")
    print("Please set environment variable with the path to site-packages:")
    print("  export DAVINCI_RESOLVE_SCRIPTS_VENV=/path/to/.venv/lib/pythonX.Y/site-packages")
    sys.exit(1)

if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

try:
    import exifread
    import rawpy
    from PIL import ExifTags, Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"Error loading libraries: {e}")
    sys.exit(1)

# --- Exif Logic ---
def get_exif_data_pillow(image):
    exif_data = {}
    info = image.getexif()
    if not info: return exif_data
    for tag, value in info.items():
        decoded = ExifTags.TAGS.get(tag, tag)
        exif_data[decoded] = value
    if not exif_data.get("FNumber"):
        try:
            info_legacy = image._getexif()
            if info_legacy:
                for tag, value in info_legacy.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    exif_data[decoded] = value
        except: pass
    return exif_data

def get_exif_data_raw(file_path):
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, details=False)
    except:
        return {}
    data = {}
    def get_tag_val(search_keys):
        for k in tags:
            for sk in search_keys:
                if sk in k: return tags[k]
        return None
    model_tag = get_tag_val(["Image Model", "Model"])
    if model_tag: data["Model"] = str(model_tag)
    make_tag = get_tag_val(["Image Make", "Make"])
    if make_tag: data["Make"] = str(make_tag)
    lens_tag = get_tag_val(["EXIF LensModel", "LensModel", "LensInfo", "Lens"])
    if lens_tag: data["LensModel"] = str(lens_tag)
    fl_tag = get_tag_val(["EXIF FocalLength", "FocalLength"])
    if fl_tag and hasattr(fl_tag, "values"):
        val = fl_tag.values[0]
        data["FocalLength"] = float(val.num) / float(val.den)
    fn_tag = get_tag_val(["EXIF FNumber", "FNumber", "ApertureValue"])
    if fn_tag and hasattr(fn_tag, "values"):
        val = fn_tag.values[0]
        data["FNumber"] = float(val.num) / float(val.den)
    iso_tag = get_tag_val(["EXIF ISOSpeedRatings", "ISOSpeed", "ISO"])
    if iso_tag: data["ISOSpeedRatings"] = str(iso_tag)
    et_tag = get_tag_val(["EXIF ExposureTime", "ExposureTime", "ShutterSpeedValue"])
    if et_tag and hasattr(et_tag, "values"):
        val = et_tag.values[0]
        if val.num == 1 and val.den > 1:
            data["ExposureTimeString"] = f"1/{val.den}"
            data["ExposureTime"] = 1.0 / float(val.den)
        else:
            data["ExposureTime"] = float(val.num) / float(val.den)
    return data

def format_shutter_speed(speed, speed_str=None):
    if speed_str: return speed_str
    if not speed: return ""
    if speed < 0.0: return ""
    if speed < 1:
        if speed > 0: return f"1/{int(1/speed)}"
        return ""
    return f"{speed}"

def create_exif_string(exif):
    raw_model = str(exif.get("Model", "Unknown Camera")).strip()
    make = str(exif.get("Make", "")).strip()
    model_clean = raw_model
    if make:
        import re
        pattern = re.compile(re.escape(make), re.IGNORECASE)
        model_clean = pattern.sub("", model_clean).strip()
        first_word = make.split()[0]
        if first_word:
            pattern_fw = re.compile(re.escape(first_word), re.IGNORECASE)
            model_clean = pattern_fw.sub("", model_clean).strip()
    for junk in ["CORPORATION", "Corporation", "Inc.", "Ltd."]:
        model_clean = model_clean.replace(junk, "").strip()
    if not model_clean: model_clean = raw_model
    simple_make = make.split()[0].title() if make else ""
    if simple_make and simple_make.lower() not in model_clean.lower():
         camera_name = f"{simple_make} {model_clean}"
    else: camera_name = model_clean
    lens = str(exif.get("LensModel", "")).strip()
    if not lens: lens = str(exif.get("LensModel", exif.get("LensInfo", ""))).strip()
    if lens and lens != camera_name: top_text = f"{camera_name} / {lens}"
    else: top_text = camera_name
    focal_length = exif.get("FocalLength", 0)
    f_number = exif.get("FNumber", 0)
    iso = exif.get("ISOSpeedRatings", 0)
    exposure_time = exif.get("ExposureTime", 0)
    exposure_time_str = exif.get("ExposureTimeString", None)
    try: fl_str = f"{int(focal_length)}mm" if focal_length else ""
    except: fl_str = f"{focal_length}mm"
    try: fn_str = f"f/{f_number}" if f_number else ""
    except: fn_str = f"f/{f_number}"
    ss_str = f"{format_shutter_speed(exposure_time, exposure_time_str)}s" if (exposure_time or exposure_time_str) else ""
    iso_str = f"ISO {iso}" if iso else ""
    settings_parts = [p for p in [fl_str, fn_str, ss_str, iso_str] if p]
    settings_str = " | ".join(settings_parts)
    return top_text, settings_str

def open_image(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
        img = Image.open(file_path)
        exif = get_exif_data_pillow(img)
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except: pass
        return img, exif
    if ext in [".arw", ".cr2", ".cr3", ".nef", ".dng", ".raf", ".orf"]:
        try:
            with rawpy.imread(file_path) as raw:
                rgb = raw.postprocess(use_camera_wb=True)
                img = Image.fromarray(rgb)
                exif = get_exif_data_raw(file_path)
                return img, exif
        except: return None, {}
    return None, {}

def add_frame(image_path, user_options=None):
    img, exif = open_image(image_path)
    if img is None: return None

    if user_options and "camera_text" in user_options:
        camera_text = user_options["camera_text"]
        settings_text = user_options["settings_text"]
    else:
        camera_text, settings_text = create_exif_string(exif)
        if camera_text == "Unknown Camera" and not settings_text:
            settings_text = "No Exif Data"

    border_color = (255, 255, 255)
    text_color_main = (0, 0, 0)
    text_color_sub = (80, 80, 80)
    border_ratio = 0.05
    polaroid_bottom = True

    if user_options:
        if user_options.get("border_color") == "Black":
            border_color = (0, 0, 0)
            text_color_main = (255, 255, 255)
            text_color_sub = (200, 200, 200)
        try:
            val = float(user_options.get("border_size", 5))
            border_ratio = val / 100.0
        except: pass
        polaroid_bottom = user_options.get("polaroid_style", True)

    width, height = img.size
    base_dim = min(width, height)
    border_uniform = int(base_dim * border_ratio)
    if polaroid_bottom: border_bottom = int(border_uniform * 3.6)
    else: border_bottom = border_uniform

    new_width = width + (border_uniform * 2)
    new_height = height + border_uniform + border_bottom
    new_img = Image.new("RGB", (new_width, new_height), border_color)
    new_img.paste(img, (border_uniform, border_uniform))
    draw = ImageDraw.Draw(new_img)

    if camera_text or settings_text:
        available_h = border_bottom
        font_size_main = int(available_h * 0.25)
        font_size_sub = int(available_h * 0.18)
        def load_font(name, size):
            candidates = {
                "Bold": ["/System/Library/Fonts/SFNS-Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "Arial Bold.ttf"],
                "Regular": ["/System/Library/Fonts/SFNS.ttf", "/Library/Fonts/Arial.ttf", "Arial.ttf"]
            }
            search_list = candidates.get(name, []) + candidates["Regular"]
            for fpath in search_list:
                try: return ImageFont.truetype(fpath, size)
                except: continue
            return ImageFont.load_default()
        font_main = load_font("Bold", font_size_main)
        font_sub = load_font("Regular", font_size_sub)
        center_x = new_width // 2
        settings_clean = settings_text.replace(" | ", "   ")
        bbox_main = draw.textbbox((0, 0), camera_text, font=font_main)
        h_main = bbox_main[3] - bbox_main[1]
        w_main = bbox_main[2] - bbox_main[0]
        bbox_sub = draw.textbbox((0, 0), settings_clean, font=font_sub)
        h_sub = bbox_sub[3] - bbox_sub[1]
        w_sub = bbox_sub[2] - bbox_sub[0]
        gap = int(h_main * 0.4)
        total_text_h = h_main + gap + h_sub
        border_area_y_start = height + border_uniform
        text_block_start_y = border_area_y_start + (border_bottom - total_text_h) / 2
        draw.text((center_x - w_main / 2, text_block_start_y), camera_text, fill=text_color_main, font=font_main)
        draw.text((center_x - w_sub / 2, text_block_start_y + h_main + gap), settings_clean, fill=text_color_sub, font=font_sub)

    root, ext = os.path.splitext(image_path)
    output_path = f"{root}_framed.jpg"
    new_img.save(output_path, quality=95, exif=img.info.get("exif"))
    return output_path

def main():
    try: resolve_obj = resolve
    except NameError:
        print("Run within DaVinci Resolve.")
        sys.exit(1)
    project = resolve_obj.GetProjectManager().GetCurrentProject()
    if not project: return
    media_pool = project.GetMediaPool()
    timeline = project.GetCurrentTimeline()
    if not timeline: return

    target_item = timeline.GetCurrentVideoItem()
    if not target_item:
        print("No item under playhead.")
        return
    mp_item = target_item.GetMediaPoolItem()
    if not mp_item: return
    file_path = mp_item.GetClipProperty("File Path")
    if not file_path or "_framed" in file_path: return
    file_name = os.path.basename(file_path)

    # UI Logic for Studio
    temp_img, temp_exif = open_image(file_path)
    if not temp_img: return
    default_cam, default_set = create_exif_string(temp_exif)

    fusion = resolve_obj.Fusion()
    ui = fusion.UIManager
    dispatcher = fusion.Dispatcher

    win = dispatcher.AddWindow({
        "ID": "ExifWin", "Geometry": [500, 300, 450, 320], "WindowTitle": "Exif Frame (Studio)",
    }, [
        ui.VGroup({"Spacing": 10}, [
            ui.Label({"Text": f"Target: {file_name}", "Weight": 0, "Font": ui.Font({"PixelSize": 12, "Style": "Bold"})}),
            ui.VGroup({"Weight": 0, "Frame": True}, [
                ui.Label({"Text": "Text Options", "Weight": 0}),
                ui.LineEdit({"ID": "CamInput", "Text": default_cam, "PlaceholderText": "Camera Model"}),
                ui.LineEdit({"ID": "SetInput", "Text": default_set, "PlaceholderText": "Settings"}),
            ]),
            ui.VGroup({"Weight": 0, "Frame": True}, [
                ui.Label({"Text": "Border Design", "Weight": 0}),
                ui.HGroup([
                    ui.Label({"Text": "Style:", "Weight": 0}),
                    ui.ComboBox({"ID": "ColorCombo", "Weight": 1}),
                    ui.CheckBox({"ID": "PolaroidCheck", "Text": "Polaroid Bottom", "Checked": True, "Weight": 1})
                ]),
                ui.HGroup([
                    ui.Label({"Text": "Size (%):", "Weight": 0}),
                    ui.Slider({"ID": "SizeSlider", "Minimum": 0, "Maximum": 20, "Value": 5, "Weight": 2}),
                    ui.Label({"ID": "SizeLabel", "Text": "5%", "Weight": 0})
                ]),
            ]),
            ui.HGroup({"Weight": 0}, [
                ui.Button({"ID": "Execute", "Text": "Process", "Weight": 1}),
                ui.Button({"ID": "Cancel", "Text": "Cancel", "Weight": 1})
            ])
        ])
    ])

    win.GetItems().ColorCombo.AddItem("White")
    win.GetItems().ColorCombo.AddItem("Black")
    user_data = None

    def OnClose(ev): dispatcher.ExitLoop()
    def OnCancel(ev): dispatcher.ExitLoop()
    def OnExecute(ev):
        nonlocal user_data
        itm = win.GetItems()
        user_data = {
            "camera_text": itm.CamInput.Text,
            "settings_text": itm.SetInput.Text,
            "border_color": itm.ColorCombo.CurrentText,
            "border_size": itm.SizeSlider.Value,
            "polaroid_style": itm.PolaroidCheck.Checked == 1
        }
        dispatcher.ExitLoop()
    def OnSlider(ev): win.GetItems().SizeLabel.Text = f"{ev.Value}%"

    win.On.ExifWin.Close = OnClose
    win.On.Cancel.Clicked = OnCancel
    win.On.Execute.Clicked = OnExecute
    win.On.SizeSlider.ValueChanged = OnSlider

    win.Show()
    dispatcher.RunLoop()
    win.Hide()

    if not user_data: return

    try:
        output = add_frame(file_path, user_options=user_data)
        if output:
            if hasattr(mp_item, "ReplaceClip"): mp_item.ReplaceClip(output)
            else: media_pool.ImportMedia([output])
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
