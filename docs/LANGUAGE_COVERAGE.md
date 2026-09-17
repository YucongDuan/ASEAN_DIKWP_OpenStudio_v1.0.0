# Language coverage / 多语支持

| Code | Language | Main navigation, common controls, core terms | Full 12 lesson bodies, examples and self-checks |
|---|---|---|---|
| zh | 简体中文 | Included | Included |
| en | English | Included | Included |
| vi | Tiếng Việt | Included | Included |
| id | Bahasa Indonesia | Included | English reading fallback |
| ms | Bahasa Melayu | Included | English reading fallback |
| pt | Português | Included | English reading fallback |
| fil | Filipino | Included | English reading fallback |
| th | ไทย | Included | English reading fallback |
| km | ខ្មែរ | Included | English reading fallback |
| lo | ລາວ | Included | English reading fallback |
| my | မြန်မာ | Included | English reading fallback |
| ta | தமிழ் | Included | English reading fallback |
| tet | Tetun | Included | English reading fallback |

There are 79 shared values per locale, including labels, language name and introductory copy. Extended interface explanations are Chinese/English, with the complete Vietnamese lesson text available through the independent reading selector. The query dictionary maps language variants to shared concept IDs; this is keyword/concept matching, not an unrestricted machine translation or large-model service.

Original book titles, paper records, repository descriptions, report notes and evidence records retain their original language. The 128-page lecture corpus has not been represented as thirteen fully translated versions. Initial translations are AI-assisted teaching drafts; native-language specialist review remains valuable, especially for terminology with multiple accepted translations.

To add a locale, follow the exact key set in `data/locales.json`; add concept synonyms to `data/concepts.json`. To add deep lesson coverage, add the locale to every content field, quiz options and explanation in `data/lessons.json`, and expose it in the reading selector in `web/app.js`. Regenerate with `python scripts/build_web.py`.

The application loads no font files and sends no text to a translation service. Rendering uses the learner's system fonts; scripts such as Khmer, Lao, Myanmar and Tamil require suitable fonts installed in that environment.
