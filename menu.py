import socket, sys, tkinter as tk, os, subprocess, threading
from pathlib import Path


VENV_FOLDER_NAME = ".venv"
GAME_NAME = "Adventurer's Path"
HOST_IP = socket.gethostbyname(socket.gethostname())


def startGame(option: str):
    """Options = 'create' or 'connect'"""
    try:
        port_server = int(port_server_entry.get())
        players = int(players_entry.get())
        url = url_entry.get()
        port_connect = int(port_entry.get())
        player_id_number = int(player_id.get())

        root.destroy()

        # Find virtual environment
        base_dir = Path(__file__).resolve().parent
        venv_path = Path(base_dir, VENV_FOLDER_NAME)
        if venv_path.exists():
            if os.name == "nt":
                env_command = f"{venv_path}\\Scripts\\python.exe"
                final_command = f"{venv_path}\\Scripts\\python.exe {base_dir}/game.py"
            else:
                env_command = f"source {venv_path}/bin/activate"
                final_command = f"{env_command}; python {base_dir}/game.py"
        else:
            final_command = f"python {base_dir}/game.py"
        
        final_command = f"{final_command} {option} {HOST_IP} {port_server} {players} {url} {port_connect} {player_id_number}"

        # Run command
        os.system(final_command)

    except Exception as e:
        output.insert("end", f"{str(e)}\n")
        output.pack(side="bottom", fill="both", expand=1)


if __name__ == "__main__":
    # Screen
    root = tk.Tk()
    root.title(GAME_NAME)
    root.resizable(True, True)
    root.configure(bg="white")
    root.iconphoto(False, tk.PhotoImage(file="graphics/sword.png"))
    win = tk.Frame(root, border=20, bg="white")
    win.pack(side="top")

    # Row
    f0 = tk.Frame(win, border=1, bg="white")
    f0.pack(side="top", fill="x", expand=1, pady=10)
    new_online_b = tk.Button(
        f0, text="Create new online game", bg="peru", font=("Arial", 12), relief="groove",
        command=lambda:startGame("create")
    )
    new_online_b.pack(side="left", padx=10)
    url_server_label = tk.Label(f0, text=f"{HOST_IP}", font=("Arial", 12), border=2, bg="white")
    url_server_label.pack(side="left", padx=10)
    port_server_entry = tk.Entry(f0, font=("Arial", 12), border=2, bg="white", width=10, relief="groove", justify="center")
    port_server_entry.pack(side="left", padx=10)
    port_server_entry.insert("end", "5000")
    players_label = tk.Label(f0, text="Online players", font=("Arial", 12), border=2, bg="white")
    players_label.pack(side="left", padx=10)
    players_entry = tk.Entry(f0, font=("Arial", 12), border=2, bg="white", width=5, relief="groove", justify="center")
    players_entry.pack(side="left", padx=10)
    players_entry.insert("end", "2")

    # Row
    f1 = tk.Frame(win, border=1, bg="white")
    f1.pack(side="top", fill="x", expand=1, pady=10)
    connect_b = tk.Button(
        f1, text="Connect to online game", bg="peru", font=("Arial", 12), relief="groove", border=2, padx=5,
        command=lambda:startGame("connect")
    )
    connect_b.pack(side="left", padx=10)
    url_entry = tk.Entry(f1, font=("Arial", 12), border=2, bg="white", relief="groove", justify="center")
    url_entry.pack(side="left", padx=10)
    url_entry.insert("end", HOST_IP)
    port_entry = tk.Entry(f1, font=("Arial", 12), border=2, bg="white", width=10, relief="groove", justify="center")
    port_entry.pack(side="left", padx=10)
    port_entry.insert("end", "5000")

    # Row
    f2 = tk.Frame(win, border=1, bg="white")
    f2.pack(side="top", fill="x", expand=1, pady=10)
    new_game_b = tk.Button(
        f2, text="Start single-player game", bg="peru", font=("Arial", 12), relief="groove",
        command=lambda:startGame("local")
    )
    new_game_b.pack(side="left", padx=10)
    player_id = tk.Entry(f2, font=("Arial", 12), border=2, bg="white", width=5, relief="groove", justify="center")
    player_id.pack(side="right", padx=10)
    player_id.insert("end", "1")
    player_id_label = tk.Label(f2, text="Player Online ID", font=("Arial", 12), border=2, bg="white")
    player_id_label.pack(side="right", padx=10)

    output = tk.Text(root, height=15, width=15)
    root.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()