1. I - zaczytanie inputów do bazy danych. Inputy muszą być w folderze inputs, muszą być odpowiednio nazwane.
Dane z table3 zaczytuje się osobno ręcznie. Można zaciągnąc albo pojedynczy input albo wszystkie razem.
Zaciągnięcie wszystkich inputów trwa około 1 minuty.

2. M - przeliczenie modelu i zapisanie go jako csv. Model przelicza się około 30 sekund, zapisuje wyniki zarówno
w bazie danych w tabeli results jak i jako csv w folderze outputs. Model trzeba przeliczyć zawsze, gdy zmieni sie input
lub parametry w pliku variables.

3. V - wyliczenie wolumenów elastyczności. Ta operacja bazuje na tabelach: table3, input5a, input5b oraz results.
Jeżeli zmieni się któryś z inputów, bądź w tabeli results zmieni się lista produktów lub ich przypisanie do roli, wtedy
należy wyliczyć jeszcze raz wolumeny elastyczności. Operacja ta działa na wszystkich procesorach, więc żeby nie zajęła
zbyt dużo czasu najlepiej zakończyć inne procesy na komputerze. Na dobrym sprzęcie trwa ok 8 minut. Rezultatem jest
utworzenie tabeli elast_vol w bazie danych.

4. E - wyliczenie całego modelu wraz z elastycznościa. Na podstawie tabeli results oraz elast_vol wyliczana jest
sprzedaż oraz marża po uwzględnieniu elastyczności - w bazie danych powstaje tabela elasticity a wyniki zapisują się
w folderze outputs. Przeliczenie jest bardzo szybkie, trwa około 10 sekund.