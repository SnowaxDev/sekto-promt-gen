.PHONY: install run ui prompt gen board
install:
	pip install -r requirements.txt
run:
	uvicorn seknuto_forge.api:app --reload --host 127.0.0.1 --port 8000
ui:
	python -c "import webbrowser; webbrowser.open('http://127.0.0.1:8000')"
prompt:
	python -m seknuto_forge.cli prompt --format A3 --mode B_sluzby
board:
	python -m seknuto_forge.cli leaderboard
