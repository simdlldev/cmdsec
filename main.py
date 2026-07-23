#!/usr/bin/env python3
import os
import sys
import argparse
import platform
import locale
import shutil
import textwrap
import re
import json
import warnings
from typing import Literal, Optional
from colorama import Fore, Back, Style, init

# Sopprime warning non necessari per mantenere pulita l'interfaccia
warnings.filterwarnings("ignore")

# Inizializza colorama
init(autoreset=True)

# Configurazione Versione
VERSION = "1.0.0"

# Colore Arancione ANSI Custom (256-color mode, code 208)
ANSI_ORANGE = "\033[38;5;208m"


def detect_language() -> str:
    """Rileva la lingua del sistema. Ritorna 'it' se italiano, altrimenti 'en' (default)."""
    lang_env = os.getenv('LC_ALL') or os.getenv('LANG') or 'en_US'
    if lang_env.lower().startswith('it'):
        return 'it'
    return 'en'


# Dizionario di Localizzazione (I18N)
MESSAGES = {
    "it": {
        "help_desc": "cmdsec - Security Analyzer CLI basato su IA",
        "verdict_scale_title": "SCALA DEI VERDETTI:",
        "v_green_desc": "Sicuro. Operazione standard senza rischi noti.",
        "v_yellow_desc": "Nessun rischio particolare (es. modifiche a file utente).",
        "v_orange_desc": "Eseguire con attenzione. Possibili effetti collaterali.",
        "v_red_desc": "Potenzialmente pericoloso. Può causare perdita dati o instabilità.",
        "v_purple_desc": "Distruttivo / Malevolo. Rischio catastrofico per il sistema.",
        "disclaimer": "DISCLAIMER: Analisi generata da IA. Possibili allucinazioni e/o errori. Verifica sempre manualmente.",
        "arg_a": "Analisi dettagliata",
        "arg_script": "Analizza uno o più script (separati da spazio)",
        "arg_debug": "Mostra informazioni di debug",
        "arg_version": "Mostra la versione del programma",
        "arg_command": "Il comando da analizzare",
        "interactive_title": "cmdsec - Modalità Interattiva",
        "interactive_desc": "Inserisci il comando da analizzare:",
        "interactive_prompt": "cmdsec > ",
        "interactive_cancel": "Operazione annullata.",
        "interactive_no_input": "[ERROR] Nessun comando inserito. Uscita.",
        "analyzing": "Analisi sicurezza in corso......",
        "ai_disclaimer_sub": "(Risultati generati da IA possono contenere errori, verifica sempre)",
        "stop_purple": " ⛔ STOP! ESECUZIONE FORTEMENTE SCONSIGLIATA ⛔ ",
        "stop_purple_sub": "Questo comando è stato identificato come distruttivo o malevolo.",
        "warn_red": " ⚠️  ATTENZIONE: Procedere con cautela.",
        "tech_details": "🔍 DETTAGLI TECNICI:",
        "v_titles": {
            "GREEN": ("🟢", "SICURO", Fore.GREEN),
            "YELLOW": ("🟡", "NON PRESENTA PARTICOLARI RISCHI", Fore.YELLOW),
            "ORANGE": ("🟠", "ESEGUIRE CON ATTENZIONE", ANSI_ORANGE),
            "RED": ("🔴", "COMANDO POTENZIALMENTE PERICOLOSO", Fore.RED),
            "PURPLE": ("🟣", "MOLTO PERICOLOSO / DISTRUTTIVO / CATASTROFICO", Fore.MAGENTA),
            "UNKNOWN": ("⚪", "SCONOSCIUTO", Fore.WHITE)
        },
        "file_not_found": "[WARNING] File non trovato: {path} (saltato)",
        "file_read_error": "[ERROR] Errore leggendo {path}: {error}",
        "no_valid_scripts": "[ERROR] Nessuno script valido trovato. Uscita.",
        "user_interrupted": "Interrotto dall'utente.",
        "dep_pydantic": "[ERROR] Libreria 'pydantic' non installata. Esegui: pip install pydantic",
        "dep_genai": "[ERROR] Libreria 'google-genai' non installata. Esegui: pip install google-genai",
        "env_key_missing": "[ERROR] Variabile d'ambiente GEMINI_API_KEY non trovata."
    },
    "en": {
        "help_desc": "cmdsec - AI-powered CLI Security Analyzer",
        "verdict_scale_title": "VERDICT SCALE:",
        "v_green_desc": "Safe. Standard operation with no known risks.",
        "v_yellow_desc": "No specific risks (e.g. user configuration changes).",
        "v_orange_desc": "Execute with caution. Potential side effects.",
        "v_red_desc": "Potentially dangerous. May cause data loss or system instability.",
        "v_purple_desc": "Destructive / Malicious. Catastrophic risk to system.",
        "disclaimer": "DISCLAIMER: AI-generated analysis. Hallucinations or errors possible. Always verify manually.",
        "arg_a": "Detailed analysis",
        "arg_script": "Analyze one or more scripts (separated by space)",
        "arg_debug": "Show debug information",
        "arg_version": "Show program version",
        "arg_command": "The command to analyze",
        "interactive_title": "cmdsec - Interactive Mode",
        "interactive_desc": "Enter the command to analyze:",
        "interactive_prompt": "cmdsec > ",
        "interactive_cancel": "Operation cancelled.",
        "interactive_no_input": "[ERROR] No command entered. Exiting.",
        "analyzing": "Security analysis in progress......",
        "ai_disclaimer_sub": "(AI-generated results may contain errors, always verify)",
        "stop_purple": " ⛔ STOP! EXECUTION STRONGLY DISCOURAGED ⛔ ",
        "stop_purple_sub": "This command has been identified as destructive or malicious.",
        "warn_red": " ⚠️  WARNING: Proceed with caution.",
        "tech_details": "🔍 TECHNICAL DETAILS:",
        "v_titles": {
            "GREEN": ("🟢", "SAFE", Fore.GREEN),
            "YELLOW": ("🟡", "NO SPECIFIC RISKS", Fore.YELLOW),
            "ORANGE": ("🟠", "EXECUTE WITH CAUTION", ANSI_ORANGE),
            "RED": ("🔴", "POTENTIALLY DANGEROUS", Fore.RED),
            "PURPLE": ("🟣", "HIGHLY DANGEROUS / DESTRUCTIVE / CATASTROPHIC", Fore.MAGENTA),
            "UNKNOWN": ("⚪", "UNKNOWN", Fore.WHITE)
        },
        "file_not_found": "[WARNING] File not found: {path} (skipped)",
        "file_read_error": "[ERROR] Error reading {path}: {error}",
        "no_valid_scripts": "[ERROR] No valid scripts found. Exiting.",
        "user_interrupted": "Interrupted by user.",
        "dep_pydantic": "[ERROR] 'pydantic' library not installed. Run: pip install pydantic",
        "dep_genai": "[ERROR] 'google-genai' library not installed. Run: pip install google-genai",
        "env_key_missing": "[ERROR] GEMINI_API_KEY environment variable not found."
    }
}

# Lingua attiva per la sessione
CURRENT_LANG = detect_language()
T = MESSAGES[CURRENT_LANG]

# Lazy import di pydantic per performance
try:
    from pydantic import BaseModel, Field
except ImportError:
    print(f"{Fore.RED}{T['dep_pydantic']}{Style.RESET_ALL}")
    sys.exit(1)


class SecurityAnalysis(BaseModel):
    verdict: Literal["GREEN", "YELLOW", "ORANGE", "RED", "PURPLE"] = Field(
        description="The security risk verdict code: GREEN, YELLOW, ORANGE, RED, or PURPLE."
    )
    description: str = Field(
        description="Description of what the command/script does and potential security impact in the requested language."
    )
    details: str = Field(
        description="Detailed technical explanation if requested (or empty string if not requested)."
    )


class SupervisorCheck(BaseModel):
    verdict: Literal["GREEN", "YELLOW", "ORANGE", "RED", "PURPLE", "CONFIRM"] = Field(
        description="Revised Verdict Code if original was wrong, or 'CONFIRM' if acceptable."
    )


def clean_json_string(text: str) -> str:
    """Pulisce la stringa fornita dall'IA rimuovendo blocchi markdown e caratteri spuri intorno al JSON."""
    if not text:
        return ""
    text = text.strip()
    
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        text = text[start_idx:end_idx + 1]
        
    return text.strip()


def format_markdown(text):
    """Interpreta un sottoinsieme di Markdown e lo converte in ANSI."""
    text = re.sub(r'`([^`]+)`', lambda m: f'{Back.LIGHTBLACK_EX}{Fore.WHITE} {m.group(1)} {Style.RESET_ALL}', text)
    text = re.sub(r'\*\*([^*]+)\*\*', lambda m: f'{Style.BRIGHT}{m.group(1)}{Style.RESET_ALL}', text)
    text = re.sub(r'\*([^*]+)\*', lambda m: f'{Style.DIM}{m.group(1)}{Style.RESET_ALL}', text)
    return text


def get_system_context():
    """Raccoglie informazioni sul sistema operativo e sulla lingua."""
    try:
        import distro
        distro_name = distro.name(pretty=True)
    except ImportError:
        distro_name = "Linux"
    except Exception:
        distro_name = "Unknown Distro"
    
    os_name = platform.system()
    release = platform.release()
    user = os.getenv('USER', 'unknown')
    is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    
    context = f"OS: {os_name} ({distro_name})\nKernel: {release}\nUser: {user} (Root: {is_root})\nLanguage: {CURRENT_LANG}"
    return context, CURRENT_LANG


def setup_gemini():
    """Configura il client Google GenAI e restituisce il client ed i nomi dei modelli."""
    try:
        from google import genai
    except ImportError:
        print(f"{Fore.RED}{T['dep_genai']}{Style.RESET_ALL}")
        sys.exit(1)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(f"{Fore.RED}{T['env_key_missing']}{Style.RESET_ALL}")
        sys.exit(1)
    
    client = genai.Client(api_key=api_key)
    main_model_name = 'models/gemma-4-31b-it'
    supervisor_model_name = 'models/gemma-4-26b-it'

    return client, main_model_name, supervisor_model_name


def get_verdict_style(verdict_code):
    code = verdict_code.upper().strip()
    v_dict = T["v_titles"]
    for key, val in v_dict.items():
        if key in code:
            return val
    return v_dict["UNKNOWN"]


def double_check_verdict(client, supervisor_model_name: str, original_analysis: SecurityAnalysis, sys_lang: str, debug: bool) -> SecurityAnalysis:
    """Usa un modello piccolo con output JSON per validare la coerenza tra analisi e verdetto."""
    if not client or not supervisor_model_name:
        return original_analysis

    prompt = f"""
    ROLE: Security Audit Supervisor.
    TASK: Review the analysis provided by a security analyst for consistency.
    
    INPUT ANALYSIS:
    Verdict: {original_analysis.verdict}
    Description: {original_analysis.description}
    Details: {original_analysis.details}
    
    CRITICAL RULES:
    1. ESCALATION (Strict): Only escalate to RED/PURPLE if the analysis confirms CONCRETE MALICIOUS BEHAVIOR (wiping disks, reverse shells, malware dropper, if can compromise system or make system unbootable/unusable escalate directly to PURPLE).
       - Do NOT escalate based on "low potential risks", "theoretical vulnerabilities", or "suspicious" flags if the context implies a user script (only if there are no dangerous commands).
       - Modifying user config files (e.g., .bashrc) or running background jobs is YELLOW/ORANGE, NOT RED/PURPLE.
    2. DE-ESCALATION: If verdict is RED/PURPLE but the analysis describes SAFE/STANDARD behavior (e.g., user config, logs, simple echoes, local file writes) -> Set GREEN/YELLOW.
    3. CONSISTENCY: The Verdict Code MUST match the Description.
    
    ACTION:
    - If verdict is clearly wrong: Output NEW Verdict Code.
    - If verdict is acceptable/debatable: Output "CONFIRM".
    """
    
    try:
        from google.genai import types
        if debug: print(f"{Fore.BLUE}[DEBUG] Running Supervisor Check (Structured Output)...{Style.RESET_ALL}")
        
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SupervisorCheck
        )
        res = client.models.generate_content(
            model=supervisor_model_name,
            contents=prompt,
            config=config
        )
        cleaned_json = clean_json_string(res.text)
        parsed = SupervisorCheck.model_validate_json(cleaned_json)
        check_verdict = parsed.verdict.upper()
        
        if debug: print(f"{Fore.BLUE}[DEBUG] Supervisor says: {check_verdict}{Style.RESET_ALL}")

        valid_verdicts = ["GREEN", "YELLOW", "ORANGE", "RED", "PURPLE"]
        if check_verdict != "CONFIRM" and check_verdict in valid_verdicts and check_verdict != original_analysis.verdict:
            old_icon = get_verdict_style(original_analysis.verdict)[0]
            adj_note = f"\n\n(⚠️ VERDICT ADJUSTED BY SUPERVISOR AI: Original was {old_icon} {original_analysis.verdict})"
            
            return SecurityAnalysis(
                verdict=check_verdict,
                description=original_analysis.description + adj_note,
                details=original_analysis.details
            )
            
    except Exception as e:
        if debug: print(f"{Fore.RED}[DEBUG] Supervisor Error: {e}{Style.RESET_ALL}")

    return original_analysis


def analyze_command(client, main_model_name: str, supervisor_model_name: str, input_text: str, is_script: bool, detailed_mode: bool, sys_lang: str, debug: bool, advanced_debug: bool, script_path=None) -> SecurityAnalysis:
    from google.genai import types
    
    context_str, lang_code = get_system_context()
    inputType = "SCRIPT CONTENT" if is_script else "COMMAND"
    path_info = f"\nSCRIPT PATH: {script_path}" if script_path else ""
    
    detail_instruction = ""
    if detailed_mode:
        detail_instruction = "Provide a DETAILED technical explanation (max 15 rows) in the 'details' field. Use markdown formatting."
    else:
        detail_instruction = "Leave the 'details' field empty."

    lang_full = "Italian" if lang_code == "it" else "English"

    prompt = f"""
    You are a Linux Security Expert CLI tool.
    
    SYSTEM CONTEXT:
    {context_str}
    
    TASK:
    Analyze the following {inputType} for security risks in its ENTIRETY.{path_info}
    
    IMPORTANT: 
    1. Respond strictly in '{lang_full}' ({lang_code}) for the 'description' and 'details' fields.
    2. Pay close attention to edge cases, special characters, obfuscation techniques, chained commands (&&, ;, |), and suspicious flags.
    3. Be BALANCED: Do not exaggerate risks for standard advanced administration tools unless they are explicitly destructive or malicious in context.
    4. DECODE and ANALYZE any encoded strings (Base64, Hex, etc.) to reveal the real payload. Judge the decoded payload, not the encoding itself.
    5. Detect various threats: wipe commands (rm -rf /, dd, wipefs), fork bombs, reverse shells, privilege escalation attempts.
    6. If the provided script is not a bash script, parse it anyway.
    
    INPUT:
    ```bash
    {input_text}
    ```
    
    INSTRUCTIONS FOR FIELDS:
    - 'verdict': Security risk level ('GREEN', 'YELLOW', 'ORANGE', 'RED', 'PURPLE').
      - GREEN: Safe.
      - YELLOW: No specific risks (standard operations).
      - ORANGE: Execute with caution (potential side effects).
      - RED: Potentially dangerous (deletes data, stops services, exposure).
      - PURPLE: Catastrophic/Destructive/Malicious (system destruction, malware, unrecoverable data loss).
    - 'description': Short summary description (max 2 sentences) explaining what the command/script does and its risk.
    - 'details': {detail_instruction}
    """
    
    if advanced_debug:
        print(f"\n{Fore.MAGENTA}[DEBUG-ADV] PROMPT SENT TO MAIN MODEL:{Style.RESET_ALL}")
        print(prompt)
        print(f"{Fore.MAGENTA}{'-'*40}{Style.RESET_ALL}")

    try:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SecurityAnalysis
        )
        res = client.models.generate_content(
            model=main_model_name,
            contents=prompt,
            config=config
        )
        raw_json = res.text.strip()
        cleaned_json = clean_json_string(raw_json)
        
        if advanced_debug:
            print(f"\n{Fore.MAGENTA}[DEBUG-ADV] RAW JSON RESPONSE (MAIN):{Style.RESET_ALL}")
            print(raw_json)
            print(f"\n{Fore.MAGENTA}[DEBUG-ADV] CLEANED JSON RESPONSE:{Style.RESET_ALL}")
            print(cleaned_json)

        analysis = SecurityAnalysis.model_validate_json(cleaned_json)
        final_analysis = double_check_verdict(client, supervisor_model_name, analysis, sys_lang, debug or advanced_debug)
        return final_analysis

    except Exception as e:
        if debug or advanced_debug:
            print(f"{Fore.RED}[DEBUG] API/JSON Error: {e}{Style.RESET_ALL}")
        return SecurityAnalysis(
            verdict="RED",
            description=f"API Error: {str(e)}",
            details=""
        )


def get_visual_width(text):
    icons = ["🟢", "🟡", "🟠", "🔴", "🟣", "⚪"]
    width = len(text)
    for icon in icons:
        width += text.count(icon)
    return width


def draw_boxed_output(icon, title, color, description, details, detailed_mode, verdict_code):
    """Disegna un box colorato e perfettamente allineato."""
    term_width = shutil.get_terminal_size((80, 20)).columns
    box_width = min(int(term_width * 0.75), 100)
    
    wrapper = textwrap.TextWrapper(width=box_width - 4)
    desc_lines = wrapper.wrap(description)
    
    reset = Style.RESET_ALL
    b_side = f"{color}┃{reset}"
    
    title_text = f" {icon} {title} {icon} "
    visual_title_len = get_visual_width(title_text)
    total_padding = box_width - 2 - visual_title_len
    pad_left = total_padding // 2
    pad_right = total_padding - pad_left
    
    top_line = f"{color}┏{'━' * pad_left}{Style.BRIGHT}{title_text}{Style.RESET_ALL}{color}{'━' * pad_right}┓{reset}"
    bottom_line = f"{color}┗{'━' * (box_width - 2)}┛{reset}"

    print(f"\n{top_line}")
    for line in desc_lines:
        line_pad = box_width - 4 - len(line)
        print(f"{b_side} {line}{' ' * line_pad} {b_side}")
    print(bottom_line)

    # AVVISI DI SICUREZZA
    v_upper = verdict_code.upper()
    if "PURPLE" in v_upper:
        print(f"\n{Back.MAGENTA}{Fore.WHITE}{Style.BRIGHT}{T['stop_purple']}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{T['stop_purple_sub']}{Style.RESET_ALL}")
    elif "RED" in v_upper:
        print(f"\n{Fore.RED}{Style.BRIGHT}{T['warn_red']}{Style.RESET_ALL}")

    if detailed_mode and details:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{T['tech_details']}{Style.RESET_ALL}")
        paragraphs = details.split('\n')
        for p in paragraphs:
            if not p.strip():
                print() 
                continue
            fmt_p = format_markdown(p)
            detail_lines = textwrap.wrap(fmt_p, width=box_width + 10, break_long_words=False)
            for line in detail_lines:
                print(f"  {line.strip()}")
        print()


def main():
    help_description = f"""
{Fore.CYAN}{Style.BRIGHT}{T['help_desc']}{Style.RESET_ALL}

{Style.BRIGHT}{T['verdict_scale_title']}{Style.RESET_ALL}
  🟢 {Fore.GREEN}GREEN{Style.RESET_ALL}  : {T['v_green_desc']}
  🟡 {Fore.YELLOW}YELLOW{Style.RESET_ALL} : {T['v_yellow_desc']}
  🟠 {ANSI_ORANGE}ORANGE{Style.RESET_ALL} : {T['v_orange_desc']}
  🔴 {Fore.RED}RED{Style.RESET_ALL}    : {T['v_red_desc']}
  🟣 {Fore.MAGENTA}PURPLE{Style.RESET_ALL} : {T['v_purple_desc']}
"""
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=help_description,
        epilog=f"{Fore.YELLOW}{T['disclaimer']}{Style.RESET_ALL}\n\n© 2026 simdlldev"
    )
    
    parser.add_argument("-a", action="store_true", help=T['arg_a'])
    parser.add_argument("-s", "--script", nargs='+', help=T['arg_script'])
    parser.add_argument("-d", "--debug", action="store_true", help=T['arg_debug'])
    parser.add_argument("-D", "--debug-advanced", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-v", "--version", action="version", version=f"cmdsec v{VERSION}")
    parser.add_argument("command", nargs=argparse.REMAINDER, help=T['arg_command'])
    args = parser.parse_args()
    
    content_to_analyze = ""
    is_file = False
    script_path = None

    if not args.command and not args.script:
        #print(f"{Fore.CYAN}{Style.BRIGHT}{T['interactive_title']}{Style.RESET_ALL}")
        print(f"{Style.DIM}{T['interactive_desc']}{Style.RESET_ALL}")
        try:
            user_input = input(f"{Fore.YELLOW}{Style.BRIGHT}{T['interactive_prompt']}{Style.RESET_ALL}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n" + Fore.YELLOW + T['interactive_cancel'] + Style.RESET_ALL)
            sys.exit(0)
            
        if not user_input:
            print(f"{Fore.RED}{T['interactive_no_input']}{Style.RESET_ALL}")
            sys.exit(1)
            
        content_to_analyze = user_input
    elif args.script:
        is_file = True
        contents = []
        paths = []
        valid_files = 0
        
        for s_path in args.script:
            if not os.path.exists(s_path):
                print(f"{Fore.YELLOW}{T['file_not_found'].format(path=s_path)}{Style.RESET_ALL}")
                continue
                
            valid_files += 1
            abs_path = os.path.abspath(s_path)
            paths.append(abs_path)
            try:
                with open(s_path, 'r') as f:
                    header = f"\n# --- START OF FILE: {abs_path} ---\n"
                    footer = f"\n# --- END OF FILE: {abs_path} ---\n"
                    contents.append(header + f.read() + footer)
            except Exception as e:
                print(f"{Fore.RED}{T['file_read_error'].format(path=s_path, error=e)}{Style.RESET_ALL}")
        
        if valid_files == 0:
            print(f"{Fore.RED}{T['no_valid_scripts']}{Style.RESET_ALL}")
            sys.exit(1)
            
        content_to_analyze = "\n".join(contents)
        script_path = "; ".join(paths)
    else:
        content_to_analyze = " ".join(args.command)

    print(f"{Fore.CYAN}{T['analyzing']}{Style.RESET_ALL}")
    print(f"{Style.DIM}{T['ai_disclaimer_sub']}{Style.RESET_ALL}", end="\r")
    
    client, main_model_name, supervisor_model_name = setup_gemini()
    
    if args.debug or args.debug_advanced:
        print(f"\n{Fore.MAGENTA}[DEBUG] Main Model: {main_model_name}")
        if supervisor_model_name:
            print(f"[DEBUG] Supervisor Model: {supervisor_model_name}{Style.RESET_ALL}")

    _, sys_lang = get_system_context()
    
    analysis = analyze_command(client, main_model_name, supervisor_model_name, content_to_analyze, is_file, args.a, sys_lang, args.debug, args.debug_advanced, script_path)
    
    if not (args.debug or args.debug_advanced):
        sys.stdout.write("\033[F\033[K")
        sys.stdout.flush()

    icon, title, color = get_verdict_style(analysis.verdict)
    
    draw_boxed_output(icon, title, color, analysis.description, analysis.details or "", args.a, analysis.verdict)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Fore.YELLOW + T['user_interrupted'] + Style.RESET_ALL)
        sys.exit(0)
