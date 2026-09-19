# Ryu Phoenix — Portfolio Site

A personal portfolio website for ryuphoenix.com, built with plain HTML, CSS, and JavaScript (no build step required).

## Structure

- `index.html` — page markup (Home, About, Skills, Projects, Contact)
- `css/style.css` — styling, including a light/dark theme
- `js/script.js` — mobile nav toggle, theme toggle, and contact form handling

## Running locally

Just open `index.html` in a browser, or serve the folder with any static file server, e.g.:

```
python3 -m http.server 8000
```

## Customizing

- Replace the placeholder name, tagline, and "About" facts in `index.html`.
- Fill in real skills and project details in the Skills and Projects sections.
- Update the social links in the footer.
- The contact form currently only shows a confirmation message client-side; wire it up to a real backend or form service (e.g. Formspree) to receive submissions.
