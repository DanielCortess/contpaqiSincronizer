import json
import os
import shutil
import sys
import threading
from pathlib import Path

import servicemanager
import win32event
import win32service
import win32serviceutil

from APP.SyncContpaqController import SyncContpaqController


def _get_runtime_base_path():
    # En PyInstaller one-file, __file__ apunta al directorio temporal de extraccion.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _load_runtime_config():
    """
    Modo proyecto: usa Src/conf.json y SQLite relativo al proyecto.
    Modo EXE: usa ProgramData/SincronizadorContpaqi/conf.json y SQLite en ProgramData.
    """
    runtime_base = _get_runtime_base_path()

    if getattr(sys, "frozen", False):
        program_data = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "SincronizadorContpaqi"
        program_data.mkdir(parents=True, exist_ok=True)

        config_path = program_data / "conf.json"
        template_config = runtime_base / "conf.json"

        if not config_path.exists():
            if not template_config.exists():
                raise Exception(f"No se encontró conf.json en ProgramData ni en la carpeta del ejecutable: {runtime_base}")
            shutil.copy2(template_config, config_path)

        with config_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)

        if not isinstance(config, dict):
            raise Exception("El archivo conf.json no contiene un objeto JSON válido")

        sql_cfg = config.get("SQLLITE") or {}
        db_cfg = sql_cfg.get("DBPATH", "./LocalDB/SQLLITESincronizadorContpaqi.db")
        db_name = Path(db_cfg).name if Path(db_cfg).name else "SQLLITESincronizadorContpaqi.db"
        db_path = program_data / "LocalDB" / db_name

        sql_cfg["DBPATH"] = str(db_path)
        sql_cfg["BASEPATH"] = str(program_data)
        config["SQLLITE"] = sql_cfg

        # Persistir configuración efectiva en ProgramData para soporte y trazabilidad.
        with config_path.open("w", encoding="utf-8") as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)

        return config

    # Modo proyecto (no frozen)
    config_path = runtime_base / "conf.json"
    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    if not isinstance(config, dict):
        raise Exception("El archivo conf.json no contiene un objeto JSON válido")

    sql_cfg = config.get("SQLLITE") or {}
    db_path = sql_cfg.get("DBPATH")
    if db_path and not Path(db_path).is_absolute():
        sql_cfg["BASEPATH"] = str(config_path.parent)
        config["SQLLITE"] = sql_cfg

    return config


class SyncContpaqWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SincronizadorContpaqiService"
    _svc_display_name_ = "Sincronizador Contpaqi"
    _svc_description_ = "Sincroniza datos entre Netvy y Contpaqi."

    def __init__(self, args):
        super().__init__(args)
        self.h_wait_stop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_event = threading.Event()
        self.worker_thread = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop_event.set()
        win32event.SetEvent(self.h_wait_stop)

        # Espera razonable para detener el ciclo de sincronizacion.
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=30)

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("Sincronizador Contpaqi service started")
        self.worker_thread = threading.Thread(target=self._run_controller, daemon=True)
        self.worker_thread.start()

        win32event.WaitForSingleObject(self.h_wait_stop, win32event.INFINITE)
        servicemanager.LogInfoMsg("Sincronizador Contpaqi service stopped")

    def _run_controller(self):
        try:
            config = _load_runtime_config()

            controller = SyncContpaqController(config)
            controller.run(stop_event=self.stop_event)
        except Exception as ex:
            servicemanager.LogErrorMsg(f"Sincronizador Contpaqi crashed: {ex}")
            self.stop_event.set()
            win32event.SetEvent(self.h_wait_stop)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "debug":
        # Modo debug: ejecutar directamente en el hilo principal para que
        # Ctrl+C (SIGINT) sea capturado correctamente por Python y detenga el proceso.
        print("[INFO] Iniciando en modo debug. Presiona Ctrl+C para detener.")
        _stop = threading.Event()
        try:
            _config = _load_runtime_config()
            _controller = SyncContpaqController(_config)
            _controller.run(stop_event=_stop)
        except KeyboardInterrupt:
            _stop.set()
            print("\n[INFO] Detenido por Ctrl+C.")
        except Exception as _ex:
            print(f"[ERROR] Error crítico: {_ex}")
            sys.exit(1)
    elif len(sys.argv) == 1:
        # En ejecutable congelado (PyInstaller), cuando SCM arranca el servicio
        # no hay argumentos CLI y se debe inicializar explícitamente el dispatcher.
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(SyncContpaqWindowsService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as _ex:
            try:
                servicemanager.LogErrorMsg(f"SincronizadorContpaqi StartServiceCtrlDispatcher error: {_ex}")
            except Exception:
                pass
            sys.exit(1)
    else:
        # Modo servicio/comandos (install, start, stop, remove, etc.)
        # Debe pasar por pywin32 para registrarse con el SCM de Windows.
        win32serviceutil.HandleCommandLine(SyncContpaqWindowsService)
