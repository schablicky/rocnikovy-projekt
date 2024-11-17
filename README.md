# Ročníkový projekt - Trading bot(Sigma Trader)
## Popis
Naše webová aplikace slouží k podpoře nebo plně automatizovanému obchodování na forexových trzích, využívajíc metody posilovaného učení (reinforcement learning). Systém se učí na základě svých vlastních akcí a jejich následného úspěchu či neúspěchu, čímž postupně zlepšuje svá rozhodnutí.

Díky API, které nám umožňuje pravidelně získávat data z trhu, ideálně každou minutu, můžeme tuto umělou inteligenci trénovat. TensorFlow funguje na bázi kroků (steps), takže sběr dat v pravidelných intervalech je pro trénink modelu optimální.

Tržní data budou ukládána do databáze, kde je následně využijeme pro zobrazení ve webovém rozhraní, což zvýší přehlednost a uživatelskou přívětivost. Rozhodnutí učiněná modelem budou rovněž archivována a vizualizována na webu, aby uživatelé lépe pochopili jeho fungování. Na stránkách nebudou chybět ani grafy, které názorně znázorní vývoj a efektivitu modelu.

Model bude buď poskytovat doporučení, kdy vstoupit do obchodu a kdy ho ukončit, nebo může být nastaven tak, aby prováděl tyto akce zcela automaticky, bez nutnosti zásahu uživatele.

## Dataset
1. Kde získat realtime training data? (zdarma) (MetaAPI?)
2. Jak je uchovat a zpracovat?

## AI model
1. Výběr frameworku (favorit: OpenAI gym)
2. Využití enviromentu AnyTrading nebo vytvoření zcela vlastního (možno pouze u OpenAI gym)
1. Výběr frameworku (favorit: TensorFlow)
2. Vytvoření zcela vlastního enviromentu

## Využití výsledků v praxi
1. Zobrazení na webové stránce (doporučení obchodu? + statistiky)
2. Automatické provedení akcí podle rozhodnutí modelu? (je možné pomocí MetaAPI)
![image](https://github.com/user-attachments/assets/926f4b7f-1f79-4ff8-8242-18b28fed8c04)
