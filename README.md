**Opis**<br/>
Kontener do wykrywania tekstu w plikach PDF z wykorzystaniem tesseract-ocr.<br/>
<br/>
**Build**<br/>
```
docker build -t ocrmypdf-container .
docker-compose up -d
```
**Przygotowanie**<br/>
Struktura katalogów wykorzystywana przez program:<br/>
```
~/ocr
~/ocr/done
~/ocr/error
~/ocr/input
~/ocr/output
```
**Użycie**<br/>
Wgraj pliki PDF do katalogu input<br/>
Poczekaj, aż program przetworzy pliki<br/>
Przetworzone pliki zostaną zapisane w katalogu output<br/>
Oryginalne pliki zostaną przeniesione do katalogów done lub error w przypadku powodzenia lub problemu z przetworzeniem
