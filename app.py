from tkinter import *
from tkinter import ttk, filedialog, simpledialog
import os, asyncio, threading
from PyPDF2 import PdfReader
from agents import AgentSystem
from dotenv import load_dotenv
from PIL import ImageGrab
from datetime import datetime

load_dotenv()

root = Tk()
root.title("Agentic Whiteboard")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 1000
window_height = 550
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.config(bg="#f2f3f5")
root.resizable(False, False)

# Variables
current_x = current_y = start_x = start_y = 0
color = "black"
active_tool = None
slides = []
current_slide = 0
agent_system = None
chat_memory = []
font_size = 12
document_content = ""  # Store full document content

# Drawing functions
def locate_xy(event):
    global start_x, start_y, current_x, current_y
    start_x, start_y = current_x, current_y = event.x, event.y

def addline(event):
    global current_x, current_y
    if active_tool is None:
        canvas.create_line((current_x, current_y, event.x, event.y), width=int(slider.get()), fill=color, capstyle=ROUND, smooth=True)
        current_x, current_y = event.x, event.y

def add_shape(event):
    global start_x, start_y, active_tool
    if active_tool == "rectangle":
        canvas.create_rectangle(start_x, start_y, event.x, event.y, outline=color, width=int(slider.get()))
    elif active_tool == "oval":
        canvas.create_oval(start_x, start_y, event.x, event.y, outline=color, width=int(slider.get()))
    active_tool = None

def on_canvas_click(event):
    if active_tool == "text":
        text = simpledialog.askstring("Input", "Enter text:")
        if text:
            canvas.create_text(event.x, event.y, text=text, fill=color, font=("Arial", font_size), anchor="nw")
        active_tool = None

def show_color(new_color): 
    global color
    color = new_color

def set_tool(tool):
    global active_tool, color
    active_tool = tool
    if tool == "eraser": 
        color = "white"
        active_tool = None

def new_canvas():
    canvas.delete('all')
    display_pallete()

def display_pallete():
    colors_list = ["black", "red", "blue", "green", "orange", "purple"]
    for i, color_name in enumerate(colors_list):
        id = colors.create_rectangle((10, 10 + i * 30, 30, 30 + i * 30), fill=color_name)
        colors.tag_bind(id, '<Button-1>', lambda x, col=color_name: show_color(col))

def increase_font():
    global font_size
    font_size = min(font_size + 2, 24)
    font_label.config(text=f"Font: {font_size}")

def decrease_font():
    global font_size
    font_size = max(font_size - 2, 8)
    font_label.config(text=f"Font: {font_size}")

# Document functions
def insert_document():
    global slides, current_slide, document_content
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt")])
    if not file_path: return
    
    slides, current_slide = [], 0
    document_content = ""
    
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        slides = [page.extract_text() for page in reader.pages]
        document_content = "\n\n".join(slides)  # Store full content
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            content = file.read()
            slides = content.split('\n\n')
            document_content = content
    
    if slides: 
        display_slide()
        # Add document to chat memory for AI access
        chat_memory.append({"role": "system", "content": f"Document loaded: {document_content[:1000]}..."})

def display_slide():
    if 0 <= current_slide < len(slides):
        canvas.delete("slide_content")
        canvas.create_text(50, 50, text=slides[current_slide][:800], anchor="nw", width=700, tags="slide_content")

def next_slide():
    global current_slide
    if current_slide < len(slides) - 1:
        current_slide += 1
        display_slide()

def prev_slide():
    global current_slide
    if current_slide > 0:
        current_slide -= 1
        display_slide()

def take_screenshot():
    try:
        x, y = canvas.winfo_rootx(), canvas.winfo_rooty()
        width, height = canvas.winfo_width(), canvas.winfo_height()
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        filename = f"whiteboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(filename)
        status_label.config(text=f"Saved: {filename}", fg="blue")
        root.after(3000, lambda: status_label.config(text="🟢 AI Ready" if agent_system else "🔴 AI Offline"))
    except Exception as e:
        print(f"Screenshot error: {e}")

# AI functions
async def initialize_ai():
    global agent_system
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            status_label.config(text="❌ No API Key", fg="red")
            return False
        agent_system = AgentSystem(canvas, api_key)
        status_label.config(text="🟢 AI Ready", fg="green")
        return True
    except Exception as e:
        status_label.config(text="❌ AI Error", fg="red")
        return False

async def handle_chat():
    global chat_memory
    if not agent_system:
        chat_output.config(state='normal')
        chat_output.insert(END, "Please initialize AI first.\n")
        chat_output.config(state='disabled')
        return
    
    query = chat_entry.get().strip()
    if query:
        chat_entry.delete(0, END)
        chat_memory.append({"role": "user", "content": query})
        
        chat_output.config(state='normal')
        chat_output.insert(END, f"You: {query}\n Thinking...\n")
        chat_output.config(state='disabled')
        chat_output.see(END)
        
        canvas_context = {
            "canvas_items": len(canvas.find_all()),
            "memory": chat_memory[-5:],
            "document_content": document_content,
            "current_slide": current_slide if slides else None
        }
        
        response = await agent_system.process_query(query, canvas_context)
        chat_memory.append({"role": "assistant", "content": response})
        
        chat_output.config(state='normal')
        chat_output.delete("end-2l", "end-1l")
        chat_output.insert(END, f"🤖 {response}\n\n")
        chat_output.config(state='disabled')
        chat_output.see(END)
        
        if len(chat_memory) > 20:
            chat_memory = chat_memory[-10:]

def clear_chat():
    global chat_memory
    chat_memory = []
    chat_output.config(state='normal')
    chat_output.delete(1.0, END)
    chat_output.config(state='disabled')

def run_async(coro):
    def run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
        finally:
            try:
                loop.close()
            except:
                pass
    threading.Thread(target=run, daemon=True).start()

def toggle_chat():
    if chat_frame.winfo_ismapped():
        chat_frame.place_forget()
    else:
        chat_frame.place(x=600, y=50, width=350, height=450)

# UI Setup
Label(root, text="Colors", bg='#f2f3f5').place(x=10, y=20)
colors = Canvas(root, bg="#fff", width=37, height=180, bd=0)
colors.place(x=30, y=60)
display_pallete()

canvas = Canvas(root, width=750, height=400, background="white", cursor="hand2")
canvas.place(x=100, y=10)
canvas.bind('<Button-1>', locate_xy)
canvas.bind('<B1-Motion>', addline)
canvas.bind('<ButtonRelease-1>', add_shape)
canvas.bind('<Button-1>', on_canvas_click, add='+')

current_value = DoubleVar()
slider = ttk.Scale(root, from_=1, to=10, orient="horizontal", variable=current_value)
slider.place(x=30, y=530)



# Buttons
Button(root, text="Eraser", bg="#f2f3f5", command=lambda: set_tool("eraser")).place(x=30, y=400)
Button(root, text="Text", command=lambda: set_tool("text"), font=("Arial", 12, "bold"), bg="#f2f3f5").place(x=30, y=350)
Button(root, text="Clear", command=new_canvas, font=("Arial", 10), bg="#f44336", fg="white").place(x=30, y=300)
Button(root, text="◀", command=prev_slide, font=("Arial", 12), bg="#f2f3f5").place(x=30, y=480)
Button(root, text="▶", command=next_slide, font=("Arial", 12), bg="#f2f3f5").place(x=60, y=480)
Button(root, text="Rectangle Shape", bg="#f2f3f5", command=lambda: set_tool("rectangle")).place(x=150, y=520)
Button(root, text="Circle Shape", bg="#f2f3f5", command=lambda: set_tool("oval")).place(x=260, y=520)

Button(root, text="Doc", command=insert_document, bg="#f2f3f5").place(x=800, y=520)
Button(root, text="Save Screenshot", command=take_screenshot, bg="#4CAF50", fg="white").place(x=850, y=520)
Button(root, text="Agentic Chatbot", command=toggle_chat, bg="#4CAF50", fg="white").place(x=600, y=520)

# Chat Frame
chat_frame = Frame(root, bg="white", bd=2, relief="solid")
header_frame = Frame(chat_frame, bg="#4CAF50", height=40)
header_frame.pack(fill=X)
header_frame.pack_propagate(False)

Label(header_frame, text="AI Assistant", bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side=LEFT, padx=10, pady=10)
Button(header_frame, text="−", command=lambda: chat_frame.place_forget(), bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), bd=0).pack(side=RIGHT, padx=5, pady=5)

status_label = Label(chat_frame, text="🔴 AI Offline", bg="white", font=("Arial", 10))
status_label.pack(pady=5)

Button(chat_frame, text="Initialize AI", command=lambda: run_async(initialize_ai()), bg="#2196F3", fg="white").pack(pady=5)

# Input at top
input_frame = Frame(chat_frame, bg="white")
input_frame.pack(fill=X, padx=10, pady=5)

chat_entry = Entry(input_frame, font=("Arial", 10))
chat_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
chat_entry.bind('<Return>', lambda e: run_async(handle_chat()))

Button(input_frame, text="Send", command=lambda: run_async(handle_chat()), bg="#FF9800", fg="white").pack(side=RIGHT)
Button(input_frame, text="Clear", command=clear_chat, bg="#f44336", fg="white").pack(side=RIGHT, padx=(0, 5))

chat_output = Text(chat_frame, height=18, width=42, font=("Arial", 9), state='disabled', wrap=WORD)
chat_output.pack(padx=10, pady=5)

Label(chat_frame, text="Ask about documents, drawings, or get help", bg="white", font=("Arial", 8), fg="gray").pack(pady=2)

root.mainloop()