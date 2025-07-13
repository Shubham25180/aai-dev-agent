Start-Process powershell -ArgumentList @"
    cd \"$PWD\"
    if (Test-Path .venv\Scripts\Activate.ps1) { . .venv\Scripts\Activate.ps1 }
    if (Test-Path requirements.txt) { pip install -r requirements.txt }
    if (Test-Path main.py) { python main.py }
    # Uncomment below to use FastAPI/uvicorn instead of main.py
    # uvicorn api:app --reload
"@

Start-Process powershell -ArgumentList @"
    cd \"$PWD\frontend\"
    if (Test-Path package.json) { npm install }
    npm run dev
"@ 