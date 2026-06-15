# Opis projektu
Projekt polegał na zaprojektowaniu komputerowej gry logicznej typu Wisielec. Aplikacja została zrealizowana w języku Python, ze szczególnym uwzględnieniem autorskiej oprawy graficznej.

## Funkcjonalności projektu

W ramach projektu zrealizowano następujące aspekty:

* **Zintegrowana baza haseł**: Przygotowano moduł obsługi bazy słów, w której hasła podzielone zostały według kategorii oraz trzech poziomów trudności (łatwy, średni, trudny).
  
* **Wizualna prezentacja zasad gry**: Opracowano pełną logikę rozgrywki opartą na klasycznym limicie prób. Kolejne niepoprawne wybory liter są obrazowane za pomocą kolejnych etapów rysunku wisielca.
* **Moduł statystyk**: Wprowadzono system zliczania i prezentowania statystyk aktualnej rozgrywki. Aplikacja gromadzi dane o liczbie wygranych oraz przegranych gier, umożliwiając wgląd w wyniki.
* **Zapis i odczyt stanu**: Dodano mechanizm zapisu i odczytu danych z pliku, który pozwala na bezpieczne zachowanie aktualnego stanu rozgrywki w dowolnym momencie. Użytkownik ma możliwość przerwania gry i jej wznowienia po ponownym uruchomieniu programu.
* **Funkcjonalność dodatkowa**: Jako dodatkową funkcjonalność zaproponowaną przez grupę, do aplikacji wprowadzono autorskie animacje umilające grę, które również natychmiastowo sygnalizują poprawne i błędne próby użytkownika.

## Zasady gry

Rozgrywka polega na odgadywaniu ukrytego hasła poprzez stopniowe wskazywanie pojedynczych liter. 

* **Przygotowanie**: Komputer losuje słowo z bazy danych i wyświetla na ekranie poziomą linię kresek – każda kreska oznacza jedną ukrytą literę.
* **Zgadywanie**: Gracz podaje pojedyncze litery. Jeśli wskazana litera znajduje się w haśle, program wpisuje ją w odpowiednie miejsca (może być ich więcej niż jedna w słowie).
* **Błędy i rysunek**: Jeśli podanej litery nie ma w słowie, program dorysowuje jeden element do postaci wisielca. Maksymalna liczba błędów w grze wynosi dokładnie 6 - głowa, tułów ręce i nogi.


# Potrzebne biblioteki
* PySide6
* csv
* random
