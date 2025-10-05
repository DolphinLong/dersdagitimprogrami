#!/usr/bin/env python3
"""
Class Scheduling Program - Main Application Entry Point
"""

import sys
import os
import argparse
import logging

# ---------- 1️⃣ PYTHON PATH ----------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ---------- 2️⃣ IMPORTS ----------
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, Qt
from ui.main_window import MainWindow
from utils.helpers import setup_logging

# ---------- 3️⃣ LOGGING ----------
def _setup_logger(debug: bool):
    """
    Basit bir logger ayarı.  
    `debug=True` ise DEBUG seviyesini açar.
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger()
    return logger

# ---------- 4️⃣ MAIN ----------
def main():
    # ---- CLI options ----
    parser = argparse.ArgumentParser(description="Class Scheduling Program")
    parser.add_argument(
        "--debug", action="store_true", help="Run in debug mode (verbose logs)"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="Set application language code (e.g., 'tr', 'en')",
    )
    args = parser.parse_args()

    # ---- Logger ----
    logger = _setup_logger(args.debug)
    logger.info("Starting Class Scheduling Program...")

    # ---- Setup logging from helpers (if any) ----
    setup_logging()  # your existing helper may override or add handlers

    # ---- Qt Application ----
    app = QApplication(sys.argv)
    app.setApplicationName("Class Scheduling Program")
    app.setApplicationVersion("1.0.0")

    # ---- Language/Translator ----
    if args.lang:
        translator = QTranslator()
        translation_file = f"i18n_{args.lang}.qm"
        if translator.load(translation_file, os.path.join(os.getcwd(), "translations")):
            app.installTranslator(translator)
            logger.info(f"Loaded language: {args.lang}")
        else:
            logger.warning(
                f"Could not load translation file '{translation_file}'. Falling back to default."
            )
    else:
        # Auto‑detect system locale
        locale = QLocale.system().name()
        translator = QTranslator()
        if translator.load(f"i18n_{locale}.qm", os.path.join(os.getcwd(), "translations")):
            app.installTranslator(translator)
            logger.info(f"Auto‑loaded language: {locale}")

    # ---- Main Window ----
    try:
        window = MainWindow()
        window.show()
        logger.info("Application window created and shown")
    except Exception as e:
        logger.exception("Failed to create/show main window")
        sys.exit(1)

    # ---- Event Loop ----
    result = app.exec_()
    logger.info(f"Application exited with code: {result}")
    sys.exit(result)

if __name__ == "__main__":
    main()
