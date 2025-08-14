# Bilal Mobile Ad Blocker v1.6 (Free, all features)
# Safe ADB-based one-click ads cleanup with rules, strict/safe modes, undo, skins, sponsor bar.

import os, sys, subprocess, threading, json, re, shutil, time, platform, random, base64, webbrowser, urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "Bilal Mobile Ad Blocker"
APP_VER  = "1.6.0"
APP_ID   = "BilalMobileAdBlocker"
IS_WIN   = platform.system().lower().startswith("win")

APPDATA = os.path.join(os.environ.get("LOCALAPPDATA", os.getcwd()), APP_ID)
os.makedirs(APPDATA, exist_ok=True)
LOG_FILE = os.path.join(APPDATA, "log.txt")
BACKUP_FILE = os.path.join(APPDATA, "disabled_backup.json")
SETTINGS_FILE = os.path.join(APPDATA, "settings.json")
PLATFORM_TOOLS_DIR = os.path.join(APPDATA, "platform-tools")
ADB_BIN = os.path.join(PLATFORM_TOOLS_DIR, "adb.exe" if IS_WIN else "adb")

CONTACT_WA = "+923018898848"
CONTACT_WA_URL = "https://wa.me/923018898848?text=Hello%20from%20Bilal%20Mobile%20Ad%20Blocker"
CREDIT_TEXT = "Developed by M. Bilal"

# Set these later when your ads.json / rules.json are ready
AD_CONFIG_URL = ""
AD_MUTE_FILE = os.path.join(APPDATA, "ads_mute.json")
RULES_URL  = ""
RULES_FILE = os.path.join(APPDATA, "rules.json")

SKINS = {
    "Bilal Green":  {"primary":"#1e7f39", "primaryDark":"#155f2b", "accent":"#e8f5e9", "textOnPrimary":"#ffffff"},
    "Dark":         {"primary":"#0f172a", "primaryDark":"#0b1221", "accent":"#1f2937", "textOnPrimary":"#ffffff"},
    "Light Blue":   {"primary":"#1e3a8a", "primaryDark":"#162c6a", "accent":"#e6eef8", "textOnPrimary":"#ffffff"},
}
DEFAULT_SKIN = "Bilal Green"

WHITELIST = {
    "com.android.vending","com.android.chrome","com.google.android.gms","com.google.android.gsf",
    "com.google.android.inputmethod.latin","com.android.systemui","com.android.settings",
    "com.android.contacts","com.android.phone"
}

BASE_BLACKLIST = {"com.facebook.appmanager","com.facebook.services","com.facebook.system","com.android.bips"}
TRANSSION_COMMON = {"com.transsion.appstore","com.transsion.phonemaster","com.carlcare.service","com.ahagames.app","com.mobiletool.taichi","com.transsion.vtools","com.transsion.afmanager"}
OPPO_GROUP = {"com.heytap.mcs","com.heytap.usercenter","com.oppo.market","com.coloros.gamespace","com.coloros.music","com.coloros.video","com.coloros.weather2","com.coloros.calendar"}
VIVO_GROUP = {"com.vivo.ad","com.vivo.browser","com.vivo.assistant","com.vivo.game","com.vivo.wallet","com.vivo.easyshare"}
SAMSUNG_GROUP = {"com.samsung.android.game.gamehome","com.samsung.android.game.gos","com.samsung.android.app.spage","com.samsung.android.mateagent","com.samsung.android.themestore","com.sec.android.app.sbrowser"}
XIAOMI_GROUP  = {"com.miui.systemAdSolution","com.miui.msa.global","com.miui.analytics","com.miui.hybrid","com.miui.hybrid.accessory","com.miui.bugreport","com.miui.daemon","com.miui.mipicks","com.miui.player","com.miui.videoplayer","com.miui.weather2","com.miui.browser","com.mi.globalbrowser","com.miui.android.fashiongallery","com.glance.internet"}
NOTHING_GROUP = {"com.nothing.hub","com.nothing.weather","com.nothing.smarthub"}

BRAND_BLACKLISTS = {
    "tecno": TRANSSION_COMMON, "infinix": TRANSSION_COMMON, "itel": TRANSSION_COMMON, "sparx": TRANSSION_COMMON,
    "oppo": OPPO_GROUP, "realme": OPPO_GROUP, "oneplus": OPPO_GROUP,
    "vivo": VIVO_GROUP, "iqoo": VIVO_GROUP,
    "samsung": SAMSUNG_GROUP,
    "xiaomi": XIAOMI_GROUP,
    "nothing": NOTHING_GROUP,
}

STRICT_EXTRA = {
    "global": {"com.glance.internet","com.miui.android.fashiongallery"},
    "tecno": {"com.transsion.appstore","com.transsion.phonemaster","com.ahagames.app"},
    "infinix": {"com.transsion.appstore","com.transsion.phonemaster","com.ahagames.app"},
    "itel": {"com.transsion.appstore","com.transsion.phonemaster","com.ahagames.app"},
    "sparx": {"com.transsion.appstore","com.transsion.phonemaster","com.ahagames.app"},
    "oppo": {"com.oppo.market","com.coloros.gamespace","com.coloros.video","com.coloros.music"},
    "vivo": {"com.vivo.browser","com.vivo.game"},
    "samsung": {"com.samsung.android.app.spage","com.samsung.android.game.gamehome","com.sec.android.app.sbrowser"},
    "xiaomi": {"com.miui.browser","com.mi.globalbrowser","com.miui.videoplayer","com.miui.player","com.miui.weather2"},
    "nothing": set(),
}

UNINSTALL_PREFERRED = {"com.transsion.appstore","com.transsion.phonemaster","com.ahagames.app","com.oppo.market","com.coloros.gamespace","com.vivo.browser","com.miui.browser","com.mi.globalbrowser","com.sec.android.app.sbrowser","com.glance.internet"}

KEYWORDS = [
    "ads","adservice","admob","advert","msa","tracker","analytics","tracking","push","mipush",
    "recommend","promo","market","hotword","heytap","xos","hios","transsion","palm","store",
    "browser","news","wallpaper","cleaner","callerid","flashlight","miui","glance","fashiongallery","hotapps","hotgames"
]
SAFE_EXCLUDE = {"com.transsion.hilauncher","com.xos.launcher","com.coloros.launcher","com.vivo.launcher","com.sec.android.app.launcher","com.miui.home","com.nothing.launcher"}

LOCAL_RULES = {
  "version": "2025.08-pro",
  "global": {"safe": list(BASE_BLACKLIST), "strict": list(STRICT_EXTRA["global"])},
  "brands": {
    "xiaomi": {"safe": ["com.miui.systemAdSolution","com.miui.msa.global","com.miui.analytics"], "strict": ["com.miui.browser","com.mi.globalbrowser","com.miui.videoplayer","com.miui.player","com.miui.weather2","com.glance.internet","com.miui.android.fashiongallery"], "models": {}},
    "oppo":   {"safe": ["com.heytap.mcs","com.oppo.market"], "strict": ["com.coloros.gamespace","com.coloros.video","com.coloros.music"]},
    "realme": {"inherit": "oppo"},
    "oneplus":{"inherit": "oppo"},
    "vivo":   {"safe": ["com.vivo.ad","com.vivo.browser"], "strict": ["com.vivo.game","com.vivo.assistant"]},
    "iqoo":   {"inherit": "vivo"},
    "samsung":{"safe": ["com.samsung.android.game.gos","com.samsung.android.game.gamehome","com.samsung.android.app.spage","com.samsung.android.themestore","com.sec.android.app.sbrowser"]},
    "tecno":  {"safe": ["com.transsion.appstore","com.transsion.phonemaster","com.carlcare.service","com.ahagames.app","com.transsion.vtools","com.mobiletool.taichi"], "strict": ["com.ahagames.app"]},
    "infinix":{"inherit":"tecno"},
    "itel":   {"inherit":"tecno"},
    "sparx":  {"inherit":"tecno"},
    "nothing":{"safe": ["com.nothing.hub","com.nothing.weather","com.nothing.smarthub"]}
  }
}

def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return {"skin": "Bilal Green"}

def save_settings(obj):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump(obj, f, indent=2)
    except Exception: pass

def safe_write_log(s):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(s + "\n")
    except Exception: pass

def is_adlike(name):
    if name in WHITELIST: return False
    if name in BASE_BLACKLIST: return True
    if name.startswith("com.google.") or name.startswith("com.android."): return False
    low = name.lower()
    return any(k in low for k in KEYWORDS)

def detect_brand(props: dict):
    raw = (props.get("ro.product.brand") or props.get("ro.product.manufacturer") or "").lower()
    aliases = {"redmi":"xiaomi","poco":"xiaomi","mi":"xiaomi","realme":"oppo","oneplus":"oppo","iqoo":"vivo","sparex":"sparx"}
    for k,v in aliases.items():
        if k in raw: return v
    for b in ["xiaomi","nothing","tecno","infinix","itel","sparx","oppo","vivo","samsung"]:
        if b in raw: return b
    if "transsion" in raw: return "tecno"
    return raw or "unknown"

def get_brand_blacklist(brand): return BRAND_BLACKLISTS.get(brand, set())

class RuleEngine:
    def __init__(self): self.data = None
    def load_local(self): self.data = LOCAL_RULES
    def load_remote(self):
        if not RULES_URL: return False
        try:
            with urllib.request.urlopen(RULES_URL, timeout=8) as r:
                data = json.loads(r.read().decode("utf-8"))
            if "brands" in data and "global" in data:
                self.data = data
                with open(RULES_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
                return True
        except Exception: pass
        return False
    def ensure_rules(self):
        if self.data is not None: return
        if os.path.exists(RULES_FILE):
            try:
                with open(RULES_FILE, "r", encoding="utf-8") as f: self.data = json.load(f)
            except Exception: self.data = None
        if self.data is None:
            if not self.load_remote(): self.load_local()
    def version(self): return (self.data or {}).get("version","local")
    def _brand_blob(self, brand):
        d = (self.data or {})
        b = (d.get("brands", {}) or {}).get(brand, {})
        inh = b.get("inherit")
        if inh:
            base = (d.get("brands", {}) or {}).get(inh, {})
            return {"safe": sorted(set(base.get("safe", [])+b.get("safe", []))),
                    "strict": sorted(set(base.get("strict", [])+b.get("strict", []))),
                    "models": {**base.get("models", {}), **b.get("models", {})}}
        return {"safe": b.get("safe", []), "strict": b.get("strict", []), "models": b.get("models", {})}
    def _match_models(self, model, device, brand_blob, strict):
        add=[]; mdl=(model or "").lower(); dev=(device or "").lower()
        for pat, obj in (brand_blob.get("models", {}) or {}).items():
            tokens=[p.strip() for p in pat.lower().split("|") if p.strip()]
            if any(t in mdl or t in dev for t in tokens):
                add += obj.get("strict" if strict else "safe", [])
        return add
    def targets(self, brand, model, device, installed, strict=False):
        self.ensure_rules()
        d = self.data or {}
        g = d.get("global", {})
        b = self._brand_blob(brand)
        lst = set(g.get("safe", []) + b.get("safe", []))
        if strict:
            lst |= set(g.get("strict", []) + b.get("strict", []))
            lst |= set(self._match_models(model, device, b, strict=True))
        else:
            lst |= set(self._match_models(model, device, b, strict=False))
        return sorted((set(lst) & set(installed)) - SAFE_EXCLUDE)

class ADB:
    def __init__(self, log_cb):
        self.log = log_cb; self.adb = None; self.ensure_adb()
    def logw(self, s): self.log(s); safe_write_log(s)
    def ensure_adb(self):
        if os.path.exists(ADB_BIN): self.adb = ADB_BIN; return
        if shutil.which("adb"): self.adb = "adb"; return
        self.adb = None
    def have_adb(self): return self.adb is not None and (self.adb == "adb" or os.path.exists(self.adb))
    def download_platform_tools(self, progress_cb=None):
        url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        self.logw("Downloading platform-tools from Google...")
        os.makedirs(PLATFORM_TOOLS_DIR, exist_ok=True)
        try:
            with urllib.request.urlopen(url) as r:
                total = int(r.headers.get("Content-Length","0")); import io, zipfile
                buf = io.BytesIO(); got=0; CH=64*1024
                while True:
                    ch = r.read(CH)
                    if not ch: break
                    buf.write(ch); got+=len(ch)
                    if total and progress_cb: progress_cb(int(got*100/total))
            zipfile.ZipFile(buf).extractall(APPDATA)
            self.adb = ADB_BIN; self.logw("Platform-tools downloaded."); return True
        except Exception as e:
            self.logw(f"Download failed: {e}"); return False
    def _run(self, args, serial=None, timeout=None):
        if not self.have_adb(): return "", "ADB not found", 1
        cmd = [self.adb] + (["-s", serial] if serial else []) + args
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
            return p.stdout.strip(), p.stderr.strip(), p.returncode
        except subprocess.TimeoutExpired: return "", "Timeout", 1
        except Exception as e: return "", str(e), 1
    def devices(self):
        out, err, rc = self._run(["devices"]); 
        if rc != 0: return []
        devs = []
        for ln in out.splitlines()[1:]:
            pr = ln.strip().split()
            if len(pr)==2 and pr[1]=="device": devs.append(pr[0])
        return devs
    def getprop(self, serial, prop):
        out,_,rc = self._run(["shell","getprop",prop], serial)
        return out.strip() if rc==0 else ""
    def sdk_int(self, serial):
        try: return int(self.getprop(serial,"ro.build.version.sdk") or "0")
        except: return 0
    def device_props(self, serial):
        props = {}
        for k in ["ro.product.brand","ro.product.manufacturer","ro.product.model","ro.product.device"]:
            props[k] = self.getprop(serial, k).lower()
        return props
    def list_packages(self, serial):
        out_all,_,rc = self._run(["shell","pm","list","packages"], serial)
        if rc != 0: return []
        names = [x.split(":",1)[1] for x in out_all.splitlines() if x.startswith("package:")]
        out_sys,_,rc = self._run(["shell","pm","list","packages","-s"], serial)
        sysset=set()
        if rc==0: sysset={x.split(":",1)[1] for x in out_sys.splitlines() if x.startswith("package:")}
        return [{"name":n, "is_system": (n in sysset)} for n in names]
    def disable(self, s, p): return self._run(["shell","pm","disable-user","--user","0",p], s)
    def enable(self, s, p):  return self._run(["shell","pm","enable",p], s)
    def uninstall_user(self, s, p): return self._run(["shell","pm","uninstall","-k","--user","0",p], s)
    def install_existing(self, s, p): return self._run(["shell","cmd","package","install-existing","--user","0",p], s)
    def force_stop(self, s, p): return self._run(["shell","am","force-stop",p], s)
    def clear_data(self, s, p): return self._run(["shell","pm","clear",p], s)
    def install_apk(self, s, apk): return self._run(["install","-r",apk], s)
    def query_appops(self, s, op):
        out, err, rc = self._run(["shell","cmd","appops","query-op","--user","0",op], s)
        if rc!=0 or not out: out, err, rc = self._run(["shell","appops","query-op","--user","0",op], s)
        pkgs=[]
        for line in out.splitlines():
            m = re.search(r"package:\s*([a-zA-Z0-9._-]+)", line)
            if m: pkgs.append(m.group(1))
        return sorted(set(pkgs))
    def appops_set(self, s, pkg, op, mode):
        out, err, rc = self._run(["shell","cmd","appops","set",pkg,op,mode], s)
        if rc!=0: out, err, rc = self._run(["shell","appops","set",pkg,op,mode], s)
        return out, err, rc
    def get_private_dns(self, s):
        mode,spec="",""
        o1,_,r1 = self._run(["shell","settings","get","global","private_dns_mode"], s);  mode=(o1 or "").strip() if r1==0 else mode
        o2,_,r2 = self._run(["shell","settings","get","global","private_dns_specifier"], s); spec=(o2 or "").strip() if r2==0 else spec
        return mode, spec
    def set_private_dns(self, s, mode, spec=None):
        self._run(["shell","settings","put","global","private_dns_mode",mode], s)
        if spec is None:
            self._run(["shell","settings","delete","global","private_dns_specifier"], s)
        else:
            self._run(["shell","settings","put","global","private_dns_specifier",spec], s)
        return True

class BilalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VER}")
        self.geometry("1120x740"); self.minsize(980, 650)

        self.settings = load_settings()
        self.skin_name = self.settings.get("skin", "Bilal Green")
        self._init_style()

        self.adb = ADB(self.log_write)
        self.rules = RuleEngine()

        self.devices = []; self.serial = None
        self.props = {}; self.brand = "unknown"
        self.all_packages = []; self.detected_adlike = []
        self.backup = self._load_backup()

        self._build_header()
        self._build_ui()
        self.refresh_devices()

    def _init_style(self):
        try:
            self.style = ttk.Style(self); self.style.theme_use("clam")
        except Exception: pass
        pal = SKINS.get(self.skin_name, SKINS["Bilal Green"])
        self.style.configure("Header.TFrame", background=pal["primary"])
        self.style.configure("Header.TLabel", background=pal["primary"], foreground=pal["textOnPrimary"], font=("Segoe UI", 12, "bold"))
        self.style.configure("TButton", padding=4)

    def _build_header(self):
        self.header = ttk.Frame(self, style="Header.TFrame"); self.header.pack(fill="x")
        ttk.Label(self.header, text=f"Bilal Mobile Ad Blocker — Free Edition", style="Header.TLabel").pack(side="left", padx=12, pady=6)
        ttk.Button(self.header, text="Contact us on WhatsApp", command=self.open_whatsapp).pack(side="right", padx=10, pady=6)

    def open_whatsapp(self):
        try: webbrowser.open_new_tab(CONTACT_WA_URL)
        except Exception: messagebox.showinfo("WhatsApp", CONTACT_WA)

    def _build_ui(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=10, pady=8)
        ttk.Label(top, text="Device:").pack(side="left")
        self.var_device = tk.StringVar()
        self.cbo_device = ttk.Combobox(top, textvariable=self.var_device, width=40, state="readonly")
        self.cbo_device.pack(side="left", padx=6)
        ttk.Button(top, text="Refresh", command=self.refresh_devices).pack(side="left", padx=6)
        ttk.Button(top, text="Fetch Apps", command=self.fetch_apps).pack(side="left", padx=6)
        self.lbl_brand = ttk.Label(top, text="Brand: -"); self.lbl_brand.pack(side="left", padx=12)

        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=8, pady=6)
        self.tab_apps = ttk.Frame(nb); nb.add(self.tab_apps, text="Apps")
        self.tab_oneclick = ttk.Frame(nb); nb.add(self.tab_oneclick, text="One‑Click Block")
        self.tab_tools = ttk.Frame(nb); nb.add(self.tab_tools, text="Tools")
        self.tab_settings = ttk.Frame(nb); nb.add(self.tab_settings, text="Settings")
        self.tab_about = ttk.Frame(nb); nb.add(self.tab_about, text="About")

        topA = ttk.Frame(self.tab_apps); topA.pack(fill="x", padx=10, pady=6)
        ttk.Label(topA, text="Search:").pack(side="left")
        self.var_search = tk.StringVar()
        ent = ttk.Entry(topA, textvariable=self.var_search, width=40); ent.pack(side="left", padx=6)
        ent.bind("<KeyRelease>", lambda e: self.apply_filter())
        ttk.Button(topA, text="Refresh Detected", command=self.refresh_detected).pack(side="right", padx=6)
        ttk.Button(topA, text="Select All Detected", command=self.select_all_detected).pack(side="right")

        main = ttk.Frame(self.tab_apps); main.pack(fill="both", expand=True, padx=10, pady=6)
        left = ttk.Frame(main); left.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(main); right.pack(side="left", fill="both", expand=True, padx=(8,0))

        ttk.Label(left, text="Detected Ad‑like").pack(anchor="w")
        self.list_ad = tk.Listbox(left, selectmode="extended"); self.list_ad.pack(fill="both", expand=True, pady=4)
        ttk.Label(right, text="All Packages").pack(anchor="w")
        self.list_all = tk.Listbox(right, selectmode="extended"); self.list_all.pack(fill="both", expand=True, pady=4)

        actions = ttk.Frame(self.tab_apps); actions.pack(fill="x", padx=10, pady=8)
        ttk.Button(actions, text="Disable", command=lambda:self.do_selected("disable")).pack(side="left", padx=4)
        ttk.Button(actions, text="Enable", command=lambda:self.do_selected("enable")).pack(side="left", padx=4)
        ttk.Button(actions, text="Uninstall (user 0)", command=lambda:self.do_selected("uninstall_user")).pack(side="left", padx=4)
        ttk.Button(actions, text="Restore install‑existing", command=lambda:self.do_selected("restore")).pack(side="left", padx=4)
        ttk.Button(actions, text="Force‑Stop", command=lambda:self.do_selected("force_stop")).pack(side="left", padx=4)
        ttk.Button(actions, text="Clear App Data (⚠️)", command=lambda:self.do_selected("clear")).pack(side="left", padx=12)

        wrap = ttk.Frame(self.tab_oneclick); wrap.pack(fill="both", expand=True, padx=10, pady=10)
        self.var_mode = tk.StringVar(value="safe")
        rb = ttk.Frame(wrap); rb.pack(fill="x", pady=(0,6))
        ttk.Label(rb, text="Mode:").pack(side="left")
        ttk.Radiobutton(rb, text="Safe (recommended)", value="safe", variable=self.var_mode).pack(side="left", padx=6)
        ttk.Radiobutton(rb, text="Strict (more aggressive)", value="strict", variable=self.var_mode).pack(side="left", padx=6)
        self.var_uninstall = tk.BooleanVar(value=False)
        ttk.Checkbutton(wrap, text="In Strict, uninstall common bloat for user 0 (reversible)", variable=self.var_uninstall).pack(anchor="w")
        ttk.Button(wrap, text="One‑Click Clean Ads (All‑in‑One)", command=self.oneclick_clean, width=40).pack(anchor="w", pady=(6,8))
        ttk.Label(wrap, text="Safe: Disable + overlay & notifications + AdGuard DNS. Strict: extra targets + AdGuard Family + optional uninstall.", foreground="#2e7d32").pack(anchor="w", pady=(0,6))
        g = ttk.Frame(wrap); g.pack(fill="x", pady=8)
        for text, key in [("Xiaomi / Redmi / Poco","xiaomi"),("Tecno / Infinix / Itel / Sparx","tecno"),("Oppo / Realme / OnePlus","oppo"),("Vivo / iQOO","vivo"),("Samsung","samsung"),("Nothing","nothing")]:
            ttk.Button(g, text=text, command=lambda k=key:self.oneclick_brand_only(k)).pack(side="left", padx=6, pady=6)
        row = ttk.Frame(wrap); row.pack(fill="x", pady=8)
        ttk.Button(row, text="Set AdGuard Private DNS", command=lambda:self.quick_dns("dns.adguard.com")).pack(side="left", padx=4)
        ttk.Button(row, text="Reset Private DNS", command=lambda:self.quick_dns(None)).pack(side="left", padx=4)
        ttk.Button(row, text="Undo Last Clean", command=self.undo_oneclick).pack(side="left", padx=20)
        ttk.Label(wrap, text="All actions are reversible via Undo or Enable/Restore.", foreground="#555").pack(anchor="w", pady=6)

        tools = ttk.Frame(self.tab_tools); tools.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(tools, text="Backup / Restore").pack(anchor="w")
        r1 = ttk.Frame(tools); r1.pack(fill="x", pady=6)
        ttk.Button(r1, text="Backup Disabled List", command=self.backup_state).pack(side="left", padx=4)
        ttk.Button(r1, text="Restore from Backup", command=self.restore_from_backup).pack(side="left", padx=4)
        ttk.Button(r1, text="Export Backup JSON", command=self.export_backup).pack(side="left", padx=12)
        ttk.Button(r1, text="Import Backup JSON", command=self.import_backup).pack(side="left", padx=4)
        ttk.Separator(tools).pack(fill="x", pady=10)
        ttk.Label(tools, text="APK Tools").pack(anchor="w")
        r2 = ttk.Frame(tools); r2.pack(fill="x", pady=6)
        ttk.Button(r2, text="Install APK...", command=self.install_apk).pack(side="left", padx=4)

        sets = ttk.Frame(self.tab_settings); sets.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(sets, text="ADB Setup").pack(anchor="w")
        rowS = ttk.Frame(sets); rowS.pack(fill="x", pady=6)
        self.lbl_adb = ttk.Label(rowS, text=f"ADB Path: {getattr(self,'adb',None) and self.adb.adb or 'Not found'}"); self.lbl_adb.pack(side="left")
        ttk.Button(rowS, text="Download/Repair ADB", command=self.download_adb_clicked).pack(side="left", padx=10)
        ttk.Separator(sets).pack(fill="x", pady=10)
        ttk.Label(sets, text="Appearance (Skin)").pack(anchor="w")
        skin_row = ttk.Frame(sets); skin_row.pack(fill="x", pady=6)
        self.cbo_skin = ttk.Combobox(skin_row, values=list(SKINS.keys()), state="readonly", width=22)
        self.cbo_skin.set(self.settings.get("skin","Bilal Green")); self.cbo_skin.pack(side="left")
        ttk.Button(skin_row, text="Apply", command=lambda:self.apply_skin(self.cbo_skin.get())).pack(side="left", padx=8)
        ttk.Separator(sets).pack(fill="x", pady=10)
        ttk.Label(sets, text="Rules").pack(anchor="w")
        self.lbl_rules = ttk.Label(sets, text=f"Rules: {self.rules.version()}"); self.lbl_rules.pack(anchor="w", pady=(4,0))
        rr = ttk.Frame(sets); rr.pack(fill="x", pady=6)
        ttk.Button(rr, text="Update Rules (online)", command=self.update_rules_online).pack(side="left", padx=4)
        ttk.Separator(sets).pack(fill="x", pady=10)
        tips = "- USB debugging ON, RSA prompt allow\n- Prefer Disable (reversible). Uninstall for user 0 bhi restore hota hai.\n"
        tk.Message(sets, text=tips, width=800).pack(anchor="w")

        about = ttk.Frame(self.tab_about); about.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(about, text=f"{APP_NAME} v{APP_VER}").pack(anchor="w")
        ttk.Label(about, text="One‑Click Clean Ads removes OEM bloat/overlays safely via ADB. Free and non‑intrusive.").pack(anchor="w", pady=6)
        ttk.Label(about, text=f"Data folder: {APPDATA}").pack(anchor="w", pady=6)
        ttk.Separator(about).pack(fill="x", pady=10)
        info = ttk.Frame(about); info.pack(fill="x")
        ttk.Label(info, text=f"{CREDIT_TEXT}  •  WhatsApp: {CONTACT_WA}").pack(anchor="w")
        ttk.Button(info, text="Chat on WhatsApp", command=self.open_whatsapp).pack(anchor="w", pady=6)

        self._build_adbar_free()
        ttk.Label(self, text="Log").pack(anchor="w", padx=10)
        self.txt_log = tk.Text(self, height=10); self.txt_log.pack(fill="both", expand=False, padx=10, pady=(0,10))

    def _build_adbar_free(self):
        self.ad_wrap = ttk.Frame(self); self.ad_wrap.pack(fill="x", padx=10, pady=(0,6))
        left = ttk.Frame(self.ad_wrap); left.pack(side="left", fill="x", expand=True)
        self.ad_img = tk.Label(left, cursor="hand2"); self.ad_img.pack(side="left")
        self.ad_txt = ttk.Label(left, text="Sponsor", foreground="#666"); self.ad_txt.pack(side="left", padx=8)
        btns = ttk.Frame(self.ad_wrap); btns.pack(side="right")
        ttk.Button(btns, text="Hide", command=self._ad_hide_session).pack(side="left", padx=4)
        ttk.Button(btns, text="Mute 24h", command=self._ad_mute_day).pack(side="left", padx=4)
        self._ad_items = []; self._ad_idx = 0; self._ad_timer = None; self._ad_current_url = None
        if self._ad_is_muted():
            self.ad_wrap.forget(); return
        self._ad_load_config()

    def _ad_is_muted(self):
        try:
            with open(AD_MUTE_FILE,"r",encoding="utf-8") as f: obj=json.load(f)
            return time.time() < float(obj.get("until", 0))
        except Exception: return False

    def _ad_hide_session(self):
        try:
            if self._ad_timer: self.after_cancel(self._ad_timer)
        except Exception: pass
        self.ad_wrap.forget()

    def _ad_mute_day(self):
        try:
            with open(AD_MUTE_FILE,"w",encoding="utf-8") as f: json.dump({"until": time.time() + 24*3600}, f)
        except Exception: pass
        self._ad_hide_session()

    def _ad_load_config(self):
        def work():
            ok=False
            if AD_CONFIG_URL:
                try:
                    with urllib.request.urlopen(AD_CONFIG_URL, timeout=8) as r:
                        data = json.load(r); ok=True
                    items = data.get("items", [])
                    expanded=[]
                    for it in items:
                        w = max(1,int(it.get("weight",1)))
                        for _ in range(w): expanded.append(it)
                    random.shuffle(expanded)
                    self._ad_items = expanded or []
                    self._ad_refresh = int(data.get("refresh_sec",120))
                    self.log_write(f"Sponsor loaded ({len(items)} creatives).")
                except Exception as e:
                    self.log_write(f"Sponsor not available: {e}")
            if not ok:
                self._ad_items = [{
                    "id":"wa-fallback","title":"Need help? WhatsApp Bilal",
                    "image":"https://raw.githubusercontent.com/ak-templates/assets/main/wa-728x90-light.png",
                    "url": CONTACT_WA_URL, "weight":1
                }]
                self._ad_refresh = 180
            self._ad_render()
        self.run_bg(work)

    def _ad_photo_from_url(self, url):
        try:
            with urllib.request.urlopen(url, timeout=8) as r: raw=r.read()
            b64=base64.b64encode(raw).decode("ascii")
            return tk.PhotoImage(data=b64)
        except Exception as e:
            self.log_write(f"Ad image error: {e}"); return None

    def _ad_render(self):
        if not self._ad_items:
            self._ad_hide_session(); return
        it = self._ad_items[self._ad_idx % len(self._ad_items)]
        self._ad_current_url = it.get("url")
        self.ad_txt.config(text=it.get("title","Sponsor"))
        img = self._ad_photo_from_url(it.get("image"))
        if img: self._ad_img_ref=img; self.ad_img.config(image=self._ad_img_ref, text="")
        else:   self.ad_img.config(image="", text=it.get("title","Sponsor"))
        def open_link(_e=None):
            try: webbrowser.open_new_tab(self._ad_current_url)
            except Exception: pass
        self.ad_img.bind("<Button-1>", open_link); self.ad_txt.bind("<Button-1>", open_link)
        try:
            if self._ad_timer: self.after_cancel(self._ad_timer)
        except Exception: pass
        self._ad_timer = self.after(max(10,getattr(self,"_ad_refresh",120))*1000, self._ad_next)

    def _ad_next(self): self._ad_idx += 1; self._ad_render()

    def log_write(self, s):
        ts = time.strftime("[%H:%M:%S] "); 
        try:
            self.txt_log.insert("end", ts + s + "\n"); self.txt_log.see("end"); self.update_idletasks()
        except Exception: pass
        safe_write_log(s)

    def run_bg(self, target): threading.Thread(target=target, daemon=True).start()

    def refresh_devices(self):
        def work():
            if not self.adb.have_adb():
                self.log_write("ADB missing. Settings > Download/Repair ADB."); return
            devs = self.adb.devices()
            self.cbo_device["values"] = [d + " (online)" for d in devs]
            if devs:
                if not self.serial: self.serial = devs[0]
                self.var_device.set(self.serial + " (online)")
                self.props = self.adb.device_props(self.serial)
                self.brand = detect_brand(self.props)
                model = self.props.get("ro.product.model","")
                self.lbl_brand.config(text=f"Brand: {self.brand or '-'} | Model: {model or '-'}")
                self.log_write(f"Devices: {', '.join(devs)} | Brand: {self.brand} | Model: {model}")
            else:
                self.serial=None; self.var_device.set(""); self.lbl_brand.config(text="Brand: -")
                self.log_write("No device. Enable USB debugging + accept RSA.")
        def on_change(*a):
            v = self.var_device.get().split()
            if v:
                self.serial = v[0]
                self.props = self.adb.device_props(self.serial)
                self.brand = detect_brand(self.props)
                model = self.props.get("ro.product.model","")
                self.lbl_brand.config(text=f"Brand: {self.brand or '-'} | Model: {model or '-'}")
        self.var_device.trace_add("write", lambda *a:on_change())
        self.run_bg(work)

    def fetch_apps(self):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        def work():
            self.log_write("Fetching packages...")
            self.all_packages = self.adb.list_packages(self.serial)
            self.refresh_detected(); self.apply_filter()
            self.log_write(f"Found {len(self.all_packages)} packages. Detected {len(self.detected_adlike)} ad‑like.")
        self.run_bg(work)

    def refresh_detected(self):
        names = [p["name"] for p in self.all_packages]
        bl = set(BASE_BLACKLIST) | get_brand_blacklist(self.brand)
        detected = []
        for n in names:
            if n in WHITELIST: continue
            if n in bl or is_adlike(n): detected.append(n)
        self.detected_adlike = sorted(set(detected))
        try:
            self.list_ad.delete(0, "end")
            for n in self.detected_adlike: self.list_ad.insert("end", n)
        except Exception: pass

    def apply_filter(self):
        q = self.var_search.get().lower().strip()
        names = sorted([p["name"] for p in self.all_packages])
        if q: names = [n for n in names if q in n.lower()]
        try:
            self.list_all.delete(0, "end")
            for n in names: self.list_all.insert("end", n)
        except Exception: pass

    def selected_packages(self):
        sel = set()
        for i in self.list_ad.curselection(): sel.add(self.list_ad.get(i))
        for i in self.list_all.curselection(): sel.add(self.list_all.get(i))
        return sorted(sel)

    def do_selected(self, action):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        pkgs = self.selected_packages()
        if not pkgs: messagebox.showinfo("Select","Select one or more packages."); return
        if action == "clear":
            if not messagebox.askyesno("Warning","This will RESET data for selected apps. Continue?"): return
        def work():
            self.log_write(f"{action} on {len(pkgs)} package(s)...")
            for p in pkgs:
                if action == "disable": out, err, rc = self.adb.disable(self.serial, p); self._track_backup(p,"disabled",rc)
                elif action == "enable": out, err, rc = self.adb.enable(self.serial, p)
                elif action == "uninstall_user": out, err, rc = self.adb.uninstall_user(self.serial, p); self._track_backup(p,"uninstalled",rc)
                elif action == "restore": out, err, rc = self.adb.install_existing(self.serial, p)
                elif action == "force_stop": out, err, rc = self.adb.force_stop(self.serial, p)
                elif action == "clear": out, err, rc = self.adb.clear_data(self.serial, p)
                else: out, err, rc = "", f"Unknown {action}", 1
                if out: self.log_write(out)
                if err: self.log_write("ERR: " + err)
            self.log_write("Done.")
        self.run_bg(work)

    def _track_backup(self, pkg, key, rc):
        if rc != 0: return
        serial = self.serial or "unknown"
        dev = self.backup.setdefault(serial, {"disabled":[], "uninstalled":[], "oneclick":{}})
        if pkg not in dev[key]: dev[key].append(pkg)
        self._save_backup()

    def oneclick_brand_only(self, brand_key):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        if not self.all_packages: self.fetch_apps()
        installed = {p["name"] for p in self.all_packages}
        bl = set(get_brand_blacklist(brand_key)) | set(BASE_BLACKLIST)
        targets = sorted((bl & installed) - SAFE_EXCLUDE)
        if not targets: messagebox.showinfo("Info","No brand packages found."); return
        self.log_write(f"One‑Click brand disable: {len(targets)}"); self._bulk_disable(targets)

    def oneclick_clean(self):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        mode = self.var_mode.get(); strict = (mode=="strict"); use_uninstall = bool(self.var_uninstall.get() and strict)
        def work():
            if not self.all_packages:
                self.log_write("Fetching packages..."); self.all_packages = self.adb.list_packages(self.serial)
            installed = {p["name"] for p in self.all_packages}
            brand = self.brand; model = self.props.get("ro.product.model",""); device = self.props.get("ro.product.device","")
            self.log_write(f"Running One‑Click Clean | brand={brand} | mode={mode} | uninstall={use_uninstall}")

            sdk = self.adb.sdk_int(self.serial); dns_backup={}
            if sdk >= 28:
                m0,s0 = self.adb.get_private_dns(self.serial); dns_backup={"mode":m0 or "", "spec":s0 or ""}
                host = "dns-family.adguard.com" if strict else "dns.adguard.com"
                self.adb.set_private_dns(self.serial, "hostname", host)
                self.log_write(f"Private DNS set to {host}")
            else:
                self.log_write("Private DNS not supported on this Android (<9).")

            overlay_pkgs = self.adb.query_appops(self.serial, "SYSTEM_ALERT_WINDOW")
            suspects = [p for p in overlay_pkgs if not p.startswith("com.google.") and not p.startswith("com.android.") and p not in WHITELIST]
            overlay_changed, notif_changed, reqinst_changed = [], [], []
            for p in suspects:
                _,_,rc = self.adb.appops_set(self.serial, p, "SYSTEM_ALERT_WINDOW", "deny");   overlay_changed += [p] if rc==0 else []
                _,_,rc = self.adb.appops_set(self.serial, p, "POST_NOTIFICATION",   "ignore"); notif_changed  += [p] if rc==0 else []
                if strict:
                    _,_,rc = self.adb.appops_set(self.serial, p, "REQUEST_INSTALL_PACKAGES", "ignore"); reqinst_changed += [p] if rc==0 else []
            if overlay_changed: self.log_write(f"Overlay denied for {len(overlay_changed)} app(s).")
            if notif_changed:  self.log_write(f"Notifications blocked for {len(notif_changed)} app(s).")
            if reqinst_changed:self.log_write(f"Unknown-sources install blocked for {len(reqinst_changed)} app(s).")

            rule_targets = set(self.rules.targets(brand, model, device, installed, strict=strict))
            heuristic = {p for p in installed if is_adlike(p)}
            base = set(BASE_BLACKLIST) | get_brand_blacklist(brand)
            targets = sorted(((rule_targets | base | heuristic) & installed) - SAFE_EXCLUDE)

            disabled, uninstalled = [], []
            for p in targets:
                if use_uninstall and p in UNINSTALL_PREFERRED:
                    _,_,rc = self.adb.uninstall_user(self.serial, p)
                    if rc==0: uninstalled.append(p)
                else:
                    _,_,rc = self.adb.disable(self.serial, p)
                    if rc==0: disabled.append(p)
                self.adb.force_stop(self.serial, p)
            self.log_write(f"Disabled={len(disabled)}  Uninstalled(user0)={len(uninstalled)}")

            dev = self.backup.setdefault(self.serial, {"disabled":[], "uninstalled":[], "oneclick":{}})
            dev["oneclick"] = {"ts": int(time.time()), "brand": brand, "mode": mode, "disabled": disabled, "uninstalled": uninstalled,
                               "overlay_denied": overlay_changed, "notif_blocked": notif_changed, "reqinst_blocked": reqinst_changed, "dns_backup": dns_backup}
            self._save_backup()
            self.log_write("One‑Click Clean complete. Use Undo if needed.")
            self.refresh_detected()
        self.run_bg(work)

    def undo_oneclick(self):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        rec = (self.backup.get(self.serial) or {}).get("oneclick")
        if not rec: messagebox.showinfo("Undo","No one‑click record found for this device."); return
        def work():
            self.log_write("Undoing last One‑Click changes...")
            for p in rec.get("disabled", []): self.adb.enable(self.serial, p)
            for p in rec.get("uninstalled", []): self.adb.install_existing(self.serial, p)
            for p in rec.get("overlay_denied", []): self.adb.appops_set(self.serial, p, "SYSTEM_ALERT_WINDOW", "allow")
            for p in rec.get("notif_blocked", []):  self.adb.appops_set(self.serial, p, "POST_NOTIFICATION", "allow")
            for p in rec.get("reqinst_blocked", []):self.adb.appops_set(self.serial, p, "REQUEST_INSTALL_PACKAGES", "allow")
            dnsb = rec.get("dns_backup") or {}
            if dnsb:
                self.adb.set_private_dns(self.serial, dnsb.get("mode") or "opportunistic", dnsb.get("spec") or None)
                self.log_write("Private DNS restored.")
            self.log_write("Undo complete.")
        self.run_bg(work)

    def _bulk_disable(self, pkgs):
        def work():
            for p in pkgs:
                _,_,rc = self.adb.disable(self.serial, p)
                if rc==0: self._track_backup(p, "disabled", rc)
            self.log_write("Brand disable done."); self.refresh_detected()
        self.run_bg(work)

    def quick_dns(self, host=None):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        def work():
            if self.adb.sdk_int(self.serial) < 28:
                self.log_write("Private DNS not supported on this Android (<9)."); return
            if host:
                m0,s0 = self.adb.get_private_dns(self.serial)
                dev = self.backup.setdefault(self.serial, {"disabled":[], "uninstalled":[], "oneclick":{}})
                dev.setdefault("dns_manual_backup", {"mode":m0 or "", "spec":s0 or ""}); self._save_backup()
                self.adb.set_private_dns(self.serial, "hostname", host)
                self.log_write(f"Private DNS set to {host}")
            else:
                self.adb.set_private_dns(self.serial, "off", None); self.log_write("Private DNS turned off.")
        self.run_bg(work)

    def _load_backup(self):
        try:
            with open(BACKUP_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except Exception: return {}
    def _save_backup(self):
        try:
            with open(BACKUP_FILE,"w",encoding="utf-8") as f: json.dump(self.backup, f, indent=2)
        except Exception: pass

    def backup_state(self):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        def work():
            out, err, rc = self.adb._run(["shell","pm","list","packages","-d"], self.serial)
            disabled=[]
            if rc==0: disabled=[x.split(":",1)[1] for x in out.splitlines() if x.startswith("package:")]
            dev = self.backup.setdefault(self.serial, {"disabled":[], "uninstalled":[], "oneclick":{}})
            for p in disabled:
                if p not in dev["disabled"]: dev["disabled"].append(p)
            self._save_backup(); self.log_write(f"Backup saved. Disabled: {len(disabled)}")
        self.run_bg(work)

    def restore_from_backup(self):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        dev = self.backup.get(self.serial) or {}
        disabled = dev.get("disabled", []); uninstalled = dev.get("uninstalled", [])
        if not disabled and not uninstalled:
            messagebox.showinfo("Restore","No backup entries for this device."); return
        def work():
            self.log_write("Restoring from backup...")
            for p in disabled: self.adb.enable(self.serial, p)
            for p in uninstalled: self.adb.install_existing(self.serial, p)
            self.log_write("Restore complete.")
        self.run_bg(work)

    def export_backup(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")], initialfile="bilal_backup.json")
        if not path: return
        try:
            with open(path,"w",encoding="utf-8") as f: json.dump(self.backup, f, indent=2)
            self.log_write(f"Backup exported: {path}")
        except Exception as e: messagebox.showerror("Export", str(e))

    def import_backup(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f: data = json.load(f)
            self.backup.update(data); self._save_backup()
            self.log_write(f"Backup imported from {path}")
        except Exception as e: messagebox.showerror("Import", str(e))

    def install_apk(self):
        if not self.serial: messagebox.showwarning("Device","No device selected"); return
        apk = filedialog.askopenfilename(filetypes=[("APK files","*.apk")])
        if not apk: return
        def work():
            self.log_write(f"Installing {os.path.basename(apk)} ...")
            out, err, rc = self.adb.install_apk(self.serial, apk)
            if out: self.log_write(out)
            if err: self.log_write("ERR: " + err)
            self.log_write("Install done.")
        self.run_bg(work)

    def apply_skin(self, name: str):
        self.skin_name = name if name in SKINS else "Bilal Green"
        self.settings["skin"] = self.skin_name; save_settings(self.settings)
        self._init_style()
        try: self.header.destroy()
        except Exception: pass
        self._build_header()

    def update_rules_online(self):
        ok = self.rules.load_remote()
        self.lbl_rules.config(text=f"Rules: {self.rules.version()}{' (online)' if ok else ' (local/offline)'}")
        self.log_write("Rules updated." if ok else "Online rules fetch failed, using local.")

    def download_adb_clicked(self):
        pb = tk.Toplevel(self); pb.title("Downloading ADB...")
        ttk.Label(pb, text="Downloading platform-tools from Google...").pack(padx=20, pady=10)
        pbar = ttk.Progressbar(pb, orient="horizontal", mode="determinate", length=360); pbar.pack(padx=20, pady=10)
        ttk.Label(pb, text="Please wait...").pack(padx=20, pady=(0,10))
        pb.resizable(False, False); pb.grab_set()
        def progress(v): 
            try: pbar["value"] = v; pb.update_idletasks()
            except Exception: pass
        def work():
            ok = self.adb.download_platform_tools(progress); pb.destroy()
            if ok:
                self.lbl_adb.config(text=f"ADB Path: {self.adb.adb}"); self.log_write("ADB ready."); self.refresh_devices()
            else: messagebox.showerror("ADB","Download failed.")
        self.run_bg(work)

if __name__ == "__main__":
    app = BilalApp()
    app.mainloop()
