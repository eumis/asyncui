import json
import tkinter as tk

import aiohttp

import asyncui
from asyncui.loop import asynchronous


class ProjectInfoApp:
    def __init__(self, master):
        self.master = master
        master.title("Project Info")
        master.geometry("700x900")

        input_frame = tk.Frame(master)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        input_label = tk.Label(input_frame, text="GitHub Project (org/repo):")
        input_label.pack(side=tk.LEFT)

        self.project_input = tk.Entry(input_frame)
        self.project_input.insert(0, "eumis/asyncui")
        self.project_input.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.project_input.bind("<Return>", lambda _: self.on_get_info(self.project_input.get()))

        get_info_btn = tk.Button(
            master, text="Get Project Info", command=lambda: self.on_get_info(self.project_input.get())
        )
        get_info_btn.pack(pady=10)

        self.project_info_text = tk.Text(master, height=15, width=50, wrap=tk.WORD)
        self.project_info_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        self.project_info_text.insert(tk.END, "Project info")
        self.project_info_text.config(state=tk.DISABLED)

    @asynchronous
    async def on_get_info(self, project: str):
        self._update_text("Fetching project info...")

        project = self.project_input.get().strip()
        if not project or "/" not in project:
            self.master.after(0, self._update_text, "Please enter a valid GitHub project (org/repo)")
            return

        info = await self.fetch_github_info(project)
        result_text = json.dumps(info, indent=4)
        self._update_text(result_text)

    async def fetch_github_info(self, project: str) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.github.com/repos/{project}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Failed to fetch project info. Status: {response.status}"}
        except Exception as e:
            return {"error": f"Failed to fetch project info. Error: {str(e)}"}

    def _update_text(self, text):
        self.project_info_text.config(state=tk.NORMAL)
        self.project_info_text.delete(1.0, tk.END)
        self.project_info_text.insert(tk.END, text)
        self.project_info_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    ProjectInfoApp(root)

    with asyncui.run_loop():
        root.mainloop()


if __name__ == "__main__":
    main()
