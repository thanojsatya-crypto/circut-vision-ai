from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from PIL import Image
import os
import time
import requests
import json
import base64
from io import BytesIO

app = FastAPI(title="CircuitVision AI Backend")

# Enable CORS to allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_IMAGE_ATTEMPTS = 3  

# Master Keyword Dictionary (41 Divisions: Theory, Core Subjects, Labs & Records)
RULE_TRIGGERS = {
    1: {
        "name": "Passive Circuits & Network Analysis",
        "keywords": [
            "rc", "rl", "lc", "rlc", "low pass", "high pass", "divider",
            "wheatstone", "resistor", "capacitor", "inductor", "impedance",
            "reactance", "passive", "filter", "snubber", "time constant",
            "tau", "cutoff frequency", "fc", "damping factor",
            "resonant frequency", "two-port network", "z-parameters",
            "y-parameters", "h-parameters", "abcd parameters",
            "transmission parameters", "supermesh", "supernode",
            "transient response", "initial conditions"
        ]
    },
    2: {
        "name": "Diode Circuits",
        "keywords": [
            "rectifier", "clipper", "clamper", "multiplier", "zener",
            "schottky", "peak detector", "diode", "pn junction",
            "forward bias", "reverse bias", "avalanche", "freewheeling",
            "bridge", "voltage drop", "vd", "ripple factor", "form factor",
            "peak inverse voltage", "piv"
        ]
    },
    3: {
        "name": "Transistor Circuits (BJT/FET)",
        "keywords": [
            "common emitter", "darlington", "mosfet", "jfet",
            "current mirror", "cascode", "bjt", "npn", "pnp", "n-channel",
            "p-channel", "igbt", "transistor", "biasing", "base",
            "collector", "emitter", "gate", "drain", "source", "beta",
            "hfe", "gm", "transconductance", "vgs", "pinch-off",
            "small-signal model", "early voltage", "ro", "rpi",
            "miller effect", "miller capacitance", "unity-gain frequency",
            "ft"
        ]
    },
    4: {
        "name": "Op-Amp Circuits",
        "keywords": [
            "op-amp", "inverting", "non-inverting", "comparator",
            "integrator", "schmitt trigger", "operational amplifier",
            "lm741", "summing", "difference", "buffer", "cmrr",
            "slew rate", "av", "voltage gain", "rf/rin",
            "input offset voltage", "bias current", "psrr",
            "gain-bandwidth product", "gbw"
        ]
    },
    5: {
        "name": "Power Supplies",
        "keywords": [
            "buck", "boost", "sepic", "flyback", "ldo", "7805", "lm317",
            "smps", "linear regulator", "switching regulator", "dc-dc",
            "converter", "power supply", "ripple", "efficiency", "vout",
            "duty cycle", "pwm", "continuous conduction mode", "ccm", "dcm"
        ]
    },
    6: {
        "name": "Power Amplifiers",
        "keywords": [
            "class a", "class b", "class ab", "class d", "lm386",
            "tda2030", "push-pull", "audio amplifier", "power gain",
            "crossover distortion", "efficiency equation",
            "total harmonic distortion", "thd", "load line",
            "maximum power dissipation", "watts", "speaker"
        ]
    },
    7: {
        "name": "Basic Timers & Clocks",
        "keywords": [
            "555", "astable", "monostable", "timer", "rtc", "clock pulse",
            "duty cycle", "delay", "556", "trigger", "threshold",
            "frequency formula", "1.44"
        ]
    },
    8: {
        "name": "Digital Logic & Sequential",
        "keywords": [
            "and gate", "nand", "xor", "flip-flop", "latch", "counter",
            "shift register", "boolean", "logic gate", "or gate",
            "not gate", "nor", "xnor", "combinational", "sequential",
            "truth table", "k-map", "demorgan", "state machine", "fsm",
            "mealy", "moore", "fan-out", "fan-in", "noise margin"
        ]
    },
    9: {
        "name": "Memory Architectures",
        "keywords": [
            "sram", "dram", "eeprom", "flash", "memory mapping", "storage",
            "rom", "prom", "volatile", "non-volatile", "address bus",
            "data bus", "refresh rate", "access time"
        ]
    },
    10: {
        "name": "Active Filters",
        "keywords": [
            "butterworth", "chebyshev", "bessel", "notch", "state variable",
            "sallen-key", "active low pass", "active high pass", "bandpass",
            "bandstop", "roll-off", "q factor", "quality factor",
            "damping ratio", "poles", "zeros", "transfer function"
        ]
    },
    11: {
        "name": "Standard Sensors",
        "keywords": [
            "ldr", "thermistor", "lm35", "hall sensor", "pir", "ultrasonic",
            "photodiode", "temperature sensor", "motion sensor", "humidity",
            "sensor", "calibration curve", "sensitivity equation"
        ]
    },
    12: {
        "name": "Motor Control",
        "keywords": [
            "h-bridge", "l298n", "stepper", "servo", "bldc", "pwm speed",
            "dc motor", "motor driver", "l293d", "a4988", "esc",
            "back emf", "torque equation", "rpm calculation"
        ]
    },
    13: {
        "name": "Serial Communication",
        "keywords": [
            "rs232", "rs485", "uart", "spi", "i2c", "can bus", "baud rate",
            "rx", "tx", "mosi", "miso", "sck", "sda", "scl", "full-duplex",
            "half-duplex", "bit rate", "parity"
        ]
    },
    14: {
        "name": "Audio & RF Front-End",
        "keywords": [
            "preamp", "tone control", "crossover", "rf amplifier", "mixer",
            "antenna", "microphone", "speaker", "impedance matching", "lna",
            "vswr", "return loss", "decibel", "dbm", "s-parameters",
            "reflection coefficient", "maxwell's equations",
            "characteristic impedance", "smith chart"
        ]
    },
    15: {
        "name": "LED & Lighting",
        "keywords": [
            "led driver", "charlieplexing", "pwm dimmer", "rgb controller",
            "ws2812b", "neopixel", "constant current", "multiplexing",
            "illumination", "current limiting resistor formula"
        ]
    },
    16: {
        "name": "Automation & Switching",
        "keywords": [
            "night light", "motion light", "line follower", "relay",
            "contactor", "solid state", "ssr", "limit switch", "optocoupler",
            "isolation voltage"
        ]
    },
    17: {
        "name": "Protection Circuits",
        "keywords": [
            "fuse", "crowbar", "tvs diode", "reverse polarity", "esd",
            "mov", "varistor", "overvoltage", "overcurrent",
            "surge protection", "ptc", "clamping voltage", "joule rating"
        ]
    },
    18: {
        "name": "Advanced Data Converters",
        "keywords": [
            "adc", "dac", "sigma-delta", "successive approximation", "sar",
            "flash adc", "quantization", "sampling rate", "nyquist",
            "resolution", "aliasing", "snr", "enob", "step size formula",
            "dnl", "inl", "quantization noise power"
        ]
    },
    19: {
        "name": "Communication & Modulation",
        "keywords": [
            "modulation", "demodulation", "am", "fm", "fsk", "psk", "qam",
            "transceiver", "multiplexer", "rfid", "encoding", "bluetooth",
            "wifi", "zigbee", "lora", "modulation index",
            "bandwidth formula", "shannon capacity", "friis transmission",
            "noise figure", "bit error rate", "ber", "carson's rule",
            "eb/n0"
        ]
    },
    20: {
        "name": "VLSI & Digital Design",
        "keywords": [
            "vlsi", "cmos", "verilog", "fpga", "logic synthesis",
            "digital testing", "layout", "routing", "wafer", "vhdl", "asic",
            "finfet", "propagation delay", "dynamic power formula",
            "lambda rules", "clock domain crossing", "cdc", "setup time",
            "hold time", "metastability", "critical path delay", "skew",
            "slack"
        ]
    },
    21: {
        "name": "Signals & Systems",
        "keywords": [
            "dsp", "signal conditioning", "fourier", "laplace",
            "z-transform", "convolution", "discrete time", "continuous time",
            "fft", "transfer function", "nyquist theorem", "roc",
            "region of convergence", "parseval's theorem",
            "impulse response", "autocorrelation", "cross-correlation",
            "power spectral density", "psd", "energy signal", "power signal",
            "dirichlet conditions", "hilbert transform"
        ]
    },
    22: {
        "name": "Microsensors & Actuation",
        "keywords": [
            "mems", "nanosensor", "strain gauge", "actuator", "interfacing",
            "piezoelectric", "transducer", "accelerometer", "gyroscope",
            "load cell", "gauge factor", "piezoelectric coefficient"
        ]
    },
    23: {
        "name": "Control Systems",
        "keywords": [
            "pid", "closed-loop", "open-loop", "feedback", "damping",
            "stability", "root locus", "bode plot", "nyquist plot",
            "proportional", "integral", "derivative", "steady state error",
            "gain margin", "phase margin", "state space", "routh-hurwitz",
            "break-away point", "state transition matrix",
            "controllability", "observability", "peak overshoot",
            "settling time", "error constants", "kp", "kv", "ka"
        ]
    },
    24: {
        "name": "Advanced Oscillators & PLLs",
        "keywords": [
            "pll", "vco", "phase-locked", "synthesizer",
            "voltage controlled", "wien bridge", "colpitts",
            "crystal oscillator", "hartley", "pierce", "phase noise",
            "jitter", "oscillation frequency formula", "loop filter design",
            "barkhausen criterion"
        ]
    },
    25: {
        "name": "Edge AI, Quantum & Compute Hardware",
        "keywords": [
            "edge ai", "accelerator", "anomaly detection", "tensor",
            "parallel compute", "neural network hardware", "tpu", "npu",
            "mac unit", "inference", "quantization error",
            "flops computation", "quantum machine learning", "qml",
            "quantum support vector machine",
            "variational quantum classifier", "qubit", "entanglement",
            "superposition", "hilbert space", "kernel trick",
            "gradient descent", "loss function"
        ]
    },
    26: {
        "name": "Core Engineering Mathematics",
        "keywords": [
            "formula", "calculate", "equation", "math", "derive", "value",
            "kvl", "kcl", "ohm's law", "kirchhoff", "thevenin", "norton",
            "superposition", "power dissipation", "p=vi", "v=ir",
            "differential equation", "laplace inverse", "partial fraction",
            "matrix determinant", "eigenvalue", "eigenvector",
            "taylor series", "maclaurin series", "design", "compute",
            "solve"
        ]
    },
    27: {
        "name": "Basic Electronic Components",
        "keywords": [
            "resistor", "capacitor", "inductor", "potentiometer",
            "transformer", "fuse", "switch", "relay", "connector",
            "breadboard", "component"
        ]
    },
    28: {
        "name": "Analog Electronics Lab",
        "keywords": [
            "ce amplifier", "cb amplifier", "cc amplifier", "rc coupled",
            "multistage", "differential amplifier", "analog lab",
            "experiment", "lab manual"
        ]
    },
    29: {
        "name": "Digital Electronics Lab",
        "keywords": [
            "adder", "subtractor", "encoder", "decoder", "mux", "demux",
            "multiplexer", "comparator", "counters", "digital lab"
        ]
    },
    30: {
        "name": "Electronic Measurements & Instrumentation",
        "keywords": [
            "cro", "dso", "multimeter", "function generator",
            "frequency counter", "oscilloscope", "probe", "measure",
            "calibration"
        ]
    },
    31: {
        "name": "Embedded Systems Lab",
        "keywords": [
            "arduino", "esp32", "stm32", "atmega", "pic",
            "microcontroller", "raspberry pi", "msp430", "embedded",
            "board", "node mcu"
        ]
    },
    32: {
        "name": "PCB Design",
        "keywords": [
            "pcb", "routing", "grounding", "copper width", "vias",
            "footprint", "gerber", "trace", "soldering", "layout"
        ]
    },
    33: {
        "name": "Troubleshooting & Fault Diagnosis",
        "keywords": [
            "not working", "no output", "voltage drop", "overheating",
            "noise", "distortion", "unstable", "oscillation",
            "short circuit", "fault", "burnt", "error", "why", "fluctuating"
        ]
    },
    34: {
        "name": "Mini Project Templates",
        "keywords": [
            "smart irrigation", "home automation", "attendance system",
            "weather station", "line follower", "iot monitoring",
            "mini project", "major project", "rfid", "toll gate",
            "prototype"
        ]
    },
    35: {
        "name": "Viva & Interview Preparation",
        "keywords": [
            "viva", "interview", "frequently asked", "oral examination",
            "questions", "explain why", "placement", "gate prep", "quiz"
        ]
    },
    36: {
        "name": "Electrical Machines",
        "keywords": [
            "dc motor", "dc generator", "transformer", "induction motor",
            "synchronous motor", "torque", "efficiency", "slip",
            "emf equation", "rotor", "stator"
        ]
    },
    37: {
        "name": "Power Systems",
        "keywords": [
            "transmission line", "distribution", "load flow",
            "fault analysis", "power factor", "compensation", "substation",
            "switchgear", "grid"
        ]
    },
    38: {
        "name": "Microprocessors & Microcontrollers",
        "keywords": [
            "8085", "8086", "8051", "instruction set", "addressing modes",
            "assembly language", "opcode", "operand", "alu", "registers"
        ]
    },
    39: {
        "name": "Communication Systems Laboratory",
        "keywords": [
            "am", "fm", "pcm", "ask", "fsk", "psk", "qpsk",
            "modulation index", "demodulation", "superheterodyne",
            "carrier wave"
        ]
    },
    40: {
        "name": "Electronic Devices & Semiconductor Physics",
        "keywords": [
            "pn junction", "carrier transport", "diffusion", "drift",
            "energy band", "breakdown mechanism", "fermi level",
            "depletion region", "bandgap"
        ]
    },
    41: {
        "name": "Lab Record Assistant",
        "keywords": [
            "record observation", "expected reading", "lab calculation",
            "error calculation", "precautions", "result statement",
            "tabular column", "observation table", "experiment result"
        ]
    }
}

SEGMENTS = {
    "Circuit Theory & Semiconductor Physics": [1, 2, 3, 4, 10, 21, 23, 26, 40],
    "Hardware Design & Synthesis": [5, 6, 7, 14, 15, 18, 19, 20, 24, 32],
    "Embedded, Digital & Microprocessors": [8, 9, 11, 12, 13, 16, 22, 25, 31, 38],
    "Power & Electrical Machines": [36, 37],
    "Lab Execution, Records & Troubleshooting": [17, 27, 28, 29, 30, 33, 34, 35, 39, 41],
    "Standard Web-Based Project Circuits": [31, 34, 27, 11, 12],
    "New Unknown Circuit Synthesis (Novel)": list(range(1, 42))
}


def dynamic_rule_router(user_prompt, selected_segment):
    prompt_lower = user_prompt.lower()
    triggered_rules = []
    compiled_rules_text = ""
    
    # Path relative to backend/main.py
    base_path = os.path.join(os.path.dirname(__file__), "ai_database", "isolated_rules")
    
    # 1. Force load selected segment
    if selected_segment != "Auto-Detect (Keyword Only)":
        for rule_idx in SEGMENTS[selected_segment]:
            triggered_rules.append(rule_idx)
            try:
                with open(os.path.join(base_path, f"rule_{rule_idx}.txt"), "r", encoding="utf-8") as file:
                    compiled_rules_text += f"\n=== DIVISION {rule_idx} ===\n{file.read()}\n"
            except FileNotFoundError:
                pass

    # 2. Universal Math/Design inclusion (Rule 26) - skip if doing Full Synthesis since it's already included
    if 26 not in triggered_rules and any(k in prompt_lower for k in RULE_TRIGGERS[26]["keywords"]):
        triggered_rules.append(26)
        try:
            with open(os.path.join(base_path, "rule_26.txt"), "r", encoding="utf-8") as file:
                compiled_rules_text += f"\n=== DIVISION 26 ===\n{file.read()}\n"
        except FileNotFoundError:
            pass

    # 3. Keyword scanning for remaining rules
    if selected_segment != "New Unknown Circuit Synthesis (Novel)":
        for rule_idx, data in RULE_TRIGGERS.items():
            if rule_idx in triggered_rules:
                continue
            if any(keyword in prompt_lower for keyword in data["keywords"]):
                triggered_rules.append(rule_idx)
                try:
                    with open(os.path.join(base_path, f"rule_{rule_idx}.txt"), "r", encoding="utf-8") as file:
                        compiled_rules_text += f"\n=== DIVISION {rule_idx} ===\n{file.read()}\n"
                except FileNotFoundError:
                    pass
                
    if not triggered_rules:
        return "No specific lab or theoretical rules triggered. Executing generic engineering principles.", []
        
    return compiled_rules_text, triggered_rules


@app.get("/metadata")
def get_metadata():
    """Returns lists of rules and segments for frontend routing and dynamic UI rendering."""
    return {
        "rule_triggers": RULE_TRIGGERS,
        "segments": SEGMENTS
    }


@app.post("/synthesize")
def synthesize(
    user_goal: str = Form(...),
    selected_segment: str = Form(...),
    api_provider: str = Form(...),
    user_api_key: str = Form(...),
    selected_model: str = Form(...),
    image_file: UploadFile = File(None)
):
    """Processes the prompt using the selected segment RAG context and submits to the appropriate LLM."""
    if not user_goal.strip():
        raise HTTPException(status_code=400, detail="Input parameters or query cannot be empty.")
        
    injected_rules, triggered_ids = dynamic_rule_router(user_goal, selected_segment)
    
    # 1. Detect provider based on key prefix
    api_key_stripped = user_api_key.strip()
    detected_provider = api_provider
    
    if api_key_stripped.startswith("sk-or-"):
        detected_provider = "OpenRouter"
    elif api_key_stripped.startswith("sk-proj-") or (api_key_stripped.startswith("sk-") and not api_key_stripped.startswith("sk-or-")):
        detected_provider = "OpenAI"
    elif api_key_stripped.startswith("AIzaSy"):
        detected_provider = "Google Gemini"
        
    is_openrouter = (detected_provider == "OpenRouter")
    is_openai = (detected_provider == "OpenAI")
    
    # 2. Model mapping to match detected provider
    actual_model = selected_model
    if detected_provider == "Google Gemini":
        if "gemini-2.0-flash" in selected_model:
            actual_model = "gemini-2.0-flash"
        else:
            actual_model = "gemini-2.5-flash"
    elif detected_provider == "OpenRouter":
        if "gemini-2.5-flash:free" in selected_model:
            actual_model = "google/gemini-2.5-flash:free"
        elif "llama-3.1-8b" in selected_model:
            actual_model = "meta-llama/llama-3.1-8b-instruct:free"
        elif "qwen-2.5-coder" in selected_model:
            actual_model = "qwen/qwen-2.5-coder-32b-instruct:free"
        elif "gemini-2.5-flash" in selected_model:
            actual_model = "google/gemini-2.5-flash"
        elif "gemini-2.0-flash" in selected_model:
            actual_model = "google/gemini-2.0-flash"
        elif "gpt-4o-mini" in selected_model:
            actual_model = "openai/gpt-4o-mini"
        elif "openrouter/auto" in selected_model or "openrouter/free" in selected_model:
            actual_model = "openrouter/auto"
        else:
            actual_model = selected_model
    else:  # OpenAI
        actual_model = "gpt-4o-mini"

    # Prepare visual assets if present
    payload = []
    img_asset = None
    if image_file:
        try:
            img_asset = Image.open(image_file.file)
            payload.append(img_asset)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")

    # Select execution workflow prompts
    if selected_segment == "New Unknown Circuit Synthesis (Novel)":
        workflow_prompt = """
        EXECUTION WORKFLOW (NOVEL SYNTHESIS):
        You are in Inventor Mode. The user wants a circuit that is NOT standard.
        Use the 41 loaded rules as your building blocks to INVENT a new hardware solution.
        STEP 1: Define the novel requirements
        STEP 2: Select cross-domain components (e.g., mixing digital logic with power electronics)
        STEP 3: Generate the custom schematic logic (How do the blocks connect?)
        STEP 4: Calculate non-standard boundary conditions and values
        STEP 5: Provide a complete Bill of Materials (BOM)
        STEP 6: Identify potential points of failure in this novel design
        """
    elif selected_segment == "Standard Web-Based Project Circuits":
        workflow_prompt = """
        EXECUTION WORKFLOW (STANDARD WEB PROJECTS):
        The user wants a well-known, pre-named project commonly found on the internet (e.g., Instructables, GitHub).
        STEP 1: Identify the standard project name and typical web architecture
        STEP 2: List the standard, easily sourceable components
        STEP 3: Provide the standard pinout and wiring guide
        STEP 4: Provide the expected logic/code flow (if microcontrollers are used)
        STEP 5: List common issues students face when building this specific internet project
        """
    else:
        workflow_prompt = """
        EXECUTION WORKFLOW (ENGINEERING MODE):
        You must sequentially generate your response strictly following these 9 steps.
        STEP 1: Identify given specifications
        STEP 2: Identify unknown parameters
        STEP 3: Select equations (from RAG or standard physics)
        STEP 4: Substitute values
        STEP 5: Calculate results (Provide exact numerical values)
        STEP 6: Choose practical components (Standard values, ratings)
        STEP 7: Verify design / Generate Lab Tables (Expected readings, observations)
        STEP 8: List common lab mistakes
        STEP 9: Generate final circuit/project summary
        """

    final_prompt = f"""
    SYSTEM STATUS: Active
    
    USER SYSTEM PARAMETERS: {user_goal}
    
    --- RAG KNOWLEDGE BASE ---
    {injected_rules}
    --------------------------
    
    CRITICAL DIRECTIVES:
    Theory MUST NOT exceed 10% of the total response. Calculations, tables, hardware mappings, and practical guidance MUST exceed 50%.
    
    {workflow_prompt}
    
    ADDITIONAL SIMULATION DIRECTIVE:
    If the design involves a microcontroller, programmable IC, or digital simulation (e.g. Arduino, ESP32, 555 timer, etc.), you MUST append a section at the very end of your response titled "🎮 ONLINE SIMULATION & CODE GUIDE".
    In this section, provide:
    1. A complete, well-commented simulation code block (e.g., C/C++ for Arduino/ESP32).
    2. A step-by-step description of how to wire this circuit in Wokwi.
    3. A clear instruction to copy this code and simulate the design online at Wokwi by using a markdown link to https://wokwi.com.
    """
    payload.append(final_prompt)
    
    # Model communication routing
    try:
        if is_openrouter or is_openai:
            content_parts = []
            for item in payload:
                if isinstance(item, Image.Image):
                    buffered = BytesIO()
                    item.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_str}"
                        }
                    })
                else:
                    content_parts.append({
                        "type": "text",
                        "text": str(item)
                    })
                    
            if is_openrouter:
                endpoint = "https://openrouter.ai/api/v1/chat/completions"
            else:
                endpoint = "https://api.openai.com/v1/chat/completions"
                
            headers = {
                "Authorization": f"Bearer {api_key_stripped}",
                "Content-Type": "application/json",
            }
            payload_data = {
                "model": actual_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a strict technical AI. Output only step-by-step proofs, lab tables, and practical hardware derivations. Do not output conversational filler."
                    },
                    {
                        "role": "user",
                        "content": content_parts if len(content_parts) > 1 else content_parts[0]["text"]
                    }
                ],
                "temperature": 0.3
            }
            res = requests.post(
                endpoint,
                headers=headers,
                json=payload_data,
                timeout=60
            )
            res.raise_for_status()
            res_json = res.json()
            output_text = res_json["choices"][0]["message"]["content"]
        else:
            client = genai.Client(api_key=api_key_stripped)
            response = client.models.generate_content(
                model=actual_model,
                contents=payload,
                config=types.GenerateContentConfig(
                    system_instruction="You are a strict technical AI. Output only step-by-step proofs, lab tables, and practical hardware derivations. Do not output conversational filler.",
                    temperature=0.3
                )
            )
            output_text = response.text
            
        return {"output": output_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
