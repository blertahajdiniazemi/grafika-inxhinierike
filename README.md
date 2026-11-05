# Detyrat seminarike – hap pas hapi

Static site: no server, no build server. Open `index.html` or publish the folder as it is
(GitHub Pages, Netlify Drop or any web server).

* `tasks.json` – the catalogue (courses, exercises, 57 tasks, theory chapters)
* `templates/` – page templates; `style.css` – the one stylesheet
* `build.py` – writes every page from the catalogue: `python3 build.py`
* `animacione/` – the 28 step-by-step animations (self-contained HTML files)
* `libri/` – book pages (JPEG), task figures and the I.3 construction sheets
* `shkarkime/` – the two books as PDF

To add an animation later: copy the file into `animacione/`, set `"animation": "<file>"`
and `"steps": <n>` on the task in `tasks.json`, run `python3 build.py`, publish again.
