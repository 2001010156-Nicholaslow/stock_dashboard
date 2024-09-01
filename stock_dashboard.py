import yfinance as yf
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

REFRESH_INTERVAL = 300000  # 5 minutes

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='5d')
        
        if data.empty or len(data) < 2:
            raise ValueError("Insufficient data to calculate change.")
        
        price = data['Close'].iloc[-1]  # Most recent close price
        prev_close = data['Close'].iloc[-2]  # Previous day's close price
        change = ((price - prev_close) / prev_close) * 100
        
        return round(price, 2), round(change, 2)
    except Exception as e:
        messagebox.showerror("Data Fetch Error", f"Error fetching data for {ticker}: {e}")
        return None, None


class StockDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Dashboard")
        self.root.geometry("250x400")
        self.root.configure(bg="#f7f7f7")

        self.stocks = self.load_stocks()
        self.create_ui()
        self.update_stocks()

        self.auto_refresh()

    def create_ui(self):
        self.control_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.control_frame.pack(pady=10)

        #Stock button
        self.add_button = tk.Button(self.control_frame, text="Add Stock", command=self.add_stock, font=("Arial", 12), bg="#4CAF50", fg="white")
        self.add_button.pack(side=tk.LEFT, padx=(0, 10))

        #Edit button
        self.edit_button = tk.Button(self.control_frame, text="Edit", command=self.edit_stock, font=("Arial", 12), bg="#FF5722", fg="white")
        self.edit_button.pack(side=tk.LEFT)

        self.list_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def display_stock(self, company, ticker, price, change):
        arrow_symbol = "▲ " if change > 0 else "▼"
        change_color = "green" if change > 0 else "red"

        stock_frame = tk.Frame(self.list_frame, bg="#ffffff")
        stock_frame.pack(fill=tk.X, pady=2)
        
        ticker_label = tk.Label(stock_frame, text=ticker, bg="#ffffff", fg="#0000FF", font=("Arial", 10, "bold"))
        ticker_label.grid(row=0, column=0, padx=5, sticky="w")

        # Price
        price_label = tk.Label(stock_frame, text=f"${price:.2f}", bg="#ffffff", fg="black", font=("Arial", 10))
        price_label.grid(row=0, column=1, padx=5, sticky="e")

        # Percentage and absolute change
        change_label = tk.Label(stock_frame, text=f"{arrow_symbol} {change:.2f}%", bg="#ffffff", fg=change_color, font=("Arial", 10, "bold"))
        change_label.grid(row=0, column=2, padx=5, sticky="e")
        
        # Adjust column weights for better alignment
        stock_frame.grid_columnconfigure(1, weight=1)



    def load_stocks(self):
        if os.path.exists("stocks.json"):
            with open("stocks.json", "r") as f:
                return json.load(f)
        return []

    def save_stocks(self):
        with open("stocks.json", "w") as f:
            json.dump(self.stocks, f)

    def update_stocks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for index, stock in enumerate(self.stocks):
            price, change = get_stock_data(stock)
            if price is not None:
                self.display_stock(index, stock, price, change)

    def auto_refresh(self):
        self.update_stocks()
        self.root.after(REFRESH_INTERVAL, self.auto_refresh)

    def add_stock(self):
        ticker = simpledialog.askstring("Add Stock", "Enter stock ticker:").upper().strip()
        
        if not ticker:
            messagebox.showerror("Invalid Input", "Stock ticker cannot be empty.")
            return
        
        if not ticker.isalnum():
            messagebox.showerror("Invalid Input", "Stock ticker should only contain alphanumeric characters.")
            return
        
        if ticker and ticker not in self.stocks:
            price, change = get_stock_data(ticker)
            if price is not None:
                self.stocks.append(ticker)
                self.update_stocks()
                self.save_stocks()
            else:
                messagebox.showerror("Invalid Ticker", f"'{ticker}' is invalid.")
        elif ticker in self.stocks:
            messagebox.showinfo("Stock Exists", f"'{ticker}' is already in your dashboard.")

    def edit_stock(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Stocks")
        edit_window.geometry("300x400")
        edit_window.configure(bg="#f7f7f7")

        self.update_stocks()
        self.root.after(REFRESH_INTERVAL, self.auto_refresh)

        for index, stock in enumerate(self.stocks):
            stock_frame = tk.Frame(edit_window, bg="#ffffff", pady=5, padx=10)
            stock_frame.pack(fill=tk.X, pady=2)

            #Move Up button
            up_button = tk.Button(stock_frame, text="↑", command=lambda i=index: self.move_stock_up(i, edit_window), 
                                  font=("Arial", 10), bg="#3E3E3E", fg="white", width=2)
            up_button.pack(side=tk.LEFT)

            #Move Down button
            down_button = tk.Button(stock_frame, text="↓", command=lambda i=index: self.move_stock_down(i, edit_window), 
                                    font=("Arial", 10), bg="#3E3E3E", fg="white", width=2)
            down_button.pack(side=tk.LEFT)

            ticker_label = tk.Label(stock_frame, text=stock, bg="#ffffff", fg="black", font=("Arial", 12))
            ticker_label.pack(side=tk.LEFT, padx=10)

            delete_button = tk.Button(stock_frame, text="Delete", command=lambda i=index: self.delete_stock(i, edit_window), 
                                      font=("Arial", 10), bg="#FF5722", fg="white")
            delete_button.pack(side=tk.RIGHT)

    def delete_stock(self, index, window):
        del self.stocks[index]
        self.update_stocks()
        self.save_stocks()
        window.destroy()
        self.edit_stock()

    def move_stock_up(self, index, window):
        if index > 0:
            self.stocks[index], self.stocks[index - 1] = self.stocks[index - 1], self.stocks[index]
            self.update_stocks()
            self.save_stocks()
            window.destroy()
            self.edit_stock()

    def move_stock_down(self, index, window):
        if index < len(self.stocks) - 1:
            self.stocks[index], self.stocks[index + 1] = self.stocks[index + 1], self.stocks[index]
            self.update_stocks()
            self.save_stocks()
            window.destroy()
            self.edit_stock()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.save_stocks()
            self.root.destroy()

root = tk.Tk()
dashboard = StockDashboard(root)
root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
root.mainloop()
