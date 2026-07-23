# 🛡️ cmdsec — Analizzatore di Sicurezza per Comandi da Terminale e Script Bash

[![GitHub release](https://img.shields.io/github/v/release/simdlldev/cmdsec)](https://github.com/simdlldev/cmdsec/releases)
[![Licenza](https://img.shields.io/badge/licenza-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://python.org)
[![PEP 668 Compliant](https://img.shields.io/badge/PEP_668-Compatibile-success.svg)](https://peps.python.org/pep-0668/)

**cmdsec** è uno strumento da riga di comando progettato per analizzare comandi Linux e script Bash prima della loro esecuzione, identificando potenziali rischi di sicurezza, comandi distruttivi o comportamenti malevoli.

[🇬🇧 Read English Documentation](README.md)

---

## 💡 Come Funziona

`cmdsec` funge da assistente di sicurezza per il tuo terminale:

1. **Analisi del Rischio**: Ispeziona il comando o lo script fornito, valutando modifiche di sistema, cancellazioni di dati, rischi per i file di sistema o connessioni di rete sospette.
2. **Valutazione su 5 Livelli di Colore**: Restituisce un box di verdetto chiaro e colorato:
   - 🟢 **GREEN (Verde)**: Comando sicuro e standard.
   - 🟡 **YELLOW (Giallo)**: Rischio basso (es. modifiche a file di configurazione utente).
   - 🟠 **ORANGE (Arancione)**: Eseguire con attenzione (possibili effetti collaterali).
   - 🔴 **RED (Rosso)**: Potenzialmente pericoloso (perdita dati o interruzione servizi).
   - 🟣 **PURPLE (Viola)**: Distruttivo / Malevolo (cancellazione dischi, malware, rischio grave).
3. **Modalità Interattiva**: Avvia `cmdsec` senza argomenti per digitare o incollare comandi complessi (contenenti `&&`, `;`, `|`) senza dover inserire virgolette.
4. **Lingua di Sistema Automatica**: Rileva la lingua di sistema ed adatta automaticamente l'interfaccia e le spiegazioni in Italiano o Inglese.

---

## 🚀 Installazione

Clona il repository ed esegui `install.sh`:

```bash
git clone https://github.com/simdlldev/cmdsec.git
cd cmdsec
./install.sh
```

Durante l'installazione ti verrà chiesto di inserire una **Google Gemini API Key** gratuita (ottienila su [Google AI Studio](https://aistudio.google.com/app/apikey)).

Assicurati che `~/.local/bin` sia nel tuo `$PATH`. Se necessario, aggiungi questa riga al tuo `~/.bashrc` o `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## 📖 Utilizzo

### Modalità Interattiva (Consigliata)
Esegui `cmdsec` senza parametri per inserire qualsiasi comando in modo sicuro:
```bash
cmdsec
```

### Analisi Diretta di un Comando
```bash
cmdsec rm -rf /tmp/test
```

### Analisi Tecnica Dettagliata (`-a`)
```bash
cmdsec -a cat /etc/shadow
```

### Analisi di Script Bash (`-s`)
```bash
cmdsec -s script.sh setup.sh
```

---

## 🗑️ Disinstallazione

Per rimuovere `cmdsec` dal tuo sistema:

```bash
./uninstall.sh
```

---

## ⚠️ Esonero di Responsabilità (Disclaimer)

Questo software viene fornito **"così com'è" (AS IS)**, senza garanzie di alcun tipo, espresse o implicite, incluse, a titolo esemplificativo, garanzie di commerciabilità o idoneità per uno scopo particolare.

- **Analisi IA**: Le valutazioni di sicurezza sono generate tramite Intelligenza Artificiale e possono occasionalmente contenere inesattezze, falsi positivi o falsi negativi.
- **Responsabilità dell'Utente**: L'utente è l'unico ed esclusivo responsabile della verifica e dell'esecuzione di qualsiasi comando sul proprio sistema. In nessun caso gli autori o i titolari del copyright saranno responsabili per danni, perdite di dati o malfunzionamenti derivanti dall'uso di `cmdsec` o dall'esecuzione dei comandi analizzati.

---

## 📜 Licenza

Distribuito sotto licenza **MIT**. Copyright © 2026 simdlldev.
