# Kodi clone backup (aco730, privat)

Clona completa a setup-ului Kodi curent, instalabila pe orice device nou printr-un
singur addon tip "wizard" cu bife — fara sa tastezi vreun URL.

**Repo privat** — contine credentiale reale (parola/cookie DigiOnline, parola web
server Kodi, RealDebrid/Trakt/resolvere din TheCrew si prietenii, login YouTube).
Nu-l face public si nu distribui link-uri din el.

## Instalare pe un device nou (Kodi 20/21)

### Pasul 1 — singurul pas manual: instaleaza wizard-ul

1. Genereaza un **GitHub Personal Access Token**: github.com -> Settings ->
   Developer settings -> Personal access tokens -> Fine-grained -> acces doar la
   repo-ul `kodi-clone-backup`, permisiune **Contents: Read-only**.
2. Descarca (autentificat pe github.com, contul aco730) fisierul:
   `repository/addons/script.aco730restore/script.aco730restore-2.0.0.zip`
3. Pune-l pe un stick USB sau in Downloads pe device-ul Kodi nou.
4. In Kodi: **Add-ons -> Install from zip file** -> selecteaza fisierul.

Asta e singurul zip pe care il atingi manual. Tot restul se face din telecomanda.

### Pasul 2 — ruleaza wizard-ul

1. Add-ons -> Program add-ons -> **aco730 Setup Wizard** -> Run.
2. Prima data iti cere tokenul de la pasul 1 — il lipesti o singura data (se
   salveaza pe device-ul respectiv).
3. Apare o lista cu bife (toate pre-bifate) — debifeaza ce nu vrei:
   - Setarile mele personale (guisettings, credentiale, cookie-uri)
   - DigiOnline.ro
   - Stiri RSS
   - Weather (Gismeteo) + dependinte
   - Skin Confluence (varianta mea, meniu/fundal custom)
   - TheCrew + Cumination + MadTitanSports + POV (live, auto-update real)
4. Confirma — wizard-ul descarca si instaleaza automat tot ce ai bifat, direct
   din repo (fara sa navighezi vreun URL, fara File Manager).
5. **Restarteaza Kodi** la final.
6. Settings -> Interface -> Skin -> **Confluence** (daca ai instalat skin-ul).

## De ce TheCrew/Cumination/MadTitan/POV nu sunt copiate static

Au propriile surse live (thecrewwh/zips, Gujal00/smrzips, unhingedthemes/zips,
etc. — vezi `repository.thecrew`'s addon.xml). Wizard-ul instaleaza doar
pointer-ul mic `repository.thecrew`, apoi cere lui Kodi sa instaleze cele 4
addon-uri **de la sursa reala**, ca sa primesti update-uri reale, nu o versiune
inghetata. Setarile lor (RealDebrid, Trakt, resolvere) sunt deja restaurate din
`userdata-backup.zip`, deci nu trebuie sa te loghezi din nou nicaieri.

**YouTube** ramane instalat separat (din sursa lui reala/official repo) — wizard-ul
nu ii copiaza codul, dar credentialele (`access_manager.json`, `api_keys.json`,
`settings.xml`) sunt in backup si se aplica automat cand rulezi wizard-ul.

## Ce NU se cloneaza (hardware-specific, seteaza manual pe fiecare device)

- Rezolutie ecran / refresh rate
- Dispozitiv audio (HDMI/optic/etc) si passthrough
- Calibrare ecran

## Structura repo

```
repository/           <- addons.xml + zips (DigiOnline, Stiri RSS, weather+deps,
                          skin custom, repository.thecrew, wizard-ul insusi)
addons/                 <- sursa necompresata a fiecarui addon (pentru editari viitoare)
userdata/                <- guisettings/sources/addon_data necompresate (referinta)
userdata-backup.zip      <- ce descarca wizard-ul cand bifezi "setarile mele personale"
build/                   <- sursa wizard-ului (script.aco730restore)
```

## Actualizare dupa modificari viitoare

Dupa orice schimbare (main.py DigiOnline, Home.xml skin, credentiale noi etc.):
1. Bump versiune in `addon.xml`-ul respectiv daca s-a schimbat codul.
2. Cere-i lui Claude sa refaca zip-urile + `addons.xml`/md5 (pasii din aceasta
   sesiune) si sa reconstruiasca `userdata-backup.zip` daca s-au schimbat setari.
3. `git add -A && git commit -m "..." && git push`.

Data urmatoare cand rulezi wizard-ul pe orice device, ia automat versiunea noua
(fara sa reinstalezi wizard-ul insusi, doar daca s-a schimbat el).
