# 📖 ABIDE Bible Study API

A FastAPI-powered spiritual API for studying Bible verses, exploring topics, emotions, and daily devotionals.

## 🔧 Features

- `/study` – Get Bible verse(s) with related verses.
- `/ask` – Ask questions by emotion or topic (e.g. "I feel afraid", "How to build faith").
- `/topics` – View all supported spiritual topics.
- `/devotional` – Get today’s devotional from `devotional.json`.

## 🗂️ Structure

- `app/` – Main API code
- `bot.py` – Telegram bot script
- `data/` – JSON files for Bible, topics, emotions, devotionals

## ▶️ Run Locally

```bash
uvicorn app.main:app --reload
