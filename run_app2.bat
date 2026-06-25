@echo off
echo Starting dashboard...

"C:\ProgramData\anaconda3\Scripts\streamlit.exe" run dashboard.py --server.port 8502

pause
