# asr-assisted-transcription

per ogni audio abbiamo:
	*FS-01	*FS-02

	*WA-01	*WA-02

	    *Gold

(nel caso dello Straparla abbiamo due Gold. Gold-FS, Gold-WA)

Research Questions:
1. numero di token trascritti
	1. proviamo a isolare solo i token linguistici (togliamo shortpauses e token metalinguistici)
2. il numero di minuti trascritti

3. Quanto si somigliano le due trascrizioni FS/WA? In termini di:
   1. il numero di unità di trascrizione
      1. proviamo ad escludere le unità che contengono solo token metalinguistici
   2. la durata media in ms delle unità di trascrizione
      1. proviamo ad escludere le unità che contengono solo token metalinguistici
   3. la durata media in ms delle unità di trascrizione
      1. proviamo ad escludere le unità che contengono solo token metalinguistici
   4. numero di span con overlap
   5. numero di span con pace variato
   6. numero di token con pattern intonativo
   7. numero di span con volume variato
   8. numero di token con allungamenti

4. Calcoliamo Delta-s(Gold, FS), Delta-w(Gold, WA) su:
   1. il numero di unità di trascrizione varia tra fase FS e fase WA?
      1. proviamo ad escludere le unità che contengono solo token metalinguistici
   2. la durata media in ms delle unità di trascrizione varia tra fase FS e fase WA?
      1. proviamo ad escludere le unità che contengono solo token metalinguistici
   3. la durata media in ms delle unità di trascrizione varia tra fase FS e fase WA?
      1. proviamo ad escludere le unità che contengono solo token metalinguistici
   4. numero di span con overlap
   5. numero di span con pace variato
   6. numero di token con pattern intonativo
   7. numero di span con volume variato
   8. numero di token con allungamenti

5. MISMATCH (per esperti e per non esperti) sul livello ortografico
   1. numero di token che mismatchano nelle due condizioni (FS e WA):
      1. li classifichiamo a mano (es. quante congiunzioni? quanti filler? quante shortpauses?...)
      2. valutazione "gravità" del mismatch (presenza/assenza di un token, stesso lemma, token diversi...)
      3. edit distance tra i token mismatchanti per valutare se ci sono typos (es. "parlare" vs "prlare")

6. MATCH
   1. calcolo accuracy (e per l'overlap che è di tipo relazionale UAS-LAS (Unlabeled attachment score e labeled attachment score)) per ogni feature jefferson: differenza tra accuratezza dell'annotatore FS rispetto al Gold e accuratezza dell'annotatore WA rispetto al gold.
   2. media delle accuratezze per file e media delle accuratezze per feature
   3. per i token che matchano a inizio e fine di unità di trascrizione, valutazione della precisione di inizio/fine unità di trascrizione (non si può fare in termini di accuracy perché sono numeri reali)
   4. Relazioni tra tipi di mismatch per le features. Ci sono features che sono più predittive di altre, sulla possibilità che esistano mismatch in altre colonne? Per esempio: avere una bassa accuratezza sui prolungamenti è predittivo rispetto ad avere una bassa accuratezza sul volume della voce?

7. valutazione precisione unità a prescindere dal contenuto
   1. Creazione grafo di corrispondenza delle unità attribuite ad ogni parlante per i vari annotatori.


Extra:
* Aggiungere gold dello straparla ex machina
* Usare gold paralleli per confronto
* Revisione gold qualitativa?
* Correlazione probabilità whisper con correzione errore da parte del revisore
* Trasformazione mismatch in 0/1
* Riorganizzazione parametri relazionali in due colonne
* backchannel identification (vedi dingemanse)
[* Per almeno uno tra ParlaBOA e PastiA, vorremmo avere il Gold della fase 01 e il gold della fase 02 da confrontare con il gold già esistente.]