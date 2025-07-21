import json

import aiohttp
import wx

import asyncui
from asyncui.loop import asynchronous


class ProjectInfoFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Project Info", size=wx.Size(700, 900))
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_label = wx.StaticText(panel, label="GitHub Project (org/repo):")
        input_sizer.Add(input_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.project_input = wx.TextCtrl(panel, value="eumis/asyncui", style=wx.TE_PROCESS_ENTER)
        self.project_input.Bind(wx.EVT_TEXT_ENTER, lambda _: self.on_get_info(self.project_input.GetValue()))
        input_sizer.Add(self.project_input, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)

        get_info_btn = wx.Button(panel, label="Get Project Info")
        get_info_btn.Bind(wx.EVT_BUTTON, lambda _: self.on_get_info(self.project_input.GetValue()))
        sizer.Add(get_info_btn, 0, wx.ALL | wx.CENTER, 10)

        self.project_info_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, value="Project info")
        sizer.Add(self.project_info_text, 1, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(sizer)

    @asynchronous
    async def on_get_info(self, project: str):
        wx.CallAfter(self.project_info_text.SetValue, "Fetching project info...")
        project = self.project_input.GetValue().strip()
        if not project or "/" not in project:
            wx.CallAfter(self.project_info_text.SetValue, "Please enter a valid GitHub project (org/repo)")
            return

        info = await self.fetch_github_info(project)
        result_text = json.dumps(info, indent=4)
        wx.CallAfter(self.project_info_text.SetValue, result_text)

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


def main():
    app = wx.App()
    frame = ProjectInfoFrame()
    frame.Show()

    with asyncui.run_loop():
        app.MainLoop()


if __name__ == "__main__":
    main()
