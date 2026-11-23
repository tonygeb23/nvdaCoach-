# NVDA Coach 1.7.0: draft translations of the two new chapters

Version 1.7.0 adds two chapters:

- `addon_store.json`, "Add-ons and the Add-on Store": 11 lessons, 48 steps.
- `braille.json`, "Using a Braille Display": 8 lessons, 34 steps. Optional; it
  does not count toward the certificate.

Both have been drafted in all eight other languages so that no student is left
without them. **These drafts are machine-assisted and have not been read by a
native speaker.** They need your review before they can be called finished. If
you would rather translate from the English yourself, do that and replace the
draft; the English files are the source of truth.

## How the drafts were made

- Every menu item, tab, button, action, status and setting name was taken from
  NVDA 2026.3.1's own translation for your language, not invented.
- Shortcut letters were taken from the same place. Where NVDA's translation
  gives a control no access key, or gives two controls the same letter, the
  lesson teaches Tab instead of an Alt shortcut.
- The names of the 25 add-ons are the names the Add-on Store shows in your
  language. Where that differs from the English name, the English name is
  given once as well.
- Style, key names and vocabulary follow your own six existing chapters.
- Nothing was tested in a running NVDA in your language.

## Rules for the files

- Do not change `id`, `order`, `type`, or `chapterComplete`.
- `"optional": true` in `braille.json` must stay exactly that: a real `true`,
  not a translated word and not a string in quotes.
- Keep the same number of lessons and steps as English, and exactly three
  hints in each step.
- `practiceText` must keep the same number of lines.
- Save as UTF-8 without a byte order mark.

Files for your language:

- `globalPlugins/nvdaCoach/lessons/[lang]/addon_store.json`
- `globalPlugins/nvdaCoach/lessons/[lang]/braille.json`
- `doc/[lang]/readme.html` (two new chapter sections, 7 and 8)
- `locale/[lang]/LC_MESSAGES/nvda.po` (new or reworded interface strings;
  entries carried over from your earlier wording are marked with a comment)

Also see `FACTUAL-CORRECTIONS-1.7.0.md`: twenty factual corrections were made
to the six original chapters in English only. Your six chapters still carry
the old statements until you update them.

---

## Spanish (es)

Check first:

1. **Opciones or Configuración.** NVDA's Spanish menu is Preferencias, then
   Opciones, so the new chapters teach "P, luego O" and say "Opciones de
   NVDA". Chapters 1 and 6 say "C de Configuración", which does not match NVDA.
2. **User Guide letter.** NVDA has "Guía del Usuario" on G; chapter 1 says U.
3. **Opening the store.** Tools is H, and the Tools menu has two items on C,
   so the lesson says press C, then Enter if the store does not open by itself.
4. **Access keys in the store.** Search is Alt+B. The add-on list has a
   different letter on each tab: Alt+L installed, Alt+D available, Alt+A
   updatable, Alt+I incompatible. Alt+A may collide with the Actualizar actions.
5. **Braille abbreviations** are taught as NVDA's catalogue gives them (bt, cv,
   ce, cc, bto, enl, enlv, dlg, en2; fl for read-only). The Spanish User Guide
   table still prints some English ones.
6. "pantalla braille" is NVDA's term; "también llamada línea braille" was added
   once. "sensores de enrutamiento" for routing keys.
7. Braille tables hint names "Español grado 1", "Español grado 2" and
   "Español computerizado de 8 puntos", reached with E and then the arrows.
8. Search examples use "reloj", the store's name for Clock.
9. Lessons say "computadora" and "laptop" like the earlier chapters, while
   quoted NVDA strings are Spain Spanish.
10. Not confirmed: the old name of Text wrap ("Ajuste de línea"), and the
    Windows strings "No guardar" and "Bluetooth y dispositivos".

## Japanese (ja)

Check first:

1. **Japanese braille tables** (braille_tables steps 1 and 2). NVDA lists only
   日本語漢点字 and 日本語6点漢字 under Japanese. The lesson names those two
   and 統一英語点字1級/2級 and does not say which a Japanese reader should
   choose. Please correct this with what readers actually use.
2. **Abbreviations lesson.** NVDA's Japanese catalogue shows full words
   (ボタン, チェックボックス, 編集可能, 見出しレベル 2, 展開, 折りたたみ)
   rather than abbreviations, so the lesson was rewritten to teach those and
   retitled コントロールの種類と状態の点字表示. The Japanese User Guide still
   lists English abbreviations. Please confirm on a real display.
3. タッチカーソル for routing keys (NVDA's term), introduced once as
   カーソルルーティングキー. マス for cell.
4. The NVDA key is written NVDAキー+ as in your existing chapters.
5. First-letter navigation in lists was replaced with arrow keys.
6. One sentence was added that is not in the English: add-on descriptions are
   mostly in English, so English search words work better.
7. The reading practice text talks about checking the spelling of English
   words, since kana braille does not show kanji.
8. アドオン ストア is written with a space, as in NVDA's menu; the warning
   dialog and User Guide section have no space, so both spellings appear.
9. Tethering uses NVDA's label 点字表示切り替え; speech mode "talk" is 声.
10. Not confirmed: Windows strings 保存しない and Bluetooth とデバイス.

## Polish (pl)

Check first:

1. **"Selected" shows as C H K**, the same letters as checkbox, in NVDA's
   Polish translation. The lesson teaches it as NVDA shows it; it may be a
   mistake in NVDA. Please confirm on a real display.
2. **Access keys.** Tools is N, Add-on Store A, Preferences O, Settings U,
   Help C, User Guide U. The add-on list is Alt+A on Zainstalowane and Alt+R on
   Odkrywaj dodatki. Other details is Alt+W. "Zainstaluj z pliku" has no access
   key, so the lesson uses Tab.
3. "przytrzymaj lewy Alt" was added, because right Alt types Polish letters.
4. "Klawisze przywoływania kursora, nazywane też klawiszami routing" for
   routing keys. "Integrał" and "brajl ze skrótami" for grade 1 and grade 2.
5. Braille tables hint names "Polski brajl literacki" and "Polski brajl
   komputerowy".
6. "Tryb przeglądania" follows your chapters, but NVDA's settings category is
   "Tryb czytania".
7. The status "Pobrany, oczekuje na instalacje" is NVDA's own spelling, kept
   because it is what the student hears.
8. The gloss "czyli sklep z dodatkami" was added once for Add-on Store.
9. Search examples were reduced to "zegar" and "OCR".
10. Your `getting_started.json` says press H for Help; NVDA's letter is C.

## Brazilian Portuguese (pt_BR)

Check first:

1. **Alt+C for the add-on list** collides with the Fechar button, which has
   the same letter. The lesson teaches Alt+C and says to press it again if you
   hear Fechar. That behaviour was assumed, not tested.
2. **Search has no access key** in pt_BR, so every "Alt+S" became Shift+Tab
   from the list.
3. Letters: Tools F, Add-on Store A, Settings Ç, Help J, User Guide U; sort is
   Alt+D; channel Alt+N, other details Alt+O and install from external source
   Alt+X are as in English.
4. "Linha braille" (NVDA's term for the device) appears close to "linha de
   texto" in the reading lesson. Please check it stays clear.
5. "Teclas de direcionamento do cursor", with "teclas de roteamento" once.
6. "Braille integral" and "braille abreviado" alongside NVDA's grau 1 and
   grau 2. Tables named "Português, grau 1" and "Português, grau 2".
7. Abbreviations as NVDA shows them: bt, cxs, edç, cxc, btopç, lnk, lnkv, lst,
   mnu, itmnu, dlg, t2. The User Guide table prints "edt" where the catalogue
   has "edç".
8. Speech modes as NVDA says them: fala, sob demanda, desligada, bipes.
9. Search examples are "área de transferência" and "relógio".
10. Not confirmed: the Windows strings "Bluetooth e dispositivos" and
    "Não salvar".

## Russian (ru)

Check first:

1. **Cyrillic access keys.** Menu: Р Инструменты, Д Магазин дополнений, П, Н,
   С Справка, Р Руководство пользователя. Store: Alt+Д list, Alt+П search,
   Alt+Р other details, Alt+К channel, Alt+Л sort, Alt+У install from external
   source. Each is given with a note that it needs the Russian keyboard layout,
   and with an arrow or Tab route as well. Your chapter 1 says H and G for Help
   and User Guide.
2. **Braille abbreviations** are taught as Cyrillic letters (кнп, флж, ред,
   комсп, ркнп, слк, псщслк, сп, мн, пнктмн, длг, з2). The practice text shows
   the right cells only with a Russian output table.
3. Control names follow what NVDA speaks ("комбинированный список",
   "редактор"); your chapters say "поле со списком" and "поле ввода".
4. "Просмотровый курсор" and "объект навигатора" are NVDA's terms; chapter 5
   once says "курсор рецензии".
5. "Перезапустить NVDA" in prose, NVDA's own "Перезагрузить" where quoted.
6. Braille terms: клавиши маршрутизации, ячейка, привязка брайля.
7. Tables named "Русский литературный брайль" and the variant with capital
   indication. NVDA also lists "Русский сокращённый брайль"; the lesson
   mentions it without claiming it is widely used.
8. The tab "Updatable add-ons" is "Обновления дополнений", and the
   enabled/disabled filter is labelled "Состояние".
9. Search examples: часы, буфер обмена, распознавание, громкость.
10. Not confirmed: the checked and unchecked checkbox signs in braille (the
    Russian User Guide shows "(x)" and "( )"), and the Windows strings.

## Turkish (tr)

Check first:

1. **The access-key step** (store layout, step 4) was rewritten the most.
   Tools then Add-on Store is R then M; Preferences then Settings is T then L;
   Help then User Guide is A then K. Search is Alt+A and sort is Alt+S. The
   list is Alt+M on the available tab only. Channel shares K with Close, and
   other details shares D with install from external source, so those are
   taught with Tab.
2. The available tab is announced as "Mağazadaki eklentiler" while its list
   label is "Mevcut eklentiler". The lesson uses the tab name.
3. **ObjPad** appears in the Turkish store as "Nesne Dolaşımı", the same as
   the chapter 5 title. Please check that sentence reads clearly.
4. Abbreviations as NVDA shows them: dğm, ok, yza, sk, sd, lnk, zbln, lst,
   mnü, mnüöğe, ik, b2, seç, so. They are spelled out letter by letter; please
   check they sound clear on a Turkish synthesizer.
5. Tables named "Türkçe derece1" (NVDA's own spelling) and "Türkçe derece 2".
6. Control names follow what NVDA speaks ("seçim kutusu", "yazı alanı"); your
   chapters say "açılır kutu" and "düzenleme alanı".
7. "Kullanıcı Rehberi" is NVDA's menu name; your chapters also use "Kullanım
   Kılavuzu".
8. The tether explanation: NVDA's label is "Braille taşınsın".
9. Search examples are "pano" and "saat".
10. Not confirmed: "güvenli kip" for secure mode, and the Windows strings.

## Simplified Chinese (zh_CN)

Check first:

1. **选项 or 首选项.** NVDA shows 选项(P); the six existing chapters say
   首选项. The new chapters use NVDA's word, so they differ from the old ones.
2. **Chinese braille** (braille_tables). The lesson says only that Chinese
   braille is written by sound and names 中文中国汉语通用盲文, 现行盲文 and
   双拼盲文. Please correct it with what readers actually use. It makes no
   claim that Chinese braille can be typed.
3. 开发板 is NVDA's spelling of the Dev channel and was copied exactly.
4. 方 for a braille cell, introduced as 也叫盲文单元. 光标定位键 for routing
   keys.
5. 路标 is NVDA's word for landmark; chapter 4 says 地标.
6. Braille abbreviations stay in English letters in NVDA's Chinese, so the
   lesson teaches btn, chk, edt and says so. Column and row follow the
   catalogue ("列", "行"); the User Guide still says C1 and R1.
7. First-letter navigation in the settings list and table list was replaced
   with arrow keys.
8. Statuses and actions use NVDA's wording, which differs in meaning from
   English in places (已下载，关闭商店时安装; 已删除，重启后生效; 更新日志).
9. Automatic updates: the setting and one option are both called 自动更新.
10. Search examples are 剪贴板 and 时钟.

## Traditional Chinese (zh_TW)

Check first:

1. **功能表 or 選單.** The new chapters use NVDA's 功能表. Your
   `nvda_settings.json` and readme say 選單.
2. **Taiwan braille** (braille_tables). The lesson says only that Taiwan's
   Chinese braille is based on Zhuyin, that NVDA's table is 中文 (台灣) 注音,
   and names 英文統一一級 and 二級. Please correct it as needed.
3. Because Zhuyin braille shows sound and not characters, "check spelling by
   touch" was worded as English spelling, and the Notepad exercise says to type
   an English sentence.
4. Braille vocabulary from NVDA: 點顯器, 方, 游標定位鍵, 摸讀, 轉譯表.
5. 跟隨遊標 is NVDA's spelling of that mode name; 游標 is used elsewhere.
6. Abbreviations stay in English in NVDA's zh_TW; the lesson says they come
   from English.
7. 便捷鍵 for access key is NVDA's word.
8. 捲動時中斷語音 and 顯示訊息 are drop-down lists, so the hints say to
   choose 停用 or 持續顯示.
9. "optional" in the lesson picker is 選修.
10. The new files are indented with two spaces; your six chapters use tabs.
