Remove-Item .\dist\AP* -Recurse
pyinstaller --onefile --windowed --log-level WARN apTracking.py
Compress-Archive .\dist\* .\dist\APTracking_Win64.zip -Force