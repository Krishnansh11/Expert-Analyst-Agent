import io
import queue
import re
import threading
import time
import gradio as gr
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime

from expert_analyst.crew import ExpertAnalyst

class QueueWriter(io.TextIOBase):
    def __init__(self, log_queue: queue.Queue[str]):
        self.log_queue = log_queue

    def write(self, text: str) -> int:
        if text and text.strip():
            self.log_queue.put(text)
        return len(text)

    def flush(self) -> None:
        return None


AGENT_LINE_RE = re.compile(r"Agent:\s*(.+)")
ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def clean_agent_name(raw_name: str) -> str:
    cleaned = ANSI_RE.sub("", raw_name)
    cleaned = cleaned.split("│", 1)[0].strip()
    return cleaned


def format_agent_status(agent_name: str) -> str:
    if not agent_name:
        return "Waiting to start..."
    if agent_name == "Completed":
        return "Completed"
    return f"{agent_name} running"


def run_expert_analyst(topic: str):
    topic = (topic or "").strip()
    if not topic:
        yield "Please enter a topic", ""
        return

    inputs = {
        "topic": topic,
        "current_year": str(datetime.now().year)
    }

    log_queue: queue.Queue[str] = queue.Queue()
    result_holder: dict[str, str] = {}
    current_status = "Starting crew run..."

    def worker() -> None:
        writer = QueueWriter(log_queue)
        try:
            with redirect_stdout(writer), redirect_stderr(writer):
                result = ExpertAnalyst().crew().kickoff(inputs=inputs)
            if hasattr(result, "raw") and result.raw:
                result_holder["output"] = result.raw
            else:
                result_holder["output"] = str(result)
        except Exception as e:
            result_holder["output"] = f"An error occurred: {str(e)}"

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    yield current_status, ""

    while thread.is_alive() or not log_queue.empty():
        while not log_queue.empty():
            chunk = log_queue.get_nowait()
            for line in chunk.splitlines():
                match = AGENT_LINE_RE.search(line.strip())
                if match:
                    current_status = format_agent_status(clean_agent_name(match.group(1)))
        yield current_status, ""
        time.sleep(0.35)

    final_status = format_agent_status("Completed")
    final_output = result_holder.get("output", "No output returned.")
    yield final_status, final_output


def clear_ui():
    return "", ""


CSS = """
.app-container {
  max-width: 860px;
  margin: 0 auto;
}
"""

with gr.Blocks(title="Expert Analyst", css=CSS) as demo:
    with gr.Column(elem_classes=["app-container"]):
        gr.Markdown(
            """
            <h1 style="text-align: center;">Expert Analyst</h1>
            Enter a topic and the crew will generate a report on the given topic.
            """
        )

        topic = gr.Textbox(
            label="Topic",
            placeholder="Enter a topic",
            lines=1,
        )
        with gr.Row():
            run_btn = gr.Button("Run", variant="primary")
            clear_btn = gr.Button("Clear")

        status = gr.Markdown("Waiting to start...")
        output = gr.Markdown(label="Final Crew Output")

        run_btn.click(fn=run_expert_analyst, inputs=topic, outputs=[status, output])
        topic.submit(fn=run_expert_analyst, inputs=topic, outputs=[status, output])
        clear_btn.click(fn=clear_ui, outputs=[status, output])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        theme=gr.Theme.from_hub("NeoPy/shadowthedgehog"),
    )