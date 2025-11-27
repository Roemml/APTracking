Remove-Item .\dist\AP* -Recurse
pyinstaller --onefile --windowed --log-level WARN APTracking.py
Compress-Archive .\dist\APTracking.exe .\dist\APTracking_Win64.zip -Force