# Reguli pentru proiectul Kristinei Maia

## Programele de pe site (regula Kristinei, 20 nov 2026)
- **Orice program nou pe care îl facem pe site are alegerea limbii**, la fel ca Level Up: întrebarea „Your program language” la începutul quiz-ului (alege automat limba telefonului, dacă e una dintre ele) și meniul „Limba” în pagina programului.
- Limbile: engleză, română, spaniolă, germană, franceză, turcă. Se traduc interfața, numele exercițiilor, instrucțiunile, dozele, titlurile și notele antrenamentelor.
- Cum e făcut la Level Up: `website/program_i18n.py` (interfață, titluri, nume), `website/program_i18n_cues.py` (instrucțiuni), `website/program_template.html` (funcțiile `T`, `TD`, `TW`, atributul `data-t`), `website/build_program.py` (verifică și afișează „FĂRĂ TRADUCERE” dacă lipsește ceva).
- Antrenamentele clienților sunt **doar pe site**; Payhip e doar pentru plată și videourile de bun venit.
- Clipurile din program și din reel-uri: **doar originalele la rezoluție mare** (1080 × 1920), fără text vechi pe ele.
