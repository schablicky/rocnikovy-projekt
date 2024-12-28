![Version](https://img.shields.io/badge/Verze-Alpha_0.1-green.svg?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMTIgMTIgNDAgNDAiPjxwYXRoIGZpbGw9IiMzMzMzMzMiIGQ9Ik0zMiwxMy40Yy0xMC41LDAtMTksOC41LTE5LDE5YzAsOC40LDUuNSwxNS41LDEzLDE4YzEsMC4yLDEuMy0wLjQsMS4zLTAuOWMwLTAuNSwwLTEuNywwLTMuMiBjLTUuMywxLjEtNi40LTIuNi02LjQtMi42QzIwLDQxLjYsMTguOCw0MSwxOC44LDQxYy0xLjctMS4yLDAuMS0xLjEsMC4xLTEuMWMxLjksMC4xLDIuOSwyLDIuOSwyYzEuNywyLjksNC41LDIuMSw1LjUsMS42IGMwLjItMS4yLDAuNy0yLjEsMS4yLTIuNmMtNC4yLTAuNS04LjctMi4xLTguNy05LjRjMC0yLjEsMC43LTMuNywyLTUuMWMtMC4yLTAuNS0wLjgtMi40LDAuMi01YzAsMCwxLjYtMC41LDUuMiwyIGMxLjUtMC40LDMuMS0wLjcsNC44LTAuN2MxLjYsMCwzLjMsMC4yLDQuNywwLjdjMy42LTIuNCw1LjItMiw1LjItMmMxLDIuNiwwLjQsNC42LDAuMiw1YzEuMiwxLjMsMiwzLDIsNS4xYzAsNy4zLTQuNSw4LjktOC43LDkuNCBjMC43LDAuNiwxLjMsMS43LDEuMywzLjVjMCwyLjYsMCw0LjYsMCw1LjJjMCwwLjUsMC40LDEuMSwxLjMsMC45YzcuNS0yLjYsMTMtOS43LDEzLTE4LjFDNTEsMjEuOSw0Mi41LDEzLjQsMzIsMTMuNHoiLz48L3N2Zz4%3D)
[![Developer](https://img.shields.io/badge/Developer-Tomáš_Schablický-red)](https://github.com/schablicky)
[![Developer](https://img.shields.io/badge/Developer-Matěj_Zimmer-pink)](https://github.com/matejzimmer)
[![Framework](https://img.shields.io/badge/Framework-Django-green)](https://www.djangoproject.com)
[![Framework](https://img.shields.io/badge/Framework-TensorFlow-orange)](https://www.tensorflow.org/)
[![Database](https://img.shields.io/badge/Datab%C3%A1ze-X-blue)](https://www.postgresql.org)
[![Frontend](https://img.shields.io/badge/Frontend-Tailwind_CSS-purple)](https://tailwindcss.com/)
## Popis projektu

Naše webová aplikace je určena k podpoře nebo plně automatizovanému obchodování na forexových trzích. Využíváme metody posilovaného učení (reinforcement learning), kde systém zlepšuje svá rozhodnutí na základě výsledků svých předchozích akcí.

Hlavní rysy aplikace:
- **Automatizované obchodování**: AI model na základě dat analyzuje a rozhoduje, kdy vstoupit do obchodu a kdy ho ukončit. Možnost plně automatizovaného režimu bez zásahu uživatele.
- **Manuální obchodování**: Uživatelé mají možnost sami rozhodovat o obchodech přímo z webového rozhraní.
- **Copy trading**: Uživatelé mohou automaticky kopírovat rozhodnutí a obchody jiných uživatelů.
- **Demo účet**: Pro uživatele je k dispozici možnost obchodovat s virtuálními penězi bez rizika.

## Hlavní funkcionality

### 1. AI Model
- **Framework**: TensorFlow
- **Enviromenty**: Vytvoření vlastního prostředí pro simulaci obchodování.
- **API integrace**: Pravidelný sběr tržních dat (např. každou minutu) pro trénink a predikce.

### 2. Vizualizace a zpracování dat
- **Grafy**: Vizualizace hodnot, jako je vývoj měn, efektivita AI modelu a obchodní statistiky.
- **Zoom**: Interaktivní grafy umožňující přiblížení pro detailní analýzu.
- **Databáze**: Ukládání tržních dat a rozhodnutí modelu pro další analýzu.

### 3. Webové rozhraní
- **Statistiky a doporučení**: Přehledné zobrazení AI doporučení a výkonu.
- **Aktuality**: Sekce pro zprávy a události z finančního světa.
- **Přihlášení**: Možnost přihlášení pomocí účtů Google nebo GitHub.
- **Žebříček**: Zobrazení úspěchů uživatelů a jejich dosažených profitů.
- **Zprávy mezi uživateli**: Uživatelé mohou mezi sebou komunikovat přímo na platformě.

### 4. Možnosti obchodování
- **Automatizované obchodování**: Akce prováděné modelem AI bez zásahu uživatele.
- **Manuální obchodování**: Uživatelé mohou spravovat obchody ručně podle vlastních strategií.
- **Copy trading**: Automatické kopírování obchodních rozhodnutí jiných uživatelů.

### 5. Demo účet
- **Virtuální měna**: Uživatelé mohou vyzkoušet platformu bez rizika pomocí nerealných prostředků.

## Dataset a integrace API
- **Reálná data**: Získávání dat z trhu pomocí MetaAPI pro trénink a obchodování v reálném čase.
- **Uchování dat**: Data jsou ukládána do databáze pro analýzu, vizualizaci a další použití.

## Použité technologie
- **Frontend**: Tailwind CSS
- **Backend**: Python, Django
- **AI Frameworky**: TensorFlow
- **Databáze**: ?
- **API**: Integrace s MetaAPI nebo jinými poskytovateli tržních dat.

## TO-DO list
- [x] Možnost provést obchod
- [x] Vidět své otevřené obchody
- [x] Uzavřít své otevřené obchody
- [x] Zprávy
- [ ] Chat mezi uživateli
- [ ] CopyTrading
- [ ] AI
- [x] Uživatelské nastavení
- [ ] Graf s vývojem ceny
- [ ] Social login
- [ ] Žebříček