import os
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading

# Category mapping
CATEGORY_MAP = {
    "Music": ["spotify", "deezer", "soundcloud", "tidal", "music"],
    "Social": ["facebook", "instagram", "twitter", "snapchat", "tiktok", "linkedin", "pinterest"],
    "Video": ["youtube", "netflix", "hulu", "primevideo", "disney", "crunchyroll", "funimation"],
    "Gaming": ["steam", "epicgames", "origin", "battlenet", "riotgames", "xbox", "playstation", "nintendo"],
    "Email": ["gmail", "yahoo", "outlook", "hotmail", "aol", "protonmail", "mail.com"],
    "Shopping": ["amazon", "ebay", "aliexpress", "etsy", "shopify", "lazada"],
    "Finance": ["paypal", "revolut", "cashapp", "venmo", "bank", "crypto", "coinbase", "binance"],
    "NSFW": ["pornhub", "onlyfans", "fansly", "xvideos", "xhamster", "brazzers", "chaturbate"],
    "Education": ["edu", "khanacademy", "coursera", "udemy", "edx"],
    "Other": []
}

DIST_DIR = os.path.join("dist", "Categories")


def extract_mail_pass(line):
    """Extract email and password if in MAIL:PASS format"""
    match = re.search(r'([\w\.-]+@[\w\.-]+\.\w+):([^\s@:\[\]]+)', line)
    return match.groups() if match else None


def determine_category(line):
    """Determine category based on keywords in the full line"""
    lower_line = line.lower()
    for category, keywords in CATEGORY_MAP.items():
        for keyword in keywords:
            if keyword in lower_line:
                return category
    return "Other"


def process_file(file_path, progress_callback=None):
    os.makedirs(DIST_DIR, exist_ok=True)
    all_mail_pass_set = set()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    total_lines = len(lines)

    for index, line in enumerate(lines):
        line = line.strip()
        result = extract_mail_pass(line)
        if result:
            email, password = result
            mail_pass = f"{email}:{password}"
            all_mail_pass_set.add(mail_pass)

            category = determine_category(line)
            category_path = os.path.join(DIST_DIR, category)
            os.makedirs(category_path, exist_ok=True)

            file_name = f"{category.lower()}.txt"
            output_path = os.path.join(category_path, file_name)

            with open(output_path, 'a', encoding='utf-8') as cat_file:
                cat_file.write(mail_pass + "\n")

        # Update progress bar
        if progress_callback:
            progress_callback(index + 1, total_lines)

    # Write the global all_mail_pass.txt
    with open(os.path.join("dist", "all_mail_pass.txt"), 'w', encoding='utf-8') as all_out:
        all_out.write("\n".join(sorted(all_mail_pass_set)))


# GUI
class MailPassSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mail:Pass Categorizer")
        self.geometry("500x320")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # UI components
        self.label = ctk.CTkLabel(self, text="Select a URL:MAIL:PASS file", font=("Arial", 16))
        self.label.pack(pady=20)

        self.browse_button = ctk.CTkButton(self, text="Browse File", command=self.browse_file)
        self.browse_button.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.status_label.pack(pady=20)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.status_label.configure(text="Processing...")
            self.progress_bar.set(0)
            threading.Thread(target=self.start_processing, args=(file_path,), daemon=True).start()

    def update_progress(self, current, total):
        if total > 0:
            percent = current / total
            self.progress_bar.set(percent)

    def start_processing(self, file_path):
        try:
            process_file(file_path, self.update_progress)
            self.status_label.configure(text="✅ Completed! Check the 'dist' folder.")
            messagebox.showinfo("Success", "Processing complete!")
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {e}")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = MailPassSorterApp()
    app.mainloop()
