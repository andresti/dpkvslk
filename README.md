# Dokumendi-Põhine Küsimus-Vastus Süsteem Lokaalseks Kasutuseks (dpkvslk)

## Teenuse ülesseadmine
* Klooni projekti repositoorium
* Ülesseadmiseks jooksuta `make setup` (olenevalt dockeri seadistusest võib-olla vajalik jooksutada administraatorina, `sudo make setup`) - see tõmbab vajalikud mudelid ja ehitab dockeri konteineri. Jooksutamine võtab mõned minutid aega.
* käivitamiseks `make up` (või `sudo make up`)
* Teenus jookseb masinas aadressil `http://localhost:5001`

## Kasutamine
* Peale teenuse käivitamist saab teenust kasutada veebiliidese kaudu, avades brauseris aadressi `http://localhost:5001`.
* Vaikimisi on kasutatavaks dokumendiks VLA 2025 avalik raport
* Küsimusi saab esitada ka API kaudu, tehes päringu nt: `curl -X POST http://localhost:5001/api/ask --data-urlencode "question=What are the main goals of Russia?"`
