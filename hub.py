import customtkinter as ctk
import json
import os
import urllib.request
import ssl
import threading
from datetime import datetime, date
from icalendar import Calendar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1100x720")
app.title("LifeHub - Unified Dashboard")

# Ensures lifehub_data.json is saved in the same directory as hub.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "lifehub_data.json")

DEFAULT_DATA = {
    "tasks": [],
    "habits": {"Hydrate (2L)": False, "Read 20 Mins": False, "Workout / Gym": False},
    "notes": "",
    "ical_urls": []
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                if "feeds" in data and isinstance(data["feeds"], list):
                    data["ical_urls"] = [f["url"] if isinstance(f, dict) else str(f) for f in data["feeds"]]
                    del data["feeds"]
                elif "ical_url" in data and data["ical_url"]:
                    if "ical_urls" not in data or not isinstance(data["ical_urls"], list):
                        data["ical_urls"] = []
                    data["ical_urls"].append(data["ical_url"])
                    del data["ical_url"]
                
                for key, val in DEFAULT_DATA.items():
                    data.setdefault(key, val)
                if not isinstance(data.get("ical_urls"), list):
                    data["ical_urls"] = []
                return data
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(hub_data, file, indent=4)

hub_data = load_data()

# --- HEADER ---
header = ctk.CTkLabel(app, text="My LifeHub", font=ctk.CTkFont(size=26, weight="bold"))
header.pack(pady=10)

main_frame = ctk.CTkFrame(app, fg_color="transparent")
main_frame.pack(fill="both", expand=True, padx=15, pady=5)

# ================= LEFT COLUMN =================
left_col = ctk.CTkFrame(main_frame, fg_color="transparent")
left_col.pack(side="left", fill="both", expand=True, padx=10)

# --- TASKS WIDGET ---
tasks_frame = ctk.CTkFrame(left_col)
tasks_frame.pack(fill="both", expand=True, pady=(0, 10))

ctk.CTkLabel(tasks_frame, text="Assignments & Goals", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

task_scroll = ctk.CTkScrollableFrame(tasks_frame, fg_color="transparent", height=130)
task_scroll.pack(fill="both", expand=True, padx=10)

task_container = ctk.CTkFrame(task_scroll, fg_color="transparent")
task_container.pack(fill="both", expand=True)

def render_tasks():
    for widget in task_container.winfo_children():
        widget.destroy()
    for idx, task_name in enumerate(hub_data["tasks"]):
        row = ctk.CTkFrame(task_container, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        cb = ctk.CTkCheckBox(
            row, text=task_name, 
            command=lambda i=idx: remove_task(i)
        )
        cb.pack(side="left", anchor="w", padx=5)
        
        del_btn = ctk.CTkButton(
            row, text="✕", width=24, height=24, fg_color="transparent", 
            hover_color="#882222", text_color="#ff5555",
            command=lambda i=idx: remove_task(i)
        )
        del_btn.pack(side="right", padx=5)

def remove_task(index):
    if 0 <= index < len(hub_data["tasks"]):
        hub_data["tasks"].pop(index)
        save_data()
        render_tasks()

def add_task():
    new_task = task_entry.get().strip()
    if new_task:
        hub_data["tasks"].append(new_task)
        save_data()
        task_entry.delete(0, "end")
        render_tasks()

entry_frame = ctk.CTkFrame(tasks_frame, fg_color="transparent")
entry_frame.pack(pady=8, fill="x", padx=10)

task_entry = ctk.CTkEntry(entry_frame, placeholder_text="New task...", width=200)
task_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
task_entry.bind("<Return>", lambda event: add_task())

ctk.CTkButton(entry_frame, text="Add", width=60, command=add_task).pack(side="right")
render_tasks()

# --- HABIT TRACKER WIDGET ---
habits_frame = ctk.CTkFrame(left_col)
habits_frame.pack(fill="both", expand=True)

ctk.CTkLabel(habits_frame, text="Daily Habit Tracker", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

habit_scroll = ctk.CTkScrollableFrame(habits_frame, fg_color="transparent", height=130)
habit_scroll.pack(fill="both", expand=True, padx=10)

habit_container = ctk.CTkFrame(habit_scroll, fg_color="transparent")
habit_container.pack(fill="both", expand=True)

def toggle_habit(habit_key, var):
    hub_data["habits"][habit_key] = bool(var.get())
    save_data()

def remove_habit(habit_key):
    if habit_key in hub_data["habits"]:
        del hub_data["habits"][habit_key]
        save_data()
        render_habits()

def render_habits():
    for widget in habit_container.winfo_children():
        widget.destroy()
    for habit_name, status in hub_data["habits"].items():
        row = ctk.CTkFrame(habit_container, fg_color="transparent")
        row.pack(fill="x", pady=2)
        var = ctk.IntVar(value=1 if status else 0)
        cb = ctk.CTkCheckBox(
            row, text=habit_name, variable=var, 
            command=lambda name=habit_name, v=var: toggle_habit(name, v)
        )
        cb.pack(side="left", anchor="w", padx=5)
        
        del_btn = ctk.CTkButton(
            row, text="✕", width=24, height=24, fg_color="transparent", 
            hover_color="#882222", text_color="#ff5555",
            command=lambda name=habit_name: remove_habit(name)
        )
        del_btn.pack(side="right", padx=5)

def add_habit():
    new_habit = habit_entry.get().strip()
    if new_habit and new_habit not in hub_data["habits"]:
        hub_data["habits"][new_habit] = False
        save_data()
        habit_entry.delete(0, "end")
        render_habits()

habit_entry_frame = ctk.CTkFrame(habits_frame, fg_color="transparent")
habit_entry_frame.pack(pady=8, fill="x", padx=10)

habit_entry = ctk.CTkEntry(habit_entry_frame, placeholder_text="New habit...", width=200)
habit_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
habit_entry.bind("<Return>", lambda event: add_habit())

ctk.CTkButton(habit_entry_frame, text="Add Habit", width=70, command=add_habit).pack(side="right")
render_habits()


# ================= RIGHT COLUMN =================
right_col = ctk.CTkFrame(main_frame, fg_color="transparent")
right_col.pack(side="right", fill="both", expand=True, padx=10)

# --- CALENDAR FEED WIDGET ---
cal_frame = ctk.CTkFrame(right_col)
cal_frame.pack(fill="both", expand=True, pady=(0, 10))

cal_header_frame = ctk.CTkFrame(cal_frame, fg_color="transparent")
cal_header_frame.pack(fill="x", padx=10, pady=5)

ctk.CTkLabel(cal_header_frame, text="Upcoming Events", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

def open_calendar_tutorial():
    popup = ctk.CTkToplevel(app)
    popup.title("How to Get Your iCal Link")
    popup.geometry("500x420")
    popup.grab_set()
    
    ctk.CTkLabel(popup, text="Finding Your Calendar Feed URL", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
    
    textbox = ctk.CTkTextbox(popup, width=450, height=300)
    textbox.pack(padx=20, pady=10)
    
    tutorial_text = (
        "1. CANVAS / SCHOOL PORTALS:\n"
        "   - Go to Canvas Dashboard -> Calendar.\n"
        "   - Scroll down on right side -> Click 'Calendar Feed'.\n"
        "   - Copy the full link in the box.\n\n"
        "2. GOOGLE CALENDAR:\n"
        "   - Open Google Calendar web.\n"
        "   - Settings -> Integrate calendar.\n"
        "   - Copy 'Secret address in iCal format'.\n\n"
        "3. APPLE CALENDAR:\n"
        "   - Right-click calendar -> Share Calendar.\n"
        "   - Turn on 'Public Calendar' -> Copy link."
    )
    textbox.insert("1.0", tutorial_text)
    textbox.configure(state="disabled")

def open_manage_feeds():
    popup = ctk.CTkToplevel(app)
    popup.title("Manage Calendar Feeds")
    popup.geometry("550x420")
    popup.grab_set()

    ctk.CTkLabel(popup, text="Manage Saved Calendar Feeds", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

    status_lbl = ctk.CTkLabel(popup, text="", font=ctk.CTkFont(size=12))
    status_lbl.pack(pady=2)

    add_frame = ctk.CTkFrame(popup, fg_color="transparent")
    add_frame.pack(fill="x", padx=20, pady=5)

    new_url_entry = ctk.CTkEntry(add_frame, placeholder_text="Paste new iCal Feed URL...", width=360)
    new_url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

    list_frame = ctk.CTkScrollableFrame(popup, width=480, height=220)
    list_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def refresh_feed_list():
        for widget in list_frame.winfo_children():
            widget.destroy()
        if not hub_data["ical_urls"]:
            ctk.CTkLabel(list_frame, text="No feeds added yet.", text_color="gray").pack(pady=10)
            return

        for idx, url_str in enumerate(hub_data["ical_urls"]):
            row = ctk.CTkFrame(list_frame)
            row.pack(fill="x", pady=3, padx=5)
            disp_text = url_str if len(url_str) < 45 else url_str[:42] + "..."
            ctk.CTkLabel(row, text=disp_text, anchor="w").pack(side="left", padx=5, fill="x", expand=True)
            ctk.CTkButton(
                row, text="✕", width=30, fg_color="#cf3333", hover_color="#992222", 
                command=lambda i=idx: remove_feed(i)
            ).pack(side="right", padx=5)

    def add_feed():
        url = new_url_entry.get().strip()
        if not url:
            status_lbl.configure(text="Please paste a URL first!", text_color="orange")
            return
        if url in hub_data["ical_urls"]:
            status_lbl.configure(text="That URL is already in your list!", text_color="yellow")
            return
            
        hub_data["ical_urls"].append(url)
        save_data()
        new_url_entry.delete(0, "end")
        status_lbl.configure(text="Feed added successfully!", text_color="#2FA572")
        refresh_feed_list()
        fetch_events()

    def remove_feed(index):
        hub_data["ical_urls"].pop(index)
        save_data()
        status_lbl.configure(text="Feed removed.", text_color="red")
        refresh_feed_list()
        fetch_events()

    ctk.CTkButton(add_frame, text="Add", width=60, command=add_feed).pack(side="right")
    refresh_feed_list()

btn_group = ctk.CTkFrame(cal_header_frame, fg_color="transparent")
btn_group.pack(side="right")

ctk.CTkButton(btn_group, text="↻ Refresh", width=65, height=28, command=lambda: fetch_events()).pack(side="left", padx=2)
ctk.CTkButton(btn_group, text="+ Feeds", width=60, height=28, command=open_manage_feeds).pack(side="left", padx=2)
ctk.CTkButton(btn_group, text="?", width=28, height=28, command=open_calendar_tutorial).pack(side="left")

events_scroll = ctk.CTkScrollableFrame(cal_frame, fg_color="transparent", height=140)
events_scroll.pack(fill="both", expand=True, padx=10, pady=5)

def fetch_events():
    for widget in events_scroll.winfo_children():
        widget.destroy()
        
    urls = hub_data.get("ical_urls", [])
    if not urls:
        ctk.CTkLabel(events_scroll, text="No calendar links saved. Click '+ Feeds' to add.", text_color="gray").pack(pady=10)
        return

    loading_lbl = ctk.CTkLabel(events_scroll, text="Fetching schedule...", text_color="gray")
    loading_lbl.pack(pady=10)

    def background_fetch():
        all_upcoming = []
        total_parsed = 0
        err_msg = None
        ssl_context = ssl._create_unverified_context()

        for raw_url in urls:
            url = raw_url.strip().replace("webcal://", "https://")
            if not url:
                continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
                    cal = Calendar.from_ical(response.read())
                    
                today = date.today()
                for event in cal.walk("vevent"):
                    summary = str(event.get("summary"))
                    start = event.get("dtstart")
                    if not start:
                        continue
                    dt = start.dt
                    event_date = dt.date() if isinstance(dt, datetime) else dt
                    total_parsed += 1
                    if event_date >= today:
                        all_upcoming.append((event_date, summary))
            except Exception as e:
                err_msg = str(e)

        def update_ui():
            if not events_scroll.winfo_exists():
                return
            for widget in events_scroll.winfo_children():
                widget.destroy()

            all_upcoming.sort(key=lambda x: x[0])
            
            if not all_upcoming:
                if total_parsed > 0:
                    ctk.CTkLabel(events_scroll, text=f"Connected! (Found {total_parsed} past events)", text_color="gray").pack(pady=2)
                    ctk.CTkLabel(events_scroll, text="No upcoming items scheduled on calendar.", text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=2)
                elif err_msg:
                    ctk.CTkLabel(events_scroll, text="Error connecting to calendar server.", text_color="#ff5555").pack(pady=2)
                    ctk.CTkLabel(events_scroll, text="Check internet or verify URL.", text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=2)
                else:
                    ctk.CTkLabel(events_scroll, text="No events found on saved feed.", text_color="gray").pack(pady=5)
                return

            for evt_date, title in all_upcoming[:15]:
                lbl_text = f"• {evt_date.strftime('%b %d')}: {title}"
                ctk.CTkLabel(events_scroll, text=lbl_text, anchor="w").pack(fill="x", pady=2, padx=5)

        app.after(0, update_ui)

    threading.Thread(target=background_fetch, daemon=True).start()

# --- TIMER WIDGET ---
timer_frame = ctk.CTkFrame(right_col)
timer_frame.pack(fill="both", expand=True)

ctk.CTkLabel(timer_frame, text="Focus Timer", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

timer_label = ctk.CTkLabel(timer_frame, text="25:00", font=ctk.CTkFont(size=30, weight="bold"))
timer_label.pack(pady=2)

timer_running = False
time_left = 1500

def update_timer_display():
    hrs = time_left // 3600
    mins = (time_left % 3600) // 60
    secs = time_left % 60
    if hrs > 0:
        timer_label.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
    else:
        timer_label.configure(text=f"{mins:02d}:{secs:02d}")

def update_timer():
    global time_left, timer_running
    if timer_running and time_left > 0:
        time_left -= 1
        update_timer_display()
        app.after(1000, update_timer)
    elif time_left == 0 and timer_running:
        timer_running = False
        timer_label.configure(text="Time's Up!")
        start_btn.configure(text="Start")

def toggle_timer():
    global timer_running
    if not timer_running:
        if time_left <= 0:
            set_custom_time()
        timer_running = True
        update_timer()
        start_btn.configure(text="Pause")
    else:
        timer_running = False
        start_btn.configure(text="Start")

def set_custom_time():
    global time_left, timer_running
    timer_running = False
    start_btn.configure(text="Start")
    
    h_val = hrs_entry.get().strip()
    m_val = mins_entry.get().strip()
    
    hrs = int(h_val) if h_val.isdigit() else 0
    mins = int(m_val) if m_val.isdigit() else 0
    
    if hrs == 0 and mins == 0:
        mins = 25
        mins_entry.delete(0, "end")
        mins_entry.insert(0, "25")
        
    time_left = (hrs * 3600) + (mins * 60)
    update_timer_display()

timer_input_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
timer_input_frame.pack(pady=3)

ctk.CTkLabel(timer_input_frame, text="Hrs:", font=ctk.CTkFont(size=12)).pack(side="left", padx=2)
hrs_entry = ctk.CTkEntry(timer_input_frame, width=45)
hrs_entry.insert(0, "0")
hrs_entry.pack(side="left", padx=2)

ctk.CTkLabel(timer_input_frame, text="Mins:", font=ctk.CTkFont(size=12)).pack(side="left", padx=2)
mins_entry = ctk.CTkEntry(timer_input_frame, width=45)
mins_entry.insert(0, "25")
mins_entry.pack(side="left", padx=2)

ctk.CTkButton(timer_input_frame, text="Set", width=45, command=set_custom_time).pack(side="left", padx=3)

btn_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
btn_frame.pack(pady=5)

start_btn = ctk.CTkButton(btn_frame, text="Start", width=70, command=toggle_timer)
start_btn.pack(side="left", padx=5)

ctk.CTkButton(btn_frame, text="Reset", width=70, fg_color="transparent", border_width=1, command=set_custom_time).pack(side="left", padx=5)

fetch_events()

app.mainloop()