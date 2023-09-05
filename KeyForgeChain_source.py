import os
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import Label, simpledialog, messagebox, Button
import pyperclip

class PasswordManager:
    def __init__(self):
        self.key = self.load_or_create_key()
        self.credentials = {}
        self.generator_credentials = {}

    def load_or_create_key(self):
        key_file = 'key.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        return key
    
    def encrypt(self, data):
        cipher_suite = Fernet(self.key)
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data

    def decrypt(self, encrypted_data):
        cipher_suite = Fernet(self.key)
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        return decrypted_data.decode()

    def save_credentials(self):
        with open('credentials.bin', 'wb') as f:
            encrypted_credentials = self.encrypt('\0'.join([f"{k}\1{v['username']}\1{v['password']}" for k, v in self.credentials.items()]))
            f.write(encrypted_credentials)

    def load_credentials(self):
        if os.path.exists('credentials.bin'):
            with open('credentials.bin', 'rb') as f:
                encrypted_credentials = f.read()
                decrypted_data = self.decrypt(encrypted_credentials)
                parts = decrypted_data.split('\0')
                self.credentials = {p.split('\1')[0]: {'username': p.split('\1')[1], 'password': p.split('\1')[2]} for p in parts if p}
        else:
            self.credentials = {}

    def add_credentials(self, website, username, password):
        self.credentials[website] = {'username': username, 'password': password}
        self.save_credentials()

    def get_credentials(self, website):
        return self.credentials.get(website, None)

    def list_credentials(self):
        return list(self.credentials.keys())
    
    def add_generated_password(self, website, password):
        if website in self.credentials:
            # If the website already exists, append the new password
            self.credentials[website].setdefault('passwords', []).append(password)
        else:
            # If the website doesn't exist, create a new entry
            self.credentials[website] = {'username': '', 'passwords': [password]}
        self.save_credentials()

def add_credentials_window():
    website = simpledialog.askstring("Add Credentials", "Enter website:")
    if website:
        username = simpledialog.askstring("Add Credentials", f"Enter username for {website}:")
        if username:
            password = simpledialog.askstring("Add Credentials", f"Enter password for {website}:")
            if password:
                password_manager.add_credentials(website, username, password)
                messagebox.showinfo("Success", "Credentials added successfully!")

def get_credentials_window():
    website = simpledialog.askstring("Get Credentials", "Enter website:")
    if website:
        credentials = password_manager.get_credentials(website)
        if credentials:
            username = credentials['username']
            password = credentials['password']
            
            window = tk.Toplevel()
            window.title("Credentials")
            
            username_label = Label(window, text=f"Username: {username}")
            username_label.pack()
            
            username_copy_button = Button(window, text="Copy Username", command=lambda: copy_to_clipboard(username))
            username_copy_button.pack()
            
            password_label = Label(window, text=f"Password: {password}")
            password_label.pack()
            
            password_copy_button = Button(window, text="Copy Password", command=lambda: copy_to_clipboard(password))
            password_copy_button.pack()
            
            delete_button = Button(window, text="Delete Credential", command=lambda: delete_credential(website))
            delete_button.pack()
        else:
            messagebox.showerror("Error", "Credentials not found for the given website.")

def delete_credential(website):
    result = messagebox.askyesno("Delete Credential", f"Do you want to delete the credential for {website}?")
    if result:
        del password_manager.credentials[website]
        password_manager.save_credentials()
        messagebox.showinfo("Deleted", "Credential deleted successfully!")

def list_credentials_window():
    credentials_list = password_manager.list_credentials()
    if credentials_list:
        window = tk.Toplevel()
        window.title("Stored Websites")

        for website in credentials_list:
            credential_button = Button(window, text=website, command=lambda w=website: delete_confirmation(w))
            credential_button.pack()
    else:
        messagebox.showinfo("No Credentials", "No credentials stored yet.")

def delete_confirmation(website):
    result = messagebox.askyesno("Delete Credential", f"Do you want to delete the credential for {website}?")
    if result:
        del password_manager.credentials[website]
        password_manager.save_credentials()
        messagebox.showinfo("Deleted", "Credential deleted successfully!")



def copy_to_clipboard(text):
    pyperclip.copy(text)
    messagebox.showinfo("Copied", "Text copied to clipboard.")

def list_credentials_window():
    credentials_list = password_manager.list_credentials()
    if credentials_list:
        messagebox.showinfo("Stored Websites", "Stored Websites:\n" + "\n".join(credentials_list))
    else:
        messagebox.showinfo("No Credentials", "No credentials stored yet.")

def main():
    root = tk.Tk()
    root.title("KeyForge Chain")
    root.geometry("400x300")  # Set the window size

    add_button = tk.Button(root, text="Add Credentials", command=add_credentials_window)
    get_button = tk.Button(root, text="Get Credentials", command=get_credentials_window)
    list_button = tk.Button(root, text="List Credentials", command=list_credentials_window)
    exit_button = tk.Button(root, text="Exit", command=root.quit)

    add_button.pack(pady=10)
    get_button.pack(pady=10)
    list_button.pack(pady=10)
    exit_button.pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    password_manager = PasswordManager()
    password_manager.load_credentials()
    main()
